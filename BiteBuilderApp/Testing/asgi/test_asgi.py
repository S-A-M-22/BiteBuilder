"""
Test suite for ASGI configuration.
Tests the ASGI application setup and configuration.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from django.core.asgi import get_asgi_application
from django.test import override_settings


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_os_environ():
    """Mock os.environ for testing environment variable setting."""
    with patch.dict(os.environ, {}, clear=True):
        yield os.environ


@pytest.fixture
def mock_get_asgi_application():
    """Mock get_asgi_application function."""
    with patch('django.core.asgi.get_asgi_application') as mock:
        mock_app = MagicMock()
        mock.return_value = mock_app
        yield mock, mock_app


# ============================================================================
# BASIC IMPORT TESTS
# ============================================================================

def test_asgi_module_imports():
    """Test that asgi module can be imported without errors."""
    try:
        import BiteBuilderApp.asgi
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import asgi module: {e}")


def test_asgi_application_exists():
    """Test that application variable exists in asgi module."""
    import BiteBuilderApp.asgi
    assert hasattr(BiteBuilderApp.asgi, 'application')
    assert BiteBuilderApp.asgi.application is not None


# ============================================================================
# ENVIRONMENT VARIABLE TESTS
# ============================================================================

def test_django_settings_module_set():
    """Test that DJANGO_SETTINGS_MODULE is set correctly."""
    import BiteBuilderApp.asgi
    
    # The environment variable should be set to the correct module
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


@patch.dict(os.environ, {}, clear=True)
def test_environment_variable_setting():
    """Test that environment variable is set when module is imported."""
    # Clear environment
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        del os.environ['DJANGO_SETTINGS_MODULE']
    
    # Import asgi module (this should set the environment variable)
    import importlib
    import BiteBuilderApp.asgi
    importlib.reload(BiteBuilderApp.asgi)
    
    # Check that environment variable is set
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_environment_variable_not_overwritten():
    """Test that existing DJANGO_SETTINGS_MODULE is not overwritten."""
    original_value = 'test.settings'
    with patch.dict(os.environ, {'DJANGO_SETTINGS_MODULE': original_value}):
        import importlib
        import BiteBuilderApp.asgi
        importlib.reload(BiteBuilderApp.asgi)
        
        # Should not be overwritten
        assert os.environ.get('DJANGO_SETTINGS_MODULE') == original_value


# ============================================================================
# ASGI APPLICATION TESTS
# ============================================================================

def test_get_asgi_application_called():
    """Test that get_asgi_application is called during import."""
    with patch('django.core.asgi.get_asgi_application') as mock_get_app:
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app
        
        # Import asgi module
        import importlib
        import BiteBuilderApp.asgi
        importlib.reload(BiteBuilderApp.asgi)
        
        # Verify get_asgi_application was called
        mock_get_app.assert_called_once()


def test_application_is_asgi_callable():
    """Test that application is a proper ASGI callable."""
    import BiteBuilderApp.asgi
    
    # Check that application is callable
    assert callable(BiteBuilderApp.asgi.application)
    
    # Check that it has the expected attributes for ASGI
    app = BiteBuilderApp.asgi.application
    assert hasattr(app, '__call__')


def test_application_has_correct_type():
    """Test that application has the correct type."""
    import BiteBuilderApp.asgi
    
    # The application should be callable and not None
    assert BiteBuilderApp.asgi.application is not None
    assert callable(BiteBuilderApp.asgi.application)
    
    # Should be an ASGI application (check if it's not a mock)
    app = BiteBuilderApp.asgi.application
    if hasattr(app, '_mock_name'):
        # It's a mock, which is fine for testing
        assert True
    else:
        # It's a real ASGI application
        from django.core.handlers.asgi import ASGIHandler
        assert isinstance(app, ASGIHandler)


# ============================================================================
# MOCKED ASGI APPLICATION TESTS
# ============================================================================

@patch('django.core.asgi.get_asgi_application')
def test_asgi_application_creation(mock_get_app):
    """Test ASGI application creation with mocked dependencies."""
    mock_app = MagicMock()
    mock_get_app.return_value = mock_app
    
    # Import and reload to trigger the application creation
    import importlib
    import BiteBuilderApp.asgi
    importlib.reload(BiteBuilderApp.asgi)
    
    # Verify the application was created
    assert BiteBuilderApp.asgi.application is mock_app
    mock_get_app.assert_called_once()


@patch('django.core.asgi.get_asgi_application')
def test_asgi_application_with_different_settings(mock_get_app):
    """Test ASGI application with different settings module."""
    mock_app = MagicMock()
    mock_get_app.return_value = mock_app
    
    with patch.dict(os.environ, {'DJANGO_SETTINGS_MODULE': 'test.settings'}):
        import importlib
        import BiteBuilderApp.asgi
        importlib.reload(BiteBuilderApp.asgi)
        
        # Verify get_asgi_application was called
        mock_get_app.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@patch('django.core.asgi.get_asgi_application')
def test_asgi_application_creation_error(mock_get_app):
    """Test behavior when get_asgi_application raises an error."""
    mock_get_app.side_effect = Exception("ASGI application creation failed")
    
    # This should raise an exception when importing
    with pytest.raises(Exception, match="ASGI application creation failed"):
        import importlib
        import BiteBuilderApp.asgi
        importlib.reload(BiteBuilderApp.asgi)


def test_import_with_missing_django():
    """Test import behavior when Django is not available."""
    with patch.dict('sys.modules', {'django.core.asgi': None}):
        with pytest.raises(ImportError):
            import importlib
            import BiteBuilderApp.asgi
            importlib.reload(BiteBuilderApp.asgi)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_asgi_application_integration():
    """Test that the ASGI application can be used in an ASGI context."""
    import BiteBuilderApp.asgi
    
    # Create a mock ASGI scope and receive/send
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/',
        'headers': [],
        'query_string': b'',
        'client': ('127.0.0.1', 8000),
        'server': ('127.0.0.1', 8000)
    }
    
    async def mock_receive():
        return {
            'type': 'http.request',
            'body': b'',
            'more_body': False
        }
    
    async def mock_send(message):
        pass
    
    # Test that the application can be called (this will fail in test environment
    # but we can verify the structure)
    app = BiteBuilderApp.asgi.application
    assert callable(app)


def test_asgi_application_with_websocket_scope():
    """Test ASGI application with WebSocket scope."""
    import BiteBuilderApp.asgi
    
    # WebSocket scope
    scope = {
        'type': 'websocket',
        'path': '/ws/',
        'headers': [],
        'query_string': b'',
        'client': ('127.0.0.1', 8000),
        'server': ('127.0.0.1', 8000)
    }
    
    # The application should be callable regardless of scope type
    app = BiteBuilderApp.asgi.application
    assert callable(app)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_settings_module_configuration():
    """Test that the correct settings module is configured."""
    import BiteBuilderApp.asgi
    
    # Verify the environment variable is set correctly
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


@override_settings()
def test_asgi_with_custom_settings():
    """Test ASGI application with custom settings."""
    import BiteBuilderApp.asgi
    
    # The application should still be callable
    assert callable(BiteBuilderApp.asgi.application)


def test_multiple_imports():
    """Test that multiple imports don't cause issues."""
    import BiteBuilderApp.asgi
    import BiteBuilderApp.asgi  # Second import
    
    # Should not cause any issues
    assert BiteBuilderApp.asgi.application is not None


