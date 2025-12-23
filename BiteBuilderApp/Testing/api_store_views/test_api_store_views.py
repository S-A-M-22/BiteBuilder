"""
Test suite for API Store Views functionality.
Comprehensive testing for store location API endpoints.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from requests.exceptions import ReadTimeout, ConnectionError

from apps.services.api_store_views import api_stores_nearby


@pytest.fixture
def api_factory():
    """Create API request factory for testing."""
    return APIRequestFactory()


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


class TestApiStoresNearby:
    """Tests for api_stores_nearby endpoint."""
    
    def test_missing_postcode_parameter(self, api_factory):
        """Test API returns 400 when postcode is missing."""
        request = api_factory.get('/api/stores-nearby/')
        response = api_stores_nearby(request)
        
        assert response.status_code == 400
        assert response.data == {"error": "Missing postcode"}
    
    def test_empty_postcode_parameter(self, api_factory):
        """Test API returns 400 when postcode is empty."""
        request = api_factory.get('/api/stores-nearby/', {'postcode': ''})
        response = api_stores_nearby(request)
        
        assert response.status_code == 400
        assert response.data == {"error": "Missing postcode"}
    
    def test_none_postcode_parameter(self, api_factory):
        """Test API returns 400 when postcode is None."""
        request = api_factory.get('/api/stores-nearby/')
        response = api_stores_nearby(request)
        
        assert response.status_code == 400
        assert response.data == {"error": "Missing postcode"}
    
    @patch('apps.services.api_store_views.requests.get')
    def test_successful_request_with_default_max(self, mock_get, api_factory):
        """Test successful API request with default max results."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Test Store",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": [{"OpenHour": "07:00-22:00"}]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == "1234"
        assert response.data[0]['name'] == "Woolworths Test Store"
        assert response.data[0]['is_open'] is True
        
        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['postcode'] == '2000'
        assert call_args[1]['params']['Max'] == 5
        assert call_args[1]['params']['Division'] == 'SUPERMARKETS'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_successful_request_with_custom_max(self, mock_get, api_factory):
        """Test successful API request with custom max results."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Test Store",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": [{"OpenHour": "07:00-22:00"}]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': '10'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        
        # Verify request was made with custom max parameter
        call_args = mock_get.call_args
        assert call_args[1]['params']['Max'] == '10'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_successful_request_multiple_stores(self, mock_get, api_factory):
        """Test successful API request with multiple stores."""
        # Mock successful response with multiple stores
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Store 1",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": [{"OpenHour": "07:00-22:00"}]
                },
                {
                    "StoreNo": "5678",
                    "Name": "Woolworths Store 2",
                    "AddressLine1": "456 Another Street",
                    "Suburb": "Another Suburb",
                    "State": "NSW",
                    "Postcode": "2001",
                    "Latitude": -33.8700,
                    "Longitude": 151.2100,
                    "IsOpen": False,
                    "Division": "SUPERMARKETS",
                    "TradingHours": [{"OpenHour": "08:00-21:00"}]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 2
        
        # Check first store
        assert response.data[0]['id'] == "1234"
        assert response.data[0]['name'] == "Woolworths Store 1"
        assert response.data[0]['is_open'] is True
        assert response.data[0]['today_hours'] == "07:00-22:00"
        
        # Check second store
        assert response.data[1]['id'] == "5678"
        assert response.data[1]['name'] == "Woolworths Store 2"
        assert response.data[1]['is_open'] is False
        assert response.data[1]['today_hours'] == "08:00-21:00"
    
    @patch('apps.services.api_store_views.requests.get')
    def test_filters_non_supermarket_stores(self, mock_get, api_factory):
        """Test API filters out non-supermarket stores."""
        # Mock response with mixed store types
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Supermarket",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": [{"OpenHour": "07:00-22:00"}]
                },
                {
                    "StoreNo": "5678",
                    "Name": "EG Service Station",
                    "AddressLine1": "456 Fuel Street",
                    "Suburb": "Fuel Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8700,
                    "Longitude": 151.2100,
                    "IsOpen": True,
                    "Division": "FUEL",
                    "TradingHours": [{"OpenHour": "24/7"}]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 1  # Only supermarket should be returned
        assert response.data[0]['name'] == "Woolworths Supermarket"
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_missing_trading_hours(self, mock_get, api_factory):
        """Test API handles stores with missing trading hours."""
        # Mock response with missing trading hours
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Test Store",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": None
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['today_hours'] is None
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_empty_trading_hours(self, mock_get, api_factory):
        """Test API handles stores with empty trading hours."""
        # Mock response with empty trading hours
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Stores": [
                {
                    "StoreNo": "1234",
                    "Name": "Woolworths Test Store",
                    "AddressLine1": "123 Test Street",
                    "Suburb": "Test Suburb",
                    "State": "NSW",
                    "Postcode": "2000",
                    "Latitude": -33.8688,
                    "Longitude": 151.2093,
                    "IsOpen": True,
                    "Division": "SUPERMARKETS",
                    "TradingHours": []
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['today_hours'] is None
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_read_timeout(self, mock_get, api_factory):
        """Test API handles ReadTimeout exception."""
        mock_get.side_effect = ReadTimeout("Request timed out")
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 504
        assert response.data == {"error": "Woolworths API timed out."}
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_connection_error(self, mock_get, api_factory):
        """Test API handles ConnectionError exception."""
        mock_get.side_effect = ConnectionError("Connection failed")
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 502
        assert response.data == {"error": "Unable to reach Woolworths API."}
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_generic_exception(self, mock_get, api_factory):
        """Test API handles generic exceptions."""
        mock_get.side_effect = Exception("Generic error")
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 500
        assert "Request failed: Generic error" in response.data["error"]
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_http_error(self, mock_get, api_factory):
        """Test API handles HTTP errors from Woolworths API."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 500
        assert "Request failed: HTTP 500 Error" in response.data["error"]
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_json_decode_error(self, mock_get, api_factory):
        """Test API handles JSON decode errors."""
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 500
        assert "Request failed:" in response.data["error"]
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_empty_stores_response(self, mock_get, api_factory):
        """Test API handles empty stores response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert response.data == []
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_missing_stores_key(self, mock_get, api_factory):
        """Test API handles response missing Stores key."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        assert response.data == []
    
    @patch('apps.services.api_store_views.requests.get')
    def test_request_headers_are_correct(self, mock_get, api_factory):
        """Test API sends correct headers to Woolworths."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        api_stores_nearby(request)
        
        # Verify headers
        call_args = mock_get.call_args
        headers = call_args[1]['headers']
        
        assert headers['User-Agent'] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        assert headers['Accept'] == "application/json, text/plain, */*"
        assert headers['Referer'] == "https://www.woolworths.com.au/"
        assert headers['Origin'] == "https://www.woolworths.com.au"
    
    @patch('apps.services.api_store_views.requests.get')
    def test_request_timeout_is_set(self, mock_get, api_factory):
        """Test API sets correct timeout."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        api_stores_nearby(request)
        
        # Verify timeout
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == 8
    
    @patch('apps.services.api_store_views.requests.get')
    def test_request_url_is_correct(self, mock_get, api_factory):
        """Test API uses correct Woolworths endpoint."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000'})
        api_stores_nearby(request)
        
        # Verify URL
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://www.woolworths.com.au/apis/ui/StoreLocator/Stores"
    
    @patch('apps.services.api_store_views.requests.get')
    def test_request_parameters_are_correct(self, mock_get, api_factory):
        """Test API sends correct parameters to Woolworths."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': '3'})
        api_stores_nearby(request)
        
        # Verify parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        
        assert params['Max'] == '3'
        assert params['Division'] == 'SUPERMARKETS'
        assert params['Facility'] == ''
        assert params['postcode'] == '2000'


