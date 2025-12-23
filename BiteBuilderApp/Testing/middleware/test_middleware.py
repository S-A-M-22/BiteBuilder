"""
Test suite for Middleware functionality.
Comprehensive testing for Django middleware classes.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpRequest
from django.contrib.sessions.backends.db import SessionStore

from apps.api.middleware import EnforceOtpMiddleware


@pytest.fixture
def request_factory():
    """Create request factory for testing."""
    return RequestFactory()


@pytest.fixture
def mock_get_response():
    """Create mock get_response function."""
    return MagicMock()


@pytest.fixture
def middleware(mock_get_response):
    """Create middleware instance for testing."""
    return EnforceOtpMiddleware(mock_get_response)


class TestEnforceOtpMiddleware:
    """Tests for EnforceOtpMiddleware class."""
    
    def test_middleware_initialization(self, mock_get_response):
        """Test middleware initialization."""
        middleware = EnforceOtpMiddleware(mock_get_response)
        assert middleware.get_response == mock_get_response
    
    def test_middleware_callable(self, middleware):
        """Test middleware is callable."""
        assert callable(middleware)
    
    def test_allowlist_paths_login(self, middleware, request_factory):
        """Test that login path is allowed."""
        request = request_factory.get('/api/auth/login/')
        request.session = {}
        
        response = middleware(request)
        
        # Should call get_response for allowed paths
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_register(self, middleware, request_factory):
        """Test that register path is allowed."""
        request = request_factory.get('/api/auth/register/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_verify_otp(self, middleware, request_factory):
        """Test that verify_otp path is allowed."""
        request = request_factory.get('/api/auth/verify_otp/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_verify(self, middleware, request_factory):
        """Test that verify path is allowed."""
        request = request_factory.get('/api/auth/verify/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_logout(self, middleware, request_factory):
        """Test that logout path is allowed."""
        request = request_factory.get('/api/auth/logout/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_reset_password(self, middleware, request_factory):
        """Test that resetPassword path is allowed."""
        request = request_factory.get('/api/auth/resetPassword/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_api_otp_reset_password(self, middleware, request_factory):
        """Test that api_otp_resetPassword path is allowed."""
        request = request_factory.get('/api/auth/api_otp_resetPassword/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_admin(self, middleware, request_factory):
        """Test that admin path is allowed."""
        request = request_factory.get('/admin/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_static(self, middleware, request_factory):
        """Test that static path is allowed."""
        request = request_factory.get('/static/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_with_parameters(self, middleware, request_factory):
        """Test that allowlist paths with parameters are allowed."""
        request = request_factory.get('/api/auth/login/?param=value')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_allowlist_paths_with_trailing_slash(self, middleware, request_factory):
        """Test that allowlist paths with trailing slash work."""
        request = request_factory.get('/api/auth/login')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_user_session_without_otp_verification(self, middleware, request_factory):
        """Test that user session without OTP verification is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_otp_verification(self, middleware, request_factory):
        """Test that user session with OTP verification is allowed."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_no_user_session(self, middleware, request_factory):
        """Test that request without user session is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {}
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_none_otp_verification(self, middleware, request_factory):
        """Test that user session with None OTP verification is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': None
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_empty_string_otp_verification(self, middleware, request_factory):
        """Test that user session with empty string OTP verification is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': ''
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_zero_otp_verification(self, middleware, request_factory):
        """Test that user session with zero OTP verification is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': 0
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_false_otp_verification(self, middleware, request_factory):
        """Test that user session with False OTP verification is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_missing_otp_verification_key(self, middleware, request_factory):
        """Test that user session missing otp_verified key is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 'user123'
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_missing_sb_user_id_key(self, middleware, request_factory):
        """Test that user session missing sb_user_id key is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_empty_sb_user_id(self, middleware, request_factory):
        """Test that user session with empty sb_user_id is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': '',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_none_sb_user_id(self, middleware, request_factory):
        """Test that user session with None sb_user_id is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': None,
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_zero_sb_user_id(self, middleware, request_factory):
        """Test that user session with zero sb_user_id is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': 0,
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_user_session_with_false_sb_user_id(self, middleware, request_factory):
        """Test that user session with False sb_user_id is blocked."""
        request = request_factory.get('/api/some-protected-endpoint/')
        request.session = {
            'sb_user_id': False,
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()


class TestEnforceOtpMiddlewareIntegration:
    """Integration tests for EnforceOtpMiddleware."""
    
    def test_middleware_with_different_http_methods(self, middleware, request_factory):
        """Test middleware with different HTTP methods."""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        
        for method in methods:
            request = getattr(request_factory, method.lower())('/api/some-endpoint/')
            request.session = {
                'sb_user_id': 'user123',
                'otp_verified': True
            }
            
            response = middleware(request)
            
            middleware.get_response.assert_called_with(request)
            middleware.get_response.reset_mock()
    
    def test_middleware_with_allowlist_and_session(self, middleware, request_factory):
        """Test middleware with allowlist paths and valid session."""
        request = request_factory.get('/api/auth/login/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False  # Even with unverified OTP, allowlist should work
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_with_allowlist_and_no_session(self, middleware, request_factory):
        """Test middleware with allowlist paths and no session."""
        request = request_factory.get('/api/auth/register/')
        request.session = {}  # No session
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_chain_execution(self, request_factory):
        """Test middleware chain execution."""
        def mock_get_response(request):
            return JsonResponse({"success": True})
        
        middleware = EnforceOtpMiddleware(mock_get_response)
        
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert response.status_code == 200
        assert response.content.decode() == '{"success": true}'
    
    def test_middleware_chain_blocked_execution(self, request_factory):
        """Test middleware chain blocked execution."""
        def mock_get_response(request):
            return JsonResponse({"success": True})
        
        middleware = EnforceOtpMiddleware(mock_get_response)
        
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False
        }
        
        response = middleware(request)
        
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "OTP required"}'


class TestEnforceOtpMiddlewareEdgeCases:
    """Edge case tests for EnforceOtpMiddleware."""
    
    def test_middleware_with_none_session(self, middleware, request_factory):
        """Test middleware with None session."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = None
        
        with pytest.raises(AttributeError):
            middleware(request)
    
    def test_middleware_with_missing_session_attribute(self, middleware, request_factory):
        """Test middleware with request missing session attribute."""
        request = request_factory.get('/api/some-endpoint/')
        delattr(request, 'session')
        
        with pytest.raises(AttributeError):
            middleware(request)
    
    def test_middleware_with_session_get_method_error(self, middleware, request_factory):
        """Test middleware when session.get method raises an error."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = MagicMock()
        request.session.get.side_effect = Exception("Session error")
        
        with pytest.raises(Exception, match="Session error"):
            middleware(request)
    
    def test_middleware_with_path_attribute_error(self, middleware, request_factory):
        """Test middleware when request.path raises an error."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {}
        
        with patch.object(request, 'path', side_effect=Exception("Path error")):
            with pytest.raises(Exception, match="Path error"):
                middleware(request)
    
    def test_middleware_with_complex_session_data(self, middleware, request_factory):
        """Test middleware with complex session data."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True,
            'other_data': {'nested': 'value'},
            'list_data': [1, 2, 3],
            'boolean_data': True,
            'number_data': 42
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_with_unicode_path(self, middleware, request_factory):
        """Test middleware with unicode path."""
        request = request_factory.get('/api/测试路径/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_with_special_characters_path(self, middleware, request_factory):
        """Test middleware with special characters in path."""
        request = request_factory.get('/api/special-chars-!@#$%^&*()/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_with_very_long_path(self, middleware, request_factory):
        """Test middleware with very long path."""
        long_path = '/api/' + 'a' * 1000 + '/'
        request = request_factory.get(long_path)
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_with_empty_path(self, middleware, request_factory):
        """Test middleware with empty path."""
        request = request_factory.get('')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_middleware_with_root_path(self, middleware, request_factory):
        """Test middleware with root path."""
        request = request_factory.get('/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_middleware_with_multiple_allowlist_matches(self, middleware, request_factory):
        """Test middleware with path that matches multiple allowlist items."""
        request = request_factory.get('/api/auth/login/extra/path/')
        request.session = {}
        
        response = middleware(request)
        
        middleware.get_response.assert_called_once_with(request)
    
    def test_middleware_allowlist_case_sensitivity(self, middleware, request_factory):
        """Test middleware allowlist case sensitivity."""
        request = request_factory.get('/API/AUTH/LOGIN/')
        request.session = {}
        
        response = middleware(request)
        
        # Should not match due to case sensitivity
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_middleware_with_whitespace_in_path(self, middleware, request_factory):
        """Test middleware with whitespace in path."""
        request = request_factory.get('/api/auth/login/ ')
        request.session = {}
        
        response = middleware(request)
        
        # Should not match due to whitespace
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response.content.decode() == '{"error": "invalid session"}'
        middleware.get_response.assert_not_called()
    
    def test_middleware_json_response_encoding(self, middleware, request_factory):
        """Test middleware JSON response encoding."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False
        }
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response['Content-Type'] == 'application/json'
        assert response.content.decode('utf-8') == '{"error": "OTP required"}'
    
    def test_middleware_json_response_invalid_session_encoding(self, middleware, request_factory):
        """Test middleware JSON response encoding for invalid session."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {}
        
        response = middleware(request)
        
        assert isinstance(response, JsonResponse)
        assert response.status_code == 423
        assert response['Content-Type'] == 'application/json'
        assert response.content.decode('utf-8') == '{"error": "invalid session"}'


class TestEnforceOtpMiddlewarePerformance:
    """Performance tests for EnforceOtpMiddleware."""
    
    def test_middleware_allowlist_performance(self, middleware, request_factory):
        """Test middleware allowlist performance with many requests."""
        allowlist_paths = [
            "/api/auth/login/",
            "/api/auth/register/",
            "/api/auth/verify_otp/",
            "/api/auth/verify/",
            "/api/auth/logout/",
            "/api/auth/resetPassword/",
            "/api/auth/api_otp_resetPassword/",
            "/admin/",
            "/static/"
        ]
        
        for path in allowlist_paths:
            request = request_factory.get(path)
            request.session = {}
            
            response = middleware(request)
            
            middleware.get_response.assert_called_with(request)
            middleware.get_response.reset_mock()
    
    def test_middleware_session_check_performance(self, middleware, request_factory):
        """Test middleware session check performance."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': True
        }
        
        # Run multiple times to test performance
        for _ in range(100):
            response = middleware(request)
            middleware.get_response.assert_called_with(request)
            middleware.get_response.reset_mock()
    
    def test_middleware_blocked_request_performance(self, middleware, request_factory):
        """Test middleware blocked request performance."""
        request = request_factory.get('/api/some-endpoint/')
        request.session = {
            'sb_user_id': 'user123',
            'otp_verified': False
        }
        
        # Run multiple times to test performance
        for _ in range(100):
            response = middleware(request)
            assert isinstance(response, JsonResponse)
            assert response.status_code == 423