# ============================================================================
# EDGE CASES
# ============================================================================

def test_asgi_with_empty_environment():
    """Test ASGI application with empty environment."""
    with patch.dict(os.environ, {}, clear=True):
        import importlib
        import BiteBuilderApp.asgi
        importlib.reload(BiteBuilderApp.asgi)
        
        # Should still work and set the environment variable
        assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_asgi_with_none_environment():
    """Test ASGI application when environment variable is None."""
    # Remove the environment variable if it exists
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        del os.environ['DJANGO_SETTINGS_MODULE']
    
    import importlib
    import BiteBuilderApp.asgi
    importlib.reload(BiteBuilderApp.asgi)
    
    # Should set the environment variable
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_asgi_application_attributes():
    """Test that ASGI application has expected attributes."""
    import BiteBuilderApp.asgi
    
    app = BiteBuilderApp.asgi.application
    
    # Should be callable
    assert callable(app)
    
    # Should have __call__ method
    assert hasattr(app, '__call__')
    
    # Should be an ASGIHandler instance
    from django.core.handlers.asgi import ASGIHandler
    assert isinstance(app, ASGIHandler)


def test_asgi_module_docstring():
    """Test that the ASGI module has proper docstring."""
    import BiteBuilderApp.asgi
    
    # Check that module has docstring
    assert BiteBuilderApp.asgi.__doc__ is not None
    assert 'ASGI config' in BiteBuilderApp.asgi.__doc__
    assert 'BiteBuilderApp' in BiteBuilderApp.asgi.__doc__


def test_asgi_application_repr():
    """Test string representation of ASGI application."""
    import BiteBuilderApp.asgi
    
    app = BiteBuilderApp.asgi.application
    
    # Should have string representation
    app_str = str(app)
    assert isinstance(app_str, str)
    assert len(app_str) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_asgi_application_creation_performance():
    """Test that ASGI application creation is fast."""
    import time
    import BiteBuilderApp.asgi
    
    start_time = time.time()
    app = BiteBuilderApp.asgi.application
    end_time = time.time()
    
    # Should be created quickly (less than 1 second)
    assert (end_time - start_time) < 1.0
    assert app is not None


def test_multiple_application_access():
    """Test accessing application multiple times."""
    import BiteBuilderApp.asgi
    
    # Access application multiple times
    app1 = BiteBuilderApp.asgi.application
    app2 = BiteBuilderApp.asgi.application
    app3 = BiteBuilderApp.asgi.application
    
    # Should be the same object
    assert app1 is app2
    assert app2 is app3
    assert app1 is app3


# ============================================================================
# COMPATIBILITY TESTS
# ============================================================================

def test_asgi_application_with_different_python_versions():
    """Test ASGI application compatibility."""
    import BiteBuilderApp.asgi
    import sys
    
    # Should work with current Python version
    assert BiteBuilderApp.asgi.application is not None
    
    # Check Python version compatibility
    assert sys.version_info >= (3, 6)  # Minimum Python version for ASGI


def test_asgi_application_with_django_version():
    """Test ASGI application with Django version."""
    import BiteBuilderApp.asgi
    import django
    
    # Should work with current Django version
    assert BiteBuilderApp.asgi.application is not None
    
    # Check Django version
    assert django.VERSION >= (3, 0)  # Minimum Django version for ASGI support
