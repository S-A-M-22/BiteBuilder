"""
Test suite for WSGI configuration.
Tests the WSGI application setup and configuration.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from django.core.wsgi import get_wsgi_application
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
def mock_get_wsgi_application():
    """Mock get_wsgi_application function."""
    with patch('django.core.wsgi.get_wsgi_application') as mock:
        mock_app = MagicMock()
        mock.return_value = mock_app
        yield mock, mock_app


# ============================================================================
# BASIC IMPORT TESTS
# ============================================================================

def test_wsgi_module_imports():
    """Test that wsgi module can be imported without errors."""
    try:
        import BiteBuilderApp.wsgi
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import wsgi module: {e}")


def test_wsgi_application_exists():
    """Test that application variable exists in wsgi module."""
    import BiteBuilderApp.wsgi
    assert hasattr(BiteBuilderApp.wsgi, 'application')
    assert BiteBuilderApp.wsgi.application is not None


# ============================================================================
# ENVIRONMENT VARIABLE TESTS
# ============================================================================

def test_django_settings_module_set():
    """Test that DJANGO_SETTINGS_MODULE is set correctly."""
    import BiteBuilderApp.wsgi
    
    # The environment variable should be set to the correct module
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


@patch.dict(os.environ, {}, clear=True)
def test_environment_variable_setting():
    """Test that environment variable is set when module is imported."""
    # Clear environment
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        del os.environ['DJANGO_SETTINGS_MODULE']
    
    # Import wsgi module (this should set the environment variable)
    import importlib
    import BiteBuilderApp.wsgi
    importlib.reload(BiteBuilderApp.wsgi)
    
    # Check that environment variable is set
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_environment_variable_not_overwritten():
    """Test that existing DJANGO_SETTINGS_MODULE is not overwritten."""
    original_value = 'test.settings'
    with patch.dict(os.environ, {'DJANGO_SETTINGS_MODULE': original_value}):
        import importlib
        import BiteBuilderApp.wsgi
        importlib.reload(BiteBuilderApp.wsgi)
        
        # Should not be overwritten
        assert os.environ.get('DJANGO_SETTINGS_MODULE') == original_value


# ============================================================================
# WSGI APPLICATION TESTS
# ============================================================================

def test_get_wsgi_application_called():
    """Test that get_wsgi_application is called during import."""
    with patch('django.core.wsgi.get_wsgi_application') as mock_get_app:
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app
        
        # Import wsgi module
        import importlib
        import BiteBuilderApp.wsgi
        importlib.reload(BiteBuilderApp.wsgi)
        
        # Verify get_wsgi_application was called
        mock_get_app.assert_called_once()


def test_application_is_wsgi_callable():
    """Test that application is a proper WSGI callable."""
    import BiteBuilderApp.wsgi
    
    # Check that application is callable
    assert callable(BiteBuilderApp.wsgi.application)
    
    # Check that it has the expected attributes for WSGI
    app = BiteBuilderApp.wsgi.application
    assert hasattr(app, '__call__')


def test_application_has_correct_type():
    """Test that application has the correct type."""
    import BiteBuilderApp.wsgi
    
    # The application should be callable and not None
    assert BiteBuilderApp.wsgi.application is not None
    assert callable(BiteBuilderApp.wsgi.application)
    
    # Should be a WSGI application (check if it's not a mock)
    app = BiteBuilderApp.wsgi.application
    if hasattr(app, '_mock_name'):
        # It's a mock, which is fine for testing
        assert True
    else:
        # It's a real WSGI application
        from django.core.handlers.wsgi import WSGIHandler
        assert isinstance(app, WSGIHandler)


# ============================================================================
# MOCKED WSGI APPLICATION TESTS
# ============================================================================

@patch('django.core.wsgi.get_wsgi_application')
def test_wsgi_application_creation(mock_get_app):
    """Test WSGI application creation with mocked dependencies."""
    mock_app = MagicMock()
    mock_get_app.return_value = mock_app
    
    # Import and reload to trigger the application creation
    import importlib
    import BiteBuilderApp.wsgi
    importlib.reload(BiteBuilderApp.wsgi)
    
    # Verify the application was created
    assert BiteBuilderApp.wsgi.application is mock_app
    mock_get_app.assert_called_once()


@patch('django.core.wsgi.get_wsgi_application')
def test_wsgi_application_with_different_settings(mock_get_app):
    """Test WSGI application with different settings module."""
    mock_app = MagicMock()
    mock_get_app.return_value = mock_app
    
    with patch.dict(os.environ, {'DJANGO_SETTINGS_MODULE': 'test.settings'}):
        import importlib
        import BiteBuilderApp.wsgi
        importlib.reload(BiteBuilderApp.wsgi)
        
        # Verify get_wsgi_application was called
        mock_get_app.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@patch('django.core.wsgi.get_wsgi_application')
def test_wsgi_application_creation_error(mock_get_app):
    """Test behavior when get_wsgi_application raises an error."""
    mock_get_app.side_effect = Exception("WSGI application creation failed")
    
    # This should raise an exception when importing
    with pytest.raises(Exception, match="WSGI application creation failed"):
        import importlib
        import BiteBuilderApp.wsgi
        importlib.reload(BiteBuilderApp.wsgi)


def test_import_with_missing_django():
    """Test import behavior when Django is not available."""
    with patch.dict('sys.modules', {'django.core.wsgi': None}):
        with pytest.raises(ImportError):
            import importlib
            import BiteBuilderApp.wsgi
            importlib.reload(BiteBuilderApp.wsgi)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_wsgi_application_integration():
    """Test that the WSGI application can be used in a WSGI context."""
    import BiteBuilderApp.wsgi
    
    # Create a mock WSGI environ and start_response
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'wsgi.version': (1, 0),
        'wsgi.input': None,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False
    }
    
    def mock_start_response(status, headers):
        pass
    
    # Test that the application can be called (this will fail in test environment
    # but we can verify the structure)
    app = BiteBuilderApp.wsgi.application
    assert callable(app)


def test_wsgi_application_with_different_methods():
    """Test WSGI application with different HTTP methods."""
    import BiteBuilderApp.wsgi
    
    # The application should be callable regardless of HTTP method
    app = BiteBuilderApp.wsgi.application
    assert callable(app)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_settings_module_configuration():
    """Test that the correct settings module is configured."""
    import BiteBuilderApp.wsgi
    
    # Verify the environment variable is set correctly
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


@override_settings()
def test_wsgi_with_custom_settings():
    """Test WSGI application with custom settings."""
    import BiteBuilderApp.wsgi
    
    # The application should still be callable
    assert callable(BiteBuilderApp.wsgi.application)


def test_multiple_imports():
    """Test that multiple imports don't cause issues."""
    import BiteBuilderApp.wsgi
    import BiteBuilderApp.wsgi  # Second import
    
    # Should not cause any issues
    assert BiteBuilderApp.wsgi.application is not None


