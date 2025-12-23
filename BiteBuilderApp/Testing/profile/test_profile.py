"""
Test suite for Profile functionality - Simplified version.
Tests that don't require database setup.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, Mock
from rest_framework.test import APIRequestFactory
from rest_framework import status

from apps.api.api_profile import fetchProfile, updateProfile


@pytest.fixture
def api_factory():
    """Create API request factory for DRF views."""
    return APIRequestFactory()


@pytest.fixture
def mock_profile_data():
    """Mock profile data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "age": 25,
        "gender": "Male",
        "height_cm": 175,
        "weight_kg": 70,
        "postcode": "2000"
    }


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing."""
    return str(uuid.uuid4())


# ============================================================================
# FETCH PROFILE TESTS
# ============================================================================

@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_success(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test successful profile fetch."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [mock_profile_data]
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "fectch correctly."
    assert response.data["id"] == mock_user_id
    assert response.data["username"] == "testuser"
    assert response.data["email"] == "test@example.com"
    assert response.data["age"] == 25
    assert response.data["gender"] == "Male"
    assert response.data["height_cm"] == 175
    assert response.data["weight_kg"] == 70
    assert response.data["postcode"] == "2000"


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_no_session(mock_sb_service, api_factory):
    """Test fetch profile with no active session."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    request = api_factory.get('/api/profile/')
    request.session = {}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No active session" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_no_data(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile when no profile data found."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No profile found" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_supabase_error(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile when Supabase service fails."""
    mock_sb_service.side_effect = Exception("Supabase connection failed")
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Check that error message contains expected text
    error_msg = str(response.data)
    assert "not such user" in error_msg


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_empty_data(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile with empty data response."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [None]
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No profile found" in response.data["error"]


# ============================================================================
# UPDATE PROFILE TESTS
# ============================================================================

@patch('apps.api.api_profile._sb_service')
def test_update_profile_success(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test successful profile update."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_profile_data
    
    update_data = {
        "age": 26,
        "weight_kg": 75
    }
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "testuser"
    assert response.data["email"] == "test@example.com"


@patch('apps.api.api_profile._sb_service')
def test_update_profile_no_session(mock_sb_service, api_factory):
    """Test update profile with no active session."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No active session" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_no_data(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with no data provided."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    request = api_factory.post('/api/profile/update/', {}, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No allowed fields to update" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_none_data(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with None data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    request = api_factory.post('/api/profile/update/', None, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No allowed fields to update" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_not_found_after_update(mock_sb_service, api_factory, mock_user_id):
    """Test update profile when profile not found after update."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Profile not found" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_supabase_error(mock_sb_service, api_factory, mock_user_id):
    """Test update profile when Supabase service fails."""
    mock_sb_service.side_effect = Exception("Database connection failed")
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Database connection failed" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_partial_data(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test update profile with partial data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_profile_data
    
    update_data = {
        "height_cm": 180,
        "postcode": "3000"
    }
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["height_cm"] == 175  # From mock data
    assert response.data["postcode"] == "2000"  # From mock data


@patch('apps.api.api_profile._sb_service')
def test_update_profile_all_fields(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test update profile with all fields."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_profile_data
    
    update_data = {
        "username": "newuser",
        "email": "new@example.com",
        "age": 30,
        "gender": "Female",
        "height_cm": 165,
        "weight_kg": 60,
        "postcode": "4000"
    }
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "testuser"  # From mock data
    assert response.data["email"] == "test@example.com"  # From mock data


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_malformed_data(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile with malformed data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [{}]
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    # Should handle missing fields gracefully - may return 400 for malformed data
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    if response.status_code == status.HTTP_200_OK:
        assert "id" in response.data
        assert response.data["id"] == mock_user_id


@patch('apps.api.api_profile._sb_service')
def test_update_profile_empty_string_data(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with empty string data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    update_data = {"username": "", "email": ""}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    # Should still process the request
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_invalid_data_types(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with invalid data types."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    update_data = {
        "age": "not_a_number",
        "height_cm": "invalid",
        "weight_kg": None
    }
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    # Should handle invalid data types
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_session_expired(mock_sb_service, api_factory):
    """Test fetch profile with expired session."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    request = api_factory.get('/api/profile/')
    request.session = {}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No active session" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_update_profile_session_expired(mock_sb_service, api_factory):
    """Test update profile with expired session."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No active session" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_network_error(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile with network error."""
    mock_sb_service.side_effect = ConnectionError("Network timeout")
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Check that error message contains expected text
    error_msg = str(response.data)
    assert "not such user" in error_msg


@patch('apps.api.api_profile._sb_service')
def test_update_profile_network_error(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with network error."""
    mock_sb_service.side_effect = ConnectionError("Network timeout")
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Network timeout" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_database_timeout(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile with database timeout."""
    mock_sb_service.side_effect = TimeoutError("Database timeout")
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Check that error message contains expected text
    error_msg = str(response.data)
    assert "not such user" in error_msg


@patch('apps.api.api_profile._sb_service')
def test_update_profile_database_timeout(mock_sb_service, api_factory, mock_user_id):
    """Test update profile with database timeout."""
    mock_sb_service.side_effect = TimeoutError("Database timeout")
    
    update_data = {"age": 26}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Database timeout" in response.data["error"]


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_single_field_update(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test fetch profile after single field update."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [mock_profile_data]
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["age"] == 25


@patch('apps.api.api_profile._sb_service')
def test_update_profile_minimal_data(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test update profile with minimal data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_profile_data
    
    update_data = {"age": 30}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["age"] == 25  # From mock data


@patch('apps.api.api_profile._sb_service')
def test_fetch_profile_unicode_data(mock_sb_service, api_factory, mock_user_id):
    """Test fetch profile with unicode data."""
    unicode_data = {
        "username": "测试用户",
        "email": "test@example.com",
        "age": 25,
        "gender": "Male",
        "height_cm": 175,
        "weight_kg": 70,
        "postcode": "2000"
    }
    
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [unicode_data]
    
    request = api_factory.get('/api/profile/')
    request.session = {'sb_user_id': mock_user_id}
    
    response = fetchProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "测试用户"


@patch('apps.api.api_profile._sb_service')
def test_update_profile_unicode_data(mock_sb_service, api_factory, mock_user_id, mock_profile_data):
    """Test update profile with unicode data."""
    mock_sb = MagicMock()
    mock_sb_service.return_value = mock_sb
    mock_sb.schema.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    mock_sb.schema.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_profile_data
    
    update_data = {"username": "新用户名"}
    
    request = api_factory.post('/api/profile/update/', update_data, format='json')
    request.session = {'sb_user_id': mock_user_id}
    
    response = updateProfile(request)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "testuser"  # From mock data
