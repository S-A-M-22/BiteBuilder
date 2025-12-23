"""
Test suite for Pagination functionality.
Comprehensive testing for Django REST Framework pagination classes.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from rest_framework.response import Response

from apps.api.pagination import AdminUsersPagination


@pytest.fixture
def api_factory():
    """Create API request factory for testing."""
    return APIRequestFactory()


@pytest.fixture
def api_client():
    """Create API client for testing."""
    return APIClient()


class TestAdminUsersPagination:
    """Tests for AdminUsersPagination class."""
    
    def test_page_size_default(self):
        """Test default page size is set correctly."""
        pagination = AdminUsersPagination()
        assert pagination.page_size == 10
    
    def test_page_size_query_param(self):
        """Test page_size_query_param is set correctly."""
        pagination = AdminUsersPagination()
        assert pagination.page_size_query_param == "page_size"
    
    def test_get_paginated_response_structure(self):
        """Test get_paginated_response returns correct structure."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 25
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value="http://example.com/next/")
        pagination.get_previous_link = MagicMock(return_value="http://example.com/previous/")
        
        # Test data
        test_data = [{"id": 1, "name": "User1"}, {"id": 2, "name": "User2"}]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 25
        assert response.data["next"] == "http://example.com/next/"
        assert response.data["previous"] == "http://example.com/previous/"
    
    def test_get_paginated_response_with_empty_data(self):
        """Test get_paginated_response with empty data."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 0
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test with empty data
        test_data = []
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == []
        assert response.data["count"] == 0
        assert response.data["next"] is None
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_none_links(self):
        """Test get_paginated_response when links are None."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 5
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods to return None
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data
        test_data = [{"id": 1, "name": "User1"}]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 5
        assert response.data["next"] is None
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_large_dataset(self):
        """Test get_paginated_response with large dataset."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 1000
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value="http://example.com/api/users/?page=2")
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data with 10 items (page_size)
        test_data = [{"id": i, "name": f"User{i}"} for i in range(1, 11)]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 1000
        assert response.data["next"] == "http://example.com/api/users/?page=2"
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_middle_page(self):
        """Test get_paginated_response with middle page (both links present)."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 100
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value="http://example.com/api/users/?page=3")
        pagination.get_previous_link = MagicMock(return_value="http://example.com/api/users/?page=1")
        
        # Test data
        test_data = [{"id": i, "name": f"User{i}"} for i in range(11, 21)]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 100
        assert response.data["next"] == "http://example.com/api/users/?page=3"
        assert response.data["previous"] == "http://example.com/api/users/?page=1"
    
    def test_get_paginated_response_with_complex_data(self):
        """Test get_paginated_response with complex nested data."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 3
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data with complex nested structure
        test_data = [
            {
                "id": 1,
                "name": "User1",
                "profile": {
                    "age": 25,
                    "email": "user1@example.com",
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            },
            {
                "id": 2,
                "name": "User2",
                "profile": {
                    "age": 30,
                    "email": "user2@example.com",
                    "preferences": {
                        "theme": "light",
                        "notifications": False
                    }
                }
            }
        ]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 3
        assert response.data["next"] is None
        assert response.data["previous"] is None
        
        # Verify nested data integrity
        assert response.data["results"][0]["profile"]["preferences"]["theme"] == "dark"
        assert response.data["results"][1]["profile"]["preferences"]["notifications"] is False
    
    def test_get_paginated_response_with_special_characters(self):
        """Test get_paginated_response with special characters in data."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 1
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data with special characters
        test_data = [
            {
                "id": 1,
                "name": "User with special chars: !@#$%^&*()",
                "email": "user@example.com",
                "description": "Contains unicode: 你好世界 🌍"
            }
        ]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 1
        assert response.data["next"] is None
        assert response.data["previous"] is None
        
        # Verify special characters are preserved
        assert "你好世界 🌍" in response.data["results"][0]["description"]
        assert "!@#$%^&*()" in response.data["results"][0]["name"]


