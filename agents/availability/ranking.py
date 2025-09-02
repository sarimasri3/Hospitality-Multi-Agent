"""
Property ranking engine with explainable scoring.
"""

from typing import List, Dict, Tuple, Optional, Any
import math
from datetime import datetime


class PropertyRanker:
    """Explainable property ranking with configurable weights."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the ranker with scoring weights.
        
        Args:
            weights: Optional custom weights for scoring factors
        """
        self.weights = weights or {
            "price": 0.3,
            "distance": 0.2,
            "capacity_fit": 0.2,
            "amenity_match": 0.2,
            "recency": 0.1
        }
    
    def rank_properties(
        self,
        properties: List[Dict],
        user_preferences: Dict[str, Any],
        search_criteria: Dict[str, Any]
    ) -> List[Tuple[Dict, float, List[str]]]:
        """
        Rank properties and return top results with scores and reasons.
        
        Args:
            properties: List of property dictionaries
            user_preferences: User preference data
            search_criteria: Search criteria including budget, guests, etc.
        
        Returns:
            List of (property, score, reason_codes) tuples
        """
        scored_properties = []
        
        for prop in properties:
            score = 0
            reasons = []
            
            # Price scoring (lower is better relative to budget)
            score_delta, reason = self._score_price(prop, search_criteria)
            score += score_delta
            if reason:
                reasons.append(reason)
            
            # Distance scoring (if location preference exists)
            if 'preferred_location' in user_preferences:
                score_delta, reason = self._score_distance(prop, user_preferences)
                score += score_delta
                if reason:
                    reasons.append(reason)
            
            # Capacity fit scoring
            score_delta, reason = self._score_capacity(prop, search_criteria)
            score += score_delta
            if reason:
                reasons.append(reason)
            
            # Amenity matching scoring
            score_delta, reason = self._score_amenities(prop, user_preferences)
            score += score_delta
            if reason:
                reasons.append(reason)
            
            # Recency scoring (newer listings get slight boost)
            score_delta, reason = self._score_recency(prop)
            score += score_delta
            if reason:
                reasons.append(reason)
            
            # Add property type bonus
            if prop.get('property_type') == user_preferences.get('preferred_type'):
                score += 0.1
                reasons.append(f"Matches your preferred {prop['property_type']}")
            
            scored_properties.append((prop, score, reasons))
        
        # Sort by score descending
        scored_properties.sort(key=lambda x: x[1], reverse=True)
        
        # Return top properties (limit to 5)
        return scored_properties[:5]
    
    def _score_price(self, prop: Dict, criteria: Dict) -> Tuple[float, Optional[str]]:
        """Score based on price relative to budget."""
        price = prop.get('minimum_price', float('inf'))
        budget = criteria.get('max_price', float('inf'))
        
        if budget == float('inf'):
            # No budget specified, neutral scoring
            return 0, None
        
        price_ratio = price / budget
        
        if price_ratio <= 0.5:
            # Exceptional value
            score = self.weights['price']
            reason = f"Exceptional value at ${price:.0f}/night"
        elif price_ratio <= 0.75:
            # Great value
            score = self.weights['price'] * 0.8
            reason = f"Great value at ${price:.0f}/night"
        elif price_ratio <= 1.0:
            # Within budget
            score = self.weights['price'] * 0.5
            reason = f"Within budget at ${price:.0f}/night"
        else:
            # Over budget
            score = -self.weights['price'] * 0.5
            reason = None
        
        return score, reason
    
    def _score_distance(self, prop: Dict, preferences: Dict) -> Tuple[float, Optional[str]]:
        """Score based on distance from preferred location."""
        prop_location = prop.get('location', {})
        pref_location = preferences.get('preferred_location', {})
        
        if not pref_location or not prop_location:
            return 0, None
        
        distance = self._calculate_distance(prop_location, pref_location)
        
        if distance < 1:
            score = self.weights['distance']
            reason = "Walking distance to your preferred area"
        elif distance < 5:
            score = self.weights['distance'] * 0.8
            reason = f"Only {distance:.1f}km from your preferred area"
        elif distance < 10:
            score = self.weights['distance'] * 0.5
            reason = f"Close to preferred area ({distance:.1f}km)"
        else:
            score = 0
            reason = None
        
        return score, reason
    
    def _score_capacity(self, prop: Dict, criteria: Dict) -> Tuple[float, Optional[str]]:
        """Score based on capacity fit."""
        capacity = prop.get('guest_space', 0)
        needed = criteria.get('number_of_guests', 1)
        
        if capacity < needed:
            # Doesn't fit
            return -1.0, None
        
        extra_space = capacity - needed
        
        if extra_space == 0:
            # Perfect fit
            score = self.weights['capacity_fit']
            reason = f"Perfect size for {needed} guest{'s' if needed > 1 else ''}"
        elif extra_space <= 2:
            # Good fit with some extra space
            score = self.weights['capacity_fit'] * 0.8
            reason = f"Comfortable space for {needed} guest{'s' if needed > 1 else ''}"
        else:
            # Too much extra space
            score = self.weights['capacity_fit'] * 0.3
            reason = None
        
        return score, reason
    
    def _score_amenities(self, prop: Dict, preferences: Dict) -> Tuple[float, Optional[str]]:
        """Score based on amenity matching."""
        requested = set(preferences.get('amenities', []))
        available = set(prop.get('amenities', []))
        
        if not requested:
            return 0, None
        
        matched = requested & available
        match_ratio = len(matched) / len(requested)
        
        score = match_ratio * self.weights['amenity_match']
        
        if match_ratio >= 0.8:
            top_amenities = list(matched)[:3]
            reason = f"Has {', '.join(top_amenities)}"
        elif match_ratio >= 0.5:
            reason = f"Has {len(matched)} of your requested amenities"
        else:
            reason = None
        
        return score, reason
    
    def _score_recency(self, prop: Dict) -> Tuple[float, Optional[str]]:
        """Score based on listing recency."""
        created_at = prop.get('created_at')
        if not created_at:
            return 0, None
        
        # Calculate days since listing
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        days_old = (datetime.now() - created_at).days
        
        if days_old < 30:
            score = self.weights['recency']
            reason = "Recently listed property"
        elif days_old < 90:
            score = self.weights['recency'] * 0.5
            reason = None
        else:
            score = 0
            reason = None
        
        return score, reason
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """
        Calculate distance between two locations using Haversine formula.
        
        Args:
            loc1: First location with lat/lng
            loc2: Second location with lat/lng
        
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1 = math.radians(loc1.get('lat', 0))
        lat2 = math.radians(loc2.get('lat', 0))
        dlat = lat2 - lat1
        dlon = math.radians(loc2.get('lng', 0) - loc1.get('lng', 0))
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def format_recommendations(
        self,
        ranked_properties: List[Tuple[Dict, float, List[str]]],
        max_results: int = 3
    ) -> str:
        """
        Format ranked properties into a readable recommendation.
        
        Args:
            ranked_properties: List of ranked property tuples
            max_results: Maximum number of results to show
        
        Returns:
            Formatted recommendation string
        """
        if not ranked_properties:
            return "No properties found matching your criteria."
        
        recommendations = []
        for i, (prop, score, reasons) in enumerate(ranked_properties[:max_results], 1):
            rec = f"\n**{i}. {prop['name']}**\n"
            rec += f"   📍 {prop['location']['city']}\n"
            rec += f"   💰 ${prop['minimum_price']:.0f}/night\n"
            rec += f"   👥 Accommodates {prop['guest_space']} guests\n"
            
            if reasons:
                rec += "   ✨ " + " • ".join(reasons[:3]) + "\n"
            
            if prop.get('amenities'):
                top_amenities = prop['amenities'][:5]
                rec += f"   🏠 {', '.join(top_amenities)}\n"
            
            recommendations.append(rec)
        
        return "\n".join(recommendations)