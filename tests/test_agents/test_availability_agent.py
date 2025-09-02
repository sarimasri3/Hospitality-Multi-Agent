"""
Tests for the Availability Agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.availability.agent import (
    search_and_rank_properties, calculate_total_price,
    filter_by_amenities, get_alternative_suggestions
)
from agents.availability.ranking import PropertyRanker


class TestAvailabilityAgent:
    """Test cases for Availability Agent functions."""
    
    @pytest.mark.asyncio
    async def test_search_and_rank_properties(self):
        """Test property search and ranking function."""
        result = await search_and_rank_properties(
            city="Miami",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=4,
            max_price=500.0
        )
        
        assert result['success'] is True
        assert 'properties' in result
        assert 'recommendations' in result
    
    @pytest.mark.asyncio
    async def test_calculate_total_price_basic(self):
        """Test basic price calculation."""
        result = await calculate_total_price(
            base_price=200.0,
            nights=3
        )
        
        assert result['nights'] == 3
        assert result['price_per_night'] == 200.0
        assert result['subtotal'] == 600.0
        assert result['service_fee'] == 60.0  # 10%
        assert result['cleaning_fee'] == 50.0
        assert result['tax'] > 0
        assert result['total'] > result['subtotal']
    
    @pytest.mark.asyncio
    async def test_calculate_total_price_with_addons(self):
        """Test price calculation with add-ons."""
        result = await calculate_total_price(
            base_price=200.0,
            nights=3,
            add_ons=["early_checkin", "welcome_basket"]
        )
        
        assert result['add_ons_total'] == 125.0  # 50 + 75
        assert result['total'] > 600.0  # Should include add-ons
        assert result['breakdown']['Add-ons'] == "$125.00"
    
    @pytest.mark.asyncio
    async def test_calculate_total_price_custom_fees(self):
        """Test price calculation with custom fees."""
        result = await calculate_total_price(
            base_price=300.0,
            nights=2,
            service_fee_percentage=0.15,
            tax_percentage=0.10,
            cleaning_fee=75.0
        )
        
        assert result['service_fee'] == 90.0  # 15% of 600
        assert result['cleaning_fee'] == 75.0
        # Tax should be 10% of (600 + 90 + 75) = 76.5
        assert abs(result['tax'] - 76.5) < 0.01
    
    @pytest.mark.asyncio
    async def test_filter_by_amenities_no_filter(self):
        """Test amenity filtering with no required amenities."""
        properties = [
            {'name': 'Prop1', 'amenities': ['wifi', 'pool']},
            {'name': 'Prop2', 'amenities': ['wifi', 'gym']}
        ]
        
        result = await filter_by_amenities(properties, [])
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_filter_by_amenities_with_filter(self):
        """Test amenity filtering with required amenities."""
        properties = [
            {'name': 'Prop1', 'amenities': ['wifi', 'pool', 'parking']},
            {'name': 'Prop2', 'amenities': ['wifi', 'gym']},
            {'name': 'Prop3', 'amenities': ['wifi', 'pool']}
        ]
        
        result = await filter_by_amenities(properties, ['wifi', 'pool'])
        assert len(result) == 2
        assert result[0]['name'] == 'Prop1'
        assert result[1]['name'] == 'Prop3'
    
    @pytest.mark.asyncio
    async def test_filter_by_amenities_strict_filter(self):
        """Test strict amenity filtering."""
        properties = [
            {'name': 'Prop1', 'amenities': ['wifi']},
            {'name': 'Prop2', 'amenities': ['wifi', 'pool', 'gym', 'parking']}
        ]
        
        result = await filter_by_amenities(properties, ['wifi', 'pool', 'gym'])
        assert len(result) == 1
        assert result[0]['name'] == 'Prop2'
    
    @pytest.mark.asyncio
    async def test_get_alternative_suggestions_nearby_cities(self):
        """Test alternative suggestions for known cities."""
        result = await get_alternative_suggestions(
            city="Miami",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=4
        )
        
        assert 'suggestions' in result
        assert 'message' in result
        
        # Should suggest nearby cities for Miami
        nearby_suggestion = next((s for s in result['suggestions'] if s['type'] == 'nearby_locations'), None)
        assert nearby_suggestion is not None
        assert 'Fort Lauderdale' in nearby_suggestion['cities']
    
    @pytest.mark.asyncio
    async def test_get_alternative_suggestions_large_group(self):
        """Test alternative suggestions for large groups."""
        result = await get_alternative_suggestions(
            city="Paris",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=8
        )
        
        # Should suggest splitting booking for large groups
        split_suggestion = next((s for s in result['suggestions'] if s['type'] == 'split_booking'), None)
        assert split_suggestion is not None
        assert '8 guests' in split_suggestion['message']
    
    @pytest.mark.asyncio
    async def test_get_alternative_suggestions_unknown_city(self):
        """Test alternative suggestions for unknown city."""
        result = await get_alternative_suggestions(
            city="UnknownCity",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=2
        )
        
        # Should still provide date flexibility suggestion
        date_suggestion = next((s for s in result['suggestions'] if s['type'] == 'date_flexibility'), None)
        assert date_suggestion is not None


class TestPropertyRanker:
    """Test cases for PropertyRanker."""
    
    @pytest.fixture
    def ranker(self):
        """Create PropertyRanker instance."""
        return PropertyRanker()
    
    @pytest.fixture
    def sample_properties(self):
        """Sample properties for testing."""
        return [
            {
                'property_id': 'prop1',
                'name': 'Luxury Villa',
                'minimum_price': 400,
                'guest_space': 8,
                'location': {'city': 'Miami', 'lat': 25.7617, 'lng': -80.1918},
                'amenities': ['pool', 'wifi', 'parking'],
                'property_type': 'villa',
                'created_at': datetime.now().isoformat()
            },
            {
                'property_id': 'prop2',
                'name': 'Budget Apartment',
                'minimum_price': 150,
                'guest_space': 4,
                'location': {'city': 'Miami', 'lat': 25.7749, 'lng': -80.1937},
                'amenities': ['wifi'],
                'property_type': 'apartment',
                'created_at': datetime.now().isoformat()
            }
        ]
    
    def test_ranker_initialization(self, ranker):
        """Test ranker initializes with default weights."""
        assert ranker.weights['price'] == 0.3
        assert ranker.weights['distance'] == 0.2
        assert ranker.weights['capacity_fit'] == 0.2
        assert ranker.weights['amenity_match'] == 0.2
        assert ranker.weights['recency'] == 0.1
    
    def test_ranker_custom_weights(self):
        """Test ranker with custom weights."""
        custom_weights = {'price': 0.5, 'distance': 0.3, 'capacity_fit': 0.2}
        ranker = PropertyRanker(custom_weights)
        assert ranker.weights['price'] == 0.5
        assert ranker.weights['distance'] == 0.3
    
    def test_rank_properties_basic(self, ranker, sample_properties):
        """Test basic property ranking."""
        user_preferences = {}
        search_criteria = {'max_price': 500, 'number_of_guests': 4}
        
        ranked = ranker.rank_properties(sample_properties, user_preferences, search_criteria)
        
        assert len(ranked) == 2
        assert all(len(item) == 3 for item in ranked)  # (property, score, reasons)
        
        # Budget apartment should rank higher due to better price
        assert ranked[0][0]['name'] == 'Budget Apartment'
    
    def test_rank_properties_with_preferences(self, ranker, sample_properties):
        """Test property ranking with user preferences."""
        user_preferences = {
            'amenities': ['pool', 'wifi'],
            'preferred_type': 'villa'
        }
        search_criteria = {'max_price': 500, 'number_of_guests': 6}
        
        ranked = ranker.rank_properties(sample_properties, user_preferences, search_criteria)
        
        # Luxury villa should rank higher due to amenity match and type preference
        assert ranked[0][0]['name'] == 'Luxury Villa'
        assert any('pool' in reason for reason in ranked[0][2])
    
    def test_score_price_within_budget(self, ranker):
        """Test price scoring within budget."""
        prop = {'minimum_price': 300}
        criteria = {'max_price': 500}
        
        score, reason = ranker._score_price(prop, criteria)
        
        assert score > 0
        assert reason is not None
        assert '$300' in reason
    
    def test_score_price_over_budget(self, ranker):
        """Test price scoring over budget."""
        prop = {'minimum_price': 600}
        criteria = {'max_price': 500}
        
        score, reason = ranker._score_price(prop, criteria)
        
        assert score < 0
        assert reason is None
    
    def test_score_price_no_budget(self, ranker):
        """Test price scoring with no budget specified."""
        prop = {'minimum_price': 300}
        criteria = {}
        
        score, reason = ranker._score_price(prop, criteria)
        
        assert score == 0
        assert reason is None
    
    def test_score_capacity_perfect_fit(self, ranker):
        """Test capacity scoring with perfect fit."""
        prop = {'guest_space': 4}
        criteria = {'number_of_guests': 4}
        
        score, reason = ranker._score_capacity(prop, criteria)
        
        assert score == ranker.weights['capacity_fit']
        assert 'Perfect size' in reason
    
    def test_score_capacity_insufficient(self, ranker):
        """Test capacity scoring with insufficient space."""
        prop = {'guest_space': 2}
        criteria = {'number_of_guests': 4}
        
        score, reason = ranker._score_capacity(prop, criteria)
        
        assert score == -1.0
        assert reason is None
    
    def test_score_amenities_full_match(self, ranker):
        """Test amenity scoring with full match."""
        prop = {'amenities': ['wifi', 'pool', 'parking', 'gym']}
        preferences = {'amenities': ['wifi', 'pool']}
        
        score, reason = ranker._score_amenities(prop, preferences)
        
        assert score == ranker.weights['amenity_match']
        assert 'wifi' in reason and 'pool' in reason
    
    def test_score_amenities_partial_match(self, ranker):
        """Test amenity scoring with partial match."""
        prop = {'amenities': ['wifi']}
        preferences = {'amenities': ['wifi', 'pool']}
        
        score, reason = ranker._score_amenities(prop, preferences)
        
        assert 0 < score < ranker.weights['amenity_match']
        assert '1 of your requested' in reason
    
    def test_score_amenities_no_preferences(self, ranker):
        """Test amenity scoring with no preferences."""
        prop = {'amenities': ['wifi', 'pool']}
        preferences = {}
        
        score, reason = ranker._score_amenities(prop, preferences)
        
        assert score == 0
        assert reason is None
    
    def test_calculate_distance(self, ranker):
        """Test distance calculation."""
        loc1 = {'lat': 25.7617, 'lng': -80.1918}  # Miami
        loc2 = {'lat': 25.7749, 'lng': -80.1937}  # Nearby Miami
        
        distance = ranker._calculate_distance(loc1, loc2)
        
        assert distance > 0
        assert distance < 10  # Should be close
    
    def test_format_recommendations_empty(self, ranker):
        """Test formatting empty recommendations."""
        result = ranker.format_recommendations([])
        assert "No properties found" in result
    
    def test_format_recommendations_with_data(self, ranker, sample_properties):
        """Test formatting recommendations with data."""
        ranked = [(sample_properties[0], 0.8, ['Great value', 'Perfect size'])]
        
        result = ranker.format_recommendations(ranked, max_results=1)
        
        assert 'Luxury Villa' in result
        assert '$400/night' in result
        assert 'Great value' in result
        assert 'Perfect size' in result


if __name__ == "__main__":
    pytest.main([__file__])