class TestAdminUsersPaginationIntegration:
    """Integration tests for AdminUsersPagination."""
    
    def test_pagination_with_viewset(self, api_factory):
        """Test pagination integration with a ViewSet."""
        from rest_framework.viewsets import ModelViewSet
        from rest_framework.serializers import ModelSerializer
        from django.db import models
        
        # Create a mock model
        class MockUser(models.Model):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'test'
        
        # Create a mock serializer
        class MockUserSerializer(ModelSerializer):
            class Meta:
                model = MockUser
                fields = ['id', 'name']
        
        # Create a mock ViewSet
        class MockUserViewSet(ModelViewSet):
            queryset = MockUser.objects.none()
            serializer_class = MockUserSerializer
            pagination_class = AdminUsersPagination
        
        # Test pagination class assignment
        viewset = MockUserViewSet()
        assert isinstance(viewset.pagination_class, type(AdminUsersPagination))
        assert viewset.pagination_class.page_size == 10
        assert viewset.pagination_class.page_size_query_param == "page_size"
    
    def test_pagination_with_different_page_sizes(self):
        """Test pagination with different page sizes."""
        # Test with custom page size
        pagination = AdminUsersPagination()
        pagination.page_size = 20
        
        assert pagination.page_size == 20
        
        # Test with very small page size
        pagination.page_size = 1
        assert pagination.page_size == 1
        
        # Test with large page size
        pagination.page_size = 100
        assert pagination.page_size == 100
    
    def test_pagination_with_different_query_params(self):
        """Test pagination with different query parameter names."""
        # Test with custom query param
        pagination = AdminUsersPagination()
        pagination.page_size_query_param = "limit"
        
        assert pagination.page_size_query_param == "limit"
        
        # Test with different query param
        pagination.page_size_query_param = "size"
        assert pagination.page_size_query_param == "size"
    
    def test_pagination_response_serialization(self):
        """Test that pagination response can be serialized."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 50
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value="http://example.com/next/")
        pagination.get_previous_link = MagicMock(return_value="http://example.com/previous/")
        
        # Test data
        test_data = [{"id": i, "name": f"User{i}"} for i in range(1, 11)]
        
        response = pagination.get_paginated_response(test_data)
        
        # Test that response data can be converted to dict
        response_dict = response.data
        
        # Verify all expected keys are present
        expected_keys = ["results", "count", "next", "previous"]
        for key in expected_keys:
            assert key in response_dict
        
        # Verify data types
        assert isinstance(response_dict["results"], list)
        assert isinstance(response_dict["count"], int)
        assert response_dict["next"] is None or isinstance(response_dict["next"], str)
        assert response_dict["previous"] is None or isinstance(response_dict["previous"], str)


class TestAdminUsersPaginationEdgeCases:
    """Edge case tests for AdminUsersPagination."""
    
    def test_get_paginated_response_with_none_data(self):
        """Test get_paginated_response with None data."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 0
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test with None data
        response = pagination.get_paginated_response(None)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] is None
        assert response.data["count"] == 0
        assert response.data["next"] is None
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_negative_count(self):
        """Test get_paginated_response with negative count."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = -5  # Negative count
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data
        test_data = [{"id": 1, "name": "User1"}]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == -5
        assert response.data["next"] is None
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_zero_count(self):
        """Test get_paginated_response with zero count."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 0
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value=None)
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data
        test_data = []
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == []
        assert response.data["count"] == 0
        assert response.data["next"] is None
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_very_large_count(self):
        """Test get_paginated_response with very large count."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 999999999  # Very large count
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods
        pagination.get_next_link = MagicMock(return_value="http://example.com/next/")
        pagination.get_previous_link = MagicMock(return_value=None)
        
        # Test data
        test_data = [{"id": i, "name": f"User{i}"} for i in range(1, 11)]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 999999999
        assert response.data["next"] == "http://example.com/next/"
        assert response.data["previous"] is None
    
    def test_get_paginated_response_with_malformed_links(self):
        """Test get_paginated_response with malformed links."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 10
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods to return malformed URLs
        pagination.get_next_link = MagicMock(return_value="not-a-valid-url")
        pagination.get_previous_link = MagicMock(return_value="also-not-valid")
        
        # Test data
        test_data = [{"id": 1, "name": "User1"}]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 10
        assert response.data["next"] == "not-a-valid-url"
        assert response.data["previous"] == "also-not-valid"
    
    def test_get_paginated_response_with_empty_string_links(self):
        """Test get_paginated_response with empty string links."""
        pagination = AdminUsersPagination()
        
        # Mock the page and paginator
        mock_page = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.count = 5
        mock_page.paginator = mock_paginator
        
        pagination.page = mock_page
        
        # Mock the link methods to return empty strings
        pagination.get_next_link = MagicMock(return_value="")
        pagination.get_previous_link = MagicMock(return_value="")
        
        # Test data
        test_data = [{"id": 1, "name": "User1"}]
        
        response = pagination.get_paginated_response(test_data)
        
        # Verify response structure
        assert isinstance(response, Response)
        assert response.data["results"] == test_data
        assert response.data["count"] == 5
        assert response.data["next"] == ""
        assert response.data["previous"] == ""
    
    def test_pagination_class_instantiation(self):
        """Test AdminUsersPagination class instantiation."""
        # Test multiple instances
        pagination1 = AdminUsersPagination()
        pagination2 = AdminUsersPagination()
        
        # Verify they are different instances
        assert pagination1 is not pagination2
        
        # Verify they have the same default values
        assert pagination1.page_size == pagination2.page_size
        assert pagination1.page_size_query_param == pagination2.page_size_query_param
        
        # Verify default values
        assert pagination1.page_size == 10
        assert pagination1.page_size_query_param == "page_size"
    
    def test_pagination_inheritance(self):
        """Test AdminUsersPagination inheritance from PageNumberPagination."""
        from rest_framework.pagination import PageNumberPagination
        
        pagination = AdminUsersPagination()
        
        # Verify inheritance
        assert isinstance(pagination, PageNumberPagination)
        assert issubclass(AdminUsersPagination, PageNumberPagination)
        
        # Verify it has the parent class methods
        assert hasattr(pagination, 'get_paginated_response')
        assert hasattr(pagination, 'get_next_link')
        assert hasattr(pagination, 'get_previous_link')
    
    def test_pagination_with_custom_attributes(self):
        """Test pagination with custom attributes."""
        pagination = AdminUsersPagination()
        
        # Test setting custom attributes
        pagination.page_size = 25
        pagination.page_size_query_param = "limit"
        
        assert pagination.page_size == 25
        assert pagination.page_size_query_param == "limit"
        
        # Test that attributes can be changed multiple times
        pagination.page_size = 50
        pagination.page_size_query_param = "size"
        
        assert pagination.page_size == 50
        assert pagination.page_size_query_param == "size"
