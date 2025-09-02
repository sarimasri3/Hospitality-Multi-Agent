"""
Tests for the Firestore MCP Server.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_servers.firestore.server import (
    create_user, get_user, create_property, search_properties,
    create_booking, get_booking, update_booking_status_tool, get_user_bookings
)


class TestFirestoreServer:
    """Test cases for Firestore MCP Server functions."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock Firestore database."""
        with patch('mcp_servers.firestore.server.db') as mock_db:
            yield mock_db
    
    @pytest.mark.asyncio
    async def test_create_user_new(self, mock_db):
        """Test creating a new user."""
        # Mock Firestore operations
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_ref.id = "user_123"
        mock_collection.document.return_value = mock_doc_ref
        mock_collection.where.return_value.limit.return_value.get.return_value = []
        mock_db.collection.return_value = mock_collection
        
        result = await create_user(
            name="John Doe",
            email="john@example.com",
            role="guest",
            phone="+1234567890"
        )
        
        assert result['success'] is True
        assert result['user_id'] == "user_123"
        assert "created successfully" in result['message']
        
        # Verify Firestore calls
        mock_db.collection.assert_called_with('users')
        mock_doc_ref.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_existing_email(self, mock_db):
        """Test creating user with existing email."""
        # Mock existing user
        mock_collection = Mock()
        mock_existing_user = Mock()
        mock_collection.where.return_value.limit.return_value.get.return_value = [mock_existing_user]
        mock_db.collection.return_value = mock_collection
        
        result = await create_user(
            name="John Doe",
            email="existing@example.com"
        )
        
        assert result['success'] is False
        assert "already exists" in result['message']
    
    @pytest.mark.asyncio
    async def test_create_user_error_handling(self, mock_db):
        """Test user creation error handling."""
        mock_db.collection.side_effect = Exception("Database error")
        
        result = await create_user(
            name="John Doe",
            email="john@example.com"
        )
        
        assert result['success'] is False
        assert "Error creating user" in result['message']
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, mock_db):
        """Test getting user by ID."""
        # Mock user document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'uid': 'user_123',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        
        result = await get_user(user_id="user_123")
        
        assert result['success'] is True
        assert result['user']['name'] == 'John Doe'
        assert result['user']['email'] == 'john@example.com'
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, mock_db):
        """Test getting user by email."""
        # Mock user query result
        mock_user_doc = Mock()
        mock_user_doc.to_dict.return_value = {
            'uid': 'user_123',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        mock_collection = Mock()
        mock_collection.where.return_value.limit.return_value.get.return_value = [mock_user_doc]
        mock_db.collection.return_value = mock_collection
        
        result = await get_user(email="john@example.com")
        
        assert result['success'] is True
        assert result['user']['name'] == 'John Doe'
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, mock_db):
        """Test getting non-existent user."""
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        
        result = await get_user(user_id="nonexistent")
        
        assert result['success'] is False
        assert "not found" in result['message']
    
    @pytest.mark.asyncio
    async def test_create_property(self, mock_db):
        """Test creating a property."""
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_ref.id = "prop_123"
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        
        result = await create_property(
            user_id="host_123",
            name="Beach Villa",
            description="Beautiful beachfront villa",
            city="Miami",
            country="USA",
            address="123 Ocean Drive",
            lat=25.7617,
            lng=-80.1918,
            minimum_price=300.0,
            property_type="villa",
            guest_space=8,
            amenities=["pool", "wifi", "parking"]
        )
        
        assert result['success'] is True
        assert result['property_id'] == "prop_123"
        assert "created successfully" in result['message']
        
        # Verify property data structure
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args['name'] == "Beach Villa"
        assert call_args['location']['city'] == "Miami"
        assert call_args['minimum_price'] == 300.0
        assert call_args['guest_space'] == 8
        assert "pool" in call_args['amenities']
    
    @pytest.mark.asyncio
    async def test_create_property_with_weekend_pricing(self, mock_db):
        """Test property creation includes weekend pricing."""
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_ref.id = "prop_123"
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        
        await create_property(
            user_id="host_123",
            name="Beach Villa",
            description="Beautiful villa",
            city="Miami",
            country="USA",
            address="123 Ocean Drive",
            lat=25.7617,
            lng=-80.1918,
            minimum_price=300.0,
            property_type="villa",
            guest_space=8,
            amenities=["pool"]
        )
        
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args['prices']['weekday'] == 300.0
        assert call_args['prices']['weekend'] == 360.0  # 20% premium
    
    @pytest.mark.asyncio
    async def test_search_properties_basic(self, mock_db):
        """Test basic property search."""
        # Mock property documents
        mock_prop1 = Mock()
        mock_prop1.id = "prop_1"
        mock_prop1.to_dict.return_value = {
            'property_id': 'prop_1',
            'name': 'Villa 1',
            'location': {'city': 'Miami'},
            'guest_space': 6,
            'minimum_price': 250,
            'amenities': ['wifi', 'pool']
        }
        
        mock_prop2 = Mock()
        mock_prop2.id = "prop_2"
        mock_prop2.to_dict.return_value = {
            'property_id': 'prop_2',
            'name': 'Villa 2',
            'location': {'city': 'Miami'},
            'guest_space': 8,
            'minimum_price': 350,
            'amenities': ['wifi', 'gym']
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_prop1, mock_prop2]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        with patch('mcp_servers.firestore.server.check_booking_overlap', return_value=False):
            result = await search_properties(
                city="Miami",
                number_of_guests=4,
                max_price=400
            )
        
        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['properties']) == 2
        assert result['properties'][0]['name'] == 'Villa 1'
    
    @pytest.mark.asyncio
    async def test_search_properties_with_amenities(self, mock_db):
        """Test property search with amenity filtering."""
        mock_prop = Mock()
        mock_prop.id = "prop_1"
        mock_prop.to_dict.return_value = {
            'property_id': 'prop_1',
            'name': 'Villa with Pool',
            'amenities': ['wifi', 'pool', 'parking']
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_prop]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        with patch('mcp_servers.firestore.server.check_booking_overlap', return_value=False):
            result = await search_properties(
                city="Miami",
                amenities=["wifi", "pool"]
            )
        
        assert result['success'] is True
        assert len(result['properties']) == 1
    
    @pytest.mark.asyncio
    async def test_search_properties_with_date_overlap(self, mock_db):
        """Test property search excludes properties with booking overlaps."""
        mock_prop = Mock()
        mock_prop.id = "prop_1"
        mock_prop.to_dict.return_value = {
            'property_id': 'prop_1',
            'name': 'Unavailable Villa'
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_prop]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        # Mock overlap check to return True (property unavailable)
        with patch('mcp_servers.firestore.server.check_booking_overlap', return_value=True):
            result = await search_properties(
                city="Miami",
                check_in_date="2025-03-15",
                check_out_date="2025-03-18"
            )
        
        assert result['success'] is True
        assert result['count'] == 0  # Property should be filtered out
    
    @pytest.mark.asyncio
    async def test_create_booking(self, mock_db):
        """Test booking creation."""
        with patch('mcp_servers.firestore.server.create_booking_transaction') as mock_transaction:
            mock_transaction.return_value = {
                'success': True,
                'booking_id': 'booking_123',
                'message': 'Booking created successfully'
            }
            
            result = await create_booking(
                property_id="prop_123",
                guest_id="guest_123",
                host_id="host_123",
                check_in_date="2025-03-15",
                check_out_date="2025-03-18",
                number_of_guests=4,
                total_price=1200.0
            )
            
            assert result['success'] is True
            assert result['booking_id'] == 'booking_123'
            
            # Verify transaction was called with correct data
            mock_transaction.assert_called_once()
            call_args = mock_transaction.call_args[0][2]  # booking_data argument
            assert call_args['property_id'] == "prop_123"
            assert call_args['guest_id'] == "guest_123"
            assert call_args['total_price'] == 1200.0
    
    @pytest.mark.asyncio
    async def test_get_booking_existing(self, mock_db):
        """Test getting existing booking."""
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'booking_id': 'booking_123',
            'property_id': 'prop_123',
            'guest_id': 'guest_123',
            'status': 'confirmed'
        }
        
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        
        result = await get_booking("booking_123")
        
        assert result['success'] is True
        assert result['booking']['booking_id'] == 'booking_123'
        assert result['booking']['status'] == 'confirmed'
    
    @pytest.mark.asyncio
    async def test_get_booking_not_found(self, mock_db):
        """Test getting non-existent booking."""
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        mock_db.collection.return_value = mock_collection
        
        result = await get_booking("nonexistent")
        
        assert result['success'] is False
        assert "not found" in result['message']
    
    @pytest.mark.asyncio
    async def test_update_booking_status(self, mock_db):
        """Test updating booking status."""
        with patch('mcp_servers.firestore.server.update_booking_status') as mock_update:
            mock_update.return_value = {
                'success': True,
                'message': 'Status updated successfully'
            }
            
            result = await update_booking_status_tool(
                booking_id="booking_123",
                new_status="confirmed",
                reason="Payment processed"
            )
            
            assert result['success'] is True
            mock_update.assert_called_once_with(
                mock_db, "booking_123", "confirmed", "Payment processed"
            )
    
    @pytest.mark.asyncio
    async def test_get_user_bookings_as_guest(self, mock_db):
        """Test getting user bookings as guest."""
        mock_booking1 = Mock()
        mock_booking1.to_dict.return_value = {
            'booking_id': 'booking_1',
            'guest_id': 'user_123',
            'status': 'confirmed'
        }
        
        mock_booking2 = Mock()
        mock_booking2.to_dict.return_value = {
            'booking_id': 'booking_2',
            'guest_id': 'user_123',
            'status': 'pending'
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_booking1, mock_booking2]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        result = await get_user_bookings(
            user_id="user_123",
            role="guest"
        )
        
        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['bookings']) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_bookings_as_host(self, mock_db):
        """Test getting user bookings as host."""
        mock_booking = Mock()
        mock_booking.to_dict.return_value = {
            'booking_id': 'booking_1',
            'host_id': 'host_123',
            'status': 'confirmed'
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_booking]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        result = await get_user_bookings(
            user_id="host_123",
            role="host"
        )
        
        assert result['success'] is True
        assert result['count'] == 1
        assert result['bookings'][0]['host_id'] == 'host_123'
    
    @pytest.mark.asyncio
    async def test_get_user_bookings_with_status_filter(self, mock_db):
        """Test getting user bookings with status filter."""
        mock_booking = Mock()
        mock_booking.to_dict.return_value = {
            'booking_id': 'booking_1',
            'guest_id': 'user_123',
            'status': 'confirmed'
        }
        
        mock_query = Mock()
        mock_query.stream.return_value = [mock_booking]
        mock_query.where.return_value = mock_query
        
        mock_collection = Mock()
        mock_collection.where.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        
        result = await get_user_bookings(
            user_id="user_123",
            role="guest",
            status="confirmed"
        )
        
        assert result['success'] is True
        assert result['bookings'][0]['status'] == 'confirmed'
        
        # Verify status filter was applied
        assert mock_query.where.call_count >= 2  # guest_id and status filters


if __name__ == "__main__":
    pytest.main([__file__])