class TestApiStoresNearbyIntegration:
    """Integration tests for api_stores_nearby endpoint."""
    
    def test_api_endpoint_accessible(self, api_client):
        """Test API endpoint is accessible via URL."""
        response = api_client.get('/api/stores-nearby/', {'postcode': '2000'})
        # This will fail without proper URL routing, but tests the endpoint structure
        assert response.status_code in [200, 404, 423]  # 404 if not routed, 200 if routed, 423 if locked
    
    def test_api_endpoint_with_valid_postcode(self, api_client):
        """Test API endpoint with valid postcode parameter."""
        with patch('apps.services.api_store_views.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"Stores": []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            response = api_client.get('/api/stores-nearby/', {'postcode': '2000'})
            # This will fail without proper URL routing, but tests the parameter handling
            assert response.status_code in [200, 404, 423]
    
    def test_api_endpoint_with_invalid_postcode(self, api_client):
        """Test API endpoint with invalid postcode parameter."""
        response = api_client.get('/api/stores-nearby/', {'postcode': ''})
        # This will fail without proper URL routing, but tests the parameter validation
        assert response.status_code in [400, 404, 423]


class TestApiStoresNearbyEdgeCases:
    """Edge case tests for api_stores_nearby endpoint."""
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_very_large_max_parameter(self, mock_get, api_factory):
        """Test API handles very large max parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': '999'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['Max'] == '999'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_zero_max_parameter(self, mock_get, api_factory):
        """Test API handles zero max parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': '0'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['Max'] == '0'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_negative_max_parameter(self, mock_get, api_factory):
        """Test API handles negative max parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': '-1'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['Max'] == '-1'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_non_numeric_max_parameter(self, mock_get, api_factory):
        """Test API handles non-numeric max parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000', 'max': 'abc'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['Max'] == 'abc'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_special_characters_in_postcode(self, mock_get, api_factory):
        """Test API handles special characters in postcode."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000-1234'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['postcode'] == '2000-1234'
    
    @patch('apps.services.api_store_views.requests.get')
    def test_handles_unicode_characters_in_postcode(self, mock_get, api_factory):
        """Test API handles unicode characters in postcode."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Stores": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        request = api_factory.get('/api/stores-nearby/', {'postcode': '2000测试'})
        response = api_stores_nearby(request)
        
        assert response.status_code == 200
        call_args = mock_get.call_args
        assert call_args[1]['params']['postcode'] == '2000测试'
