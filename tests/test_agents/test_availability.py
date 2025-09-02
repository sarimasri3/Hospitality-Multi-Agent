"""
Unit tests for the Availability Agent and Ranking Engine.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.availability.ranking import PropertyRanker


class TestPropertyRanker:
    """Test the property ranking engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ranker = PropertyRanker()
        
        # Sample properties for testing
        self.properties = [
            {
                "property_id": "prop1",
                "name": "Luxury Beach Villa",
                "minimum_price": 200,
                "guest_space": 6,
                "location": {"city": "Miami", "lat": 25.7617, "lng": -80.1918},
                "amenities": ["pool", "wifi", "parking", "beach_access"],
                "property_type": "villa",
                "created_at": datetime.now().isoformat()
            },
            {
                "property_id": "prop2",
                "name": "Downtown Apartment",
                "minimum_price": 150,
                "guest_space": 4,
                "location": {"city": "Miami", "lat": 25.7749, "lng": -80.1937},
                "amenities": ["wifi", "parking", "gym"],
                "property_type": "apartment",
                "created_at": datetime.now().isoformat()
            },
            {
                "property_id": "prop3",
                "name": "Budget Studio",
                "minimum_price": 80,
                "guest_space": 2,
                "location": {"city": "Miami", "lat": 25.7589, "lng": -80.1965},
                "amenities": ["wifi"],
                "property_type": "studio",
                "created_at": datetime.now().isoformat()
            }
        ]
    
    def test_rank_properties_by_price(self):
        """Test ranking properties by price."""
        search_criteria = {
            "max_price": 250,
            "number_of_guests": 2
        }
        user_preferences = {}
        
        ranked = self.ranker.rank_properties(
            self.properties,
            user_preferences,
            search_criteria
        )
        
        # Should return list of tuples
        assert len(ranked) > 0
        assert len(ranked[0]) == 3  # (property, score, reasons)
        
        # Check that properties are ranked
        scores = [score for _, score, _ in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_rank_properties_by_capacity(self):
        """Test ranking by capacity fit."""
        search_criteria = {
            "number_of_guests": 4,
            "max_price": 500
        }
        user_preferences = {}
        
        ranked = self.ranker.rank_properties(
            self.properties,
            user_preferences,
            search_criteria
        )
        
        # Property with capacity 4 should rank well
        top_property = ranked[0][0]
        assert top_property["guest_space"] >= 4
    
    def test_rank_properties_by_amenities(self):
        """Test ranking by amenity matching."""
        search_criteria = {
            "number_of_guests": 2,
            "max_price": 500
        }
        user_preferences = {
            "amenities": ["pool", "beach_access", "wifi"]
        }
        
        ranked = self.ranker.rank_properties(
            self.properties,
            user_preferences,
            search_criteria
        )
        
        # Property with most matching amenities should rank higher
        top_property = ranked[0][0]
        top_amenities = set(top_property["amenities"])
        requested = set(user_preferences["amenities"])
        
        # Check that top property has good amenity match
        assert len(top_amenities & requested) > 0
    
    def test_format_recommendations(self):
        """Test recommendation formatting."""
        search_criteria = {
            "number_of_guests": 4,
            "max_price": 300
        }
        user_preferences = {}
        
        ranked = self.ranker.rank_properties(
            self.properties,
            user_preferences,
            search_criteria
        )
        
        formatted = self.ranker.format_recommendations(ranked, max_results=2)
        
        # Check formatting
        assert isinstance(formatted, str)
        assert "1." in formatted
        assert "$" in formatted  # Price should be included
        assert "Miami" in formatted  # Location should be included
    
    def test_distance_calculation(self):
        """Test distance calculation between locations."""
        loc1 = {"lat": 25.7617, "lng": -80.1918}
        loc2 = {"lat": 25.7749, "lng": -80.1937}
        
        distance = self.ranker._calculate_distance(loc1, loc2)
        
        # Distance should be positive and reasonable (< 10km for these coords)
        assert distance > 0
        assert distance < 10
    
    def test_custom_weights(self):
        """Test ranker with custom weights."""
        custom_weights = {
            "price": 0.5,  # Heavily weight price
            "distance": 0.1,
            "capacity_fit": 0.2,
            "amenity_match": 0.1,
            "recency": 0.1
        }
        
        ranker = PropertyRanker(weights=custom_weights)
        
        search_criteria = {
            "max_price": 100,  # Low budget
            "number_of_guests": 2
        }
        user_preferences = {}
        
        ranked = ranker.rank_properties(
            self.properties,
            user_preferences,
            search_criteria
        )
        
        # With heavy price weight, cheapest should rank high
        top_property = ranked[0][0]
        assert top_property["minimum_price"] == 80  # Budget Studio