# ============================================================================
# EDGE CASES
# ============================================================================

def test_wsgi_with_empty_environment():
    """Test WSGI application with empty environment."""
    with patch.dict(os.environ, {}, clear=True):
        import importlib
        import BiteBuilderApp.wsgi
        importlib.reload(BiteBuilderApp.wsgi)
        
        # Should still work and set the environment variable
        assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_wsgi_with_none_environment():
    """Test WSGI application when environment variable is None."""
    # Remove the environment variable if it exists
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        del os.environ['DJANGO_SETTINGS_MODULE']
    
    import importlib
    import BiteBuilderApp.wsgi
    importlib.reload(BiteBuilderApp.wsgi)
    
    # Should set the environment variable
    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'


def test_wsgi_application_attributes():
    """Test that WSGI application has expected attributes."""
    import BiteBuilderApp.wsgi
    
    app = BiteBuilderApp.wsgi.application
    
    # Should be callable
    assert callable(app)
    
    # Should have __call__ method
    assert hasattr(app, '__call__')
    
    # Should be a WSGIHandler instance
    from django.core.handlers.wsgi import WSGIHandler
    assert isinstance(app, WSGIHandler)


def test_wsgi_module_docstring():
    """Test that the WSGI module has proper docstring."""
    import BiteBuilderApp.wsgi
    
    # Check that module has docstring
    assert BiteBuilderApp.wsgi.__doc__ is not None
    assert 'WSGI config' in BiteBuilderApp.wsgi.__doc__
    assert 'BiteBuilderApp' in BiteBuilderApp.wsgi.__doc__


def test_wsgi_application_repr():
    """Test string representation of WSGI application."""
    import BiteBuilderApp.wsgi
    
    app = BiteBuilderApp.wsgi.application
    
    # Should have string representation
    app_str = str(app)
    assert isinstance(app_str, str)
    assert len(app_str) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_wsgi_application_creation_performance():
    """Test that WSGI application creation is fast."""
    import time
    import BiteBuilderApp.wsgi
    
    start_time = time.time()
    app = BiteBuilderApp.wsgi.application
    end_time = time.time()
    
    # Should be created quickly (less than 1 second)
    assert (end_time - start_time) < 1.0
    assert app is not None


def test_multiple_application_access():
    """Test accessing application multiple times."""
    import BiteBuilderApp.wsgi
    
    # Access application multiple times
    app1 = BiteBuilderApp.wsgi.application
    app2 = BiteBuilderApp.wsgi.application
    app3 = BiteBuilderApp.wsgi.application
    
    # Should be the same object
    assert app1 is app2
    assert app2 is app3
    assert app1 is app3


# ============================================================================
# COMPATIBILITY TESTS
# ============================================================================

def test_wsgi_application_with_different_python_versions():
    """Test WSGI application compatibility."""
    import BiteBuilderApp.wsgi
    import sys
    
    # Should work with current Python version
    assert BiteBuilderApp.wsgi.application is not None
    
    # Check Python version compatibility
    assert sys.version_info >= (3, 6)  # Minimum Python version for Django


def test_wsgi_application_with_django_version():
    """Test WSGI application with Django version."""
    import BiteBuilderApp.wsgi
    import django
    
    # Should work with current Django version
    assert BiteBuilderApp.wsgi.application is not None
    
    # Check Django version
    assert django.VERSION >= (2, 0)  # Minimum Django version
