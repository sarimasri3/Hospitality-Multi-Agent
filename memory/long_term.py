"""
Long-term memory management for user profiles and preferences.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class LongTermMemory:
    """
    Manages long-term memory for user profiles and preferences.
    In production, this would integrate with Firestore.
    """
    
    def __init__(self):
        """Initialize LTM storage."""
        # In production, this would connect to Firestore
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._preferences: Dict[str, Dict[str, Any]] = {}
        self._booking_history: Dict[str, List[Dict]] = {}
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile.
        
        Args:
            user_id: User identifier
        
        Returns:
            User profile or None if not found
        """
        return self._profiles.get(user_id)
    
    async def update_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> bool:
        """
        Update user profile.
        
        Args:
            user_id: User identifier
            profile_data: Profile updates
        
        Returns:
            True if updated
        """
        if user_id not in self._profiles:
            self._profiles[user_id] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
        
        self._profiles[user_id].update(profile_data)
        self._profiles[user_id]["updated_at"] = datetime.now().isoformat()
        
        return True
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences based on booking history.
        
        Args:
            user_id: User identifier
        
        Returns:
            User preferences dictionary
        """
        if user_id not in self._preferences:
            return {
                "preferred_cities": [],
                "average_budget": None,
                "typical_guests": None,
                "favorite_amenities": [],
                "preferred_property_types": [],
                "typical_stay_length": None,
                "frequently_selected_addons": []
            }
        
        return self._preferences[user_id]
    
    async def update_user_preferences(
        self,
        user_id: str,
        booking_data: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences based on new booking.
        
        Args:
            user_id: User identifier
            booking_data: Booking information
        
        Returns:
            True if updated
        """
        if user_id not in self._preferences:
            self._preferences[user_id] = {
                "preferred_cities": [],
                "budgets": [],
                "guest_counts": [],
                "amenities": [],
                "property_types": [],
                "stay_lengths": [],
                "addons": []
            }
        
        prefs = self._preferences[user_id]
        
        # Update preferences with new booking data
        if 'city' in booking_data:
            if booking_data['city'] not in prefs['preferred_cities']:
                prefs['preferred_cities'].append(booking_data['city'])
        
        if 'max_price' in booking_data:
            prefs['budgets'].append(booking_data['max_price'])
            prefs['average_budget'] = sum(prefs['budgets']) / len(prefs['budgets'])
        
        if 'number_of_guests' in booking_data:
            prefs['guest_counts'].append(booking_data['number_of_guests'])
            prefs['typical_guests'] = max(set(prefs['guest_counts']), key=prefs['guest_counts'].count)
        
        if 'amenities' in booking_data:
            prefs['amenities'].extend(booking_data['amenities'])
            # Find most common amenities
            amenity_counts = {}
            for amenity in prefs['amenities']:
                amenity_counts[amenity] = amenity_counts.get(amenity, 0) + 1
            prefs['favorite_amenities'] = sorted(
                amenity_counts.keys(),
                key=lambda x: amenity_counts[x],
                reverse=True
            )[:5]
        
        if 'add_ons' in booking_data:
            prefs['addons'].extend(booking_data['add_ons'])
            # Find frequently selected add-ons
            addon_counts = {}
            for addon in prefs['addons']:
                addon_counts[addon] = addon_counts.get(addon, 0) + 1
            prefs['frequently_selected_addons'] = [
                addon for addon, count in addon_counts.items() if count >= 2
            ]
        
        prefs['updated_at'] = datetime.now().isoformat()
        
        return True
    
    async def add_booking_to_history(
        self,
        user_id: str,
        booking: Dict[str, Any]
    ) -> bool:
        """
        Add a booking to user's history.
        
        Args:
            user_id: User identifier
            booking: Booking data
        
        Returns:
            True if added
        """
        if user_id not in self._booking_history:
            self._booking_history[user_id] = []
        
        self._booking_history[user_id].append({
            **booking,
            "added_to_history": datetime.now().isoformat()
        })
        
        # Keep only last 50 bookings
        if len(self._booking_history[user_id]) > 50:
            self._booking_history[user_id] = self._booking_history[user_id][-50:]
        
        # Update preferences based on booking
        await self.update_user_preferences(user_id, booking)
        
        return True
    
    async def get_booking_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user's booking history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of bookings to return
        
        Returns:
            List of bookings
        """
        if user_id not in self._booking_history:
            return []
        
        history = self._booking_history[user_id]
        return history[-limit:] if len(history) > limit else history
    
    async def get_personalization_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalization context for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Personalization context
        """
        preferences = await self.get_user_preferences(user_id)
        history = await self.get_booking_history(user_id, limit=5)
        
        # Calculate insights
        insights = {
            "is_repeat_customer": len(history) > 0,
            "booking_count": len(self._booking_history.get(user_id, [])),
            "favorite_city": preferences['preferred_cities'][0] if preferences['preferred_cities'] else None,
            "average_budget": preferences.get('average_budget'),
            "typical_party_size": preferences.get('typical_guests'),
            "prefers_addons": len(preferences.get('frequently_selected_addons', [])) > 0
        }
        
        return {
            "preferences": preferences,
            "recent_bookings": history,
            "insights": insights
        }