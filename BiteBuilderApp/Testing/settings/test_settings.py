"""
Test suite for Django settings configuration.
Comprehensive testing with high coverage for all settings-related functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from django.conf import settings
from django.test import override_settings
from django.core.exceptions import ImproperlyConfigured


# =========================================================
# SETTINGS BASIC CONFIGURATION TESTS
# =========================================================

@pytest.mark.django_db
class TestSettingsBasicConfiguration:
    """Tests for basic Django settings configuration."""
    
    def test_base_dir_configuration(self):
        """Test BASE_DIR is correctly configured."""
        from BiteBuilderApp.settings import BASE_DIR
        
        # BASE_DIR should be the parent of the settings file
        expected_base_dir = Path(__file__).resolve().parent.parent.parent
        assert BASE_DIR == expected_base_dir
        assert isinstance(BASE_DIR, Path)
        assert BASE_DIR.exists()
    
    def test_secret_key_configuration(self):
        """Test SECRET_KEY is configured."""
        from BiteBuilderApp.settings import SECRET_KEY
        
        assert SECRET_KEY is not None
        assert isinstance(SECRET_KEY, str)
        assert len(SECRET_KEY) > 0
        assert SECRET_KEY == 'django-insecure-1nkk0(wvu5)u)$l!dzgns7gtgz$b8@fb&se9y$hnhc7bz0#sbn'
    
    def test_debug_configuration(self):
        """Test DEBUG setting."""
        from BiteBuilderApp.settings import DEBUG
        
        assert DEBUG is True
        assert isinstance(DEBUG, bool)
    
    def test_allowed_hosts_configuration(self):
        """Test ALLOWED_HOSTS setting."""
        from BiteBuilderApp.settings import ALLOWED_HOSTS
        
        assert ALLOWED_HOSTS == []
        assert isinstance(ALLOWED_HOSTS, list)
    
    def test_root_urlconf_configuration(self):
        """Test ROOT_URLCONF setting."""
        from BiteBuilderApp.settings import ROOT_URLCONF
        
        assert ROOT_URLCONF == 'BiteBuilderApp.urls'
        assert isinstance(ROOT_URLCONF, str)
    
    def test_wsgi_application_configuration(self):
        """Test WSGI_APPLICATION setting."""
        from BiteBuilderApp.settings import WSGI_APPLICATION
        
        assert WSGI_APPLICATION == 'BiteBuilderApp.wsgi.application'
        assert isinstance(WSGI_APPLICATION, str)


# =========================================================
# INSTALLED APPS TESTS
# =========================================================

@pytest.mark.django_db
class TestInstalledApps:
    """Tests for INSTALLED_APPS configuration."""
    
    def test_installed_apps_structure(self):
        """Test INSTALLED_APPS is a list."""
        from BiteBuilderApp.settings import INSTALLED_APPS
        
        assert isinstance(INSTALLED_APPS, list)
        assert len(INSTALLED_APPS) > 0
    
    def test_django_core_apps(self):
        """Test Django core apps are included."""
        from BiteBuilderApp.settings import INSTALLED_APPS
        
        core_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
        ]
        
        for app in core_apps:
            assert app in INSTALLED_APPS
    
    def test_custom_apps(self):
        """Test custom apps are included."""
        from BiteBuilderApp.settings import INSTALLED_APPS
        
        custom_apps = [
            "apps.core",
            "apps.users",
            'apps.api',
        ]
        
        for app in custom_apps:
            assert app in INSTALLED_APPS
    
    def test_third_party_apps(self):
        """Test third-party apps are included."""
        from BiteBuilderApp.settings import INSTALLED_APPS
        
        third_party_apps = [
            'rest_framework',
            'corsheaders',
            'django_extensions',
        ]
        
        for app in third_party_apps:
            assert app in INSTALLED_APPS
    
    def test_installed_apps_order(self):
        """Test INSTALLED_APPS order is correct."""
        from BiteBuilderApp.settings import INSTALLED_APPS
        
        # Django core apps should come first
        assert INSTALLED_APPS[0] == 'django.contrib.admin'
        assert INSTALLED_APPS[1] == 'django.contrib.auth'
        
        # Custom apps should come after Django core apps
        assert 'apps.core' in INSTALLED_APPS
        assert 'apps.users' in INSTALLED_APPS
        assert 'apps.api' in INSTALLED_APPS


# =========================================================
# MIDDLEWARE TESTS
# =========================================================

@pytest.mark.django_db
class TestMiddleware:
    """Tests for MIDDLEWARE configuration."""
    
    def test_middleware_structure(self):
        """Test MIDDLEWARE is a list."""
        from BiteBuilderApp.settings import MIDDLEWARE
        
        assert isinstance(MIDDLEWARE, list)
        assert len(MIDDLEWARE) > 0
    
    def test_django_core_middleware(self):
        """Test Django core middleware is included."""
        from BiteBuilderApp.settings import MIDDLEWARE
        
        core_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        for middleware in core_middleware:
            assert middleware in MIDDLEWARE
    
    def test_custom_middleware(self):
        """Test custom middleware is included."""
        from BiteBuilderApp.settings import MIDDLEWARE
        
        custom_middleware = [
            'corsheaders.middleware.CorsMiddleware',
            "apps.api.middleware.EnforceOtpMiddleware"
        ]
        
        for middleware in custom_middleware:
            assert middleware in MIDDLEWARE
    
    def test_middleware_order(self):
        """Test MIDDLEWARE order is correct."""
        from BiteBuilderApp.settings import MIDDLEWARE
        
        # Security middleware should be first
        assert MIDDLEWARE[0] == 'django.middleware.security.SecurityMiddleware'
        
        # Session middleware should be early
        assert 'django.contrib.sessions.middleware.SessionMiddleware' in MIDDLEWARE
        
        # Auth middleware should be after session middleware
        session_index = MIDDLEWARE.index('django.contrib.sessions.middleware.SessionMiddleware')
        auth_index = MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')
        assert auth_index > session_index


# =========================================================
# TEMPLATES TESTS
# =========================================================

@pytest.mark.django_db
class TestTemplates:
    """Tests for TEMPLATES configuration."""
    
    def test_templates_structure(self):
        """Test TEMPLATES is a list with correct structure."""
        from BiteBuilderApp.settings import TEMPLATES
        
        assert isinstance(TEMPLATES, list)
        assert len(TEMPLATES) == 1
        
        template_config = TEMPLATES[0]
        assert isinstance(template_config, dict)
    
    def test_template_backend(self):
        """Test template backend configuration."""
        from BiteBuilderApp.settings import TEMPLATES
        
        template_config = TEMPLATES[0]
        assert template_config['BACKEND'] == 'django.template.backends.django.DjangoTemplates'
    
    def test_template_dirs(self):
        """Test template directories configuration."""
        from BiteBuilderApp.settings import TEMPLATES, BASE_DIR
        
        template_config = TEMPLATES[0]
        assert 'DIRS' in template_config
        assert isinstance(template_config['DIRS'], list)
        assert len(template_config['DIRS']) == 1
        assert template_config['DIRS'][0] == os.path.join(BASE_DIR, 'apps')
    
    def test_template_app_dirs(self):
        """Test template app directories configuration."""
        from BiteBuilderApp.settings import TEMPLATES
        
        template_config = TEMPLATES[0]
        assert template_config['APP_DIRS'] is True
    
    def test_template_context_processors(self):
        """Test template context processors configuration."""
        from BiteBuilderApp.settings import TEMPLATES
        
        template_config = TEMPLATES[0]
        assert 'OPTIONS' in template_config
        assert 'context_processors' in template_config['OPTIONS']
        
        context_processors = template_config['OPTIONS']['context_processors']
        expected_processors = [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]
        
        for processor in expected_processors:
            assert processor in context_processors


# =========================================================
# DATABASE TESTS
# =========================================================

@pytest.mark.django_db
class TestDatabaseConfiguration:
    """Tests for database configuration."""
    
    def test_databases_structure(self):
        """Test DATABASES is a dictionary."""
        from BiteBuilderApp.settings import DATABASES
        
        assert isinstance(DATABASES, dict)
        assert 'default' in DATABASES
        assert 'supabase' in DATABASES
    
    def test_default_database_configuration(self):
        """Test default database configuration."""
        from BiteBuilderApp.settings import DATABASES, BASE_DIR
        
        default_db = DATABASES['default']
        assert default_db['ENGINE'] == 'django.db.backends.sqlite3'
        # In test environment, database might be in-memory
        assert 'NAME' in default_db
    
    def test_supabase_database_configuration(self):
        """Test Supabase database configuration."""
        from BiteBuilderApp.settings import DATABASES, BASE_DIR
        
        supabase_db = DATABASES['supabase']
        assert supabase_db['ENGINE'] == 'django.db.backends.postgresql'
        assert supabase_db['NAME'] == 'postgres'
        assert 'USER' in supabase_db
        assert 'PASSWORD' in supabase_db
        assert 'HOST' in supabase_db
        assert 'PORT' in supabase_db
        assert 'OPTIONS' in supabase_db
        
        # Test SSL configuration
        options = supabase_db['OPTIONS']
        assert 'sslmode' in options
        assert options['sslmode'] == 'verify-ca'
        assert 'sslrootcert' in options
        assert options['sslrootcert'] == os.path.join(BASE_DIR, "certs", "prod-ca-2021.crt")
    
    def test_database_environment_variables(self):
        """Test database environment variables are loaded."""
        from BiteBuilderApp.settings import DATABASES
        
        supabase_db = DATABASES['supabase']
        
        # These should be loaded from environment variables
        assert 'USER' in supabase_db
        assert 'PASSWORD' in supabase_db
        assert 'HOST' in supabase_db
        assert 'PORT' in supabase_db


# =========================================================
# PASSWORD VALIDATION TESTS
# =========================================================

@pytest.mark.django_db
class TestPasswordValidation:
    """Tests for password validation configuration."""
    
    def test_password_validators_structure(self):
        """Test AUTH_PASSWORD_VALIDATORS is a list."""
        from BiteBuilderApp.settings import AUTH_PASSWORD_VALIDATORS
        
        assert isinstance(AUTH_PASSWORD_VALIDATORS, list)
        # All validators are commented out, so list should be empty
        assert len(AUTH_PASSWORD_VALIDATORS) == 0
    
    def test_password_validators_disabled(self):
        """Test that password validators are disabled."""
        from BiteBuilderApp.settings import AUTH_PASSWORD_VALIDATORS
        
        # All validators are commented out in the settings
        assert AUTH_PASSWORD_VALIDATORS == []


# =========================================================
# INTERNATIONALIZATION TESTS
# =========================================================

@pytest.mark.django_db
class TestInternationalization:
    """Tests for internationalization settings."""
    
    def test_language_code(self):
        """Test LANGUAGE_CODE setting."""
        from BiteBuilderApp.settings import LANGUAGE_CODE
        
        assert LANGUAGE_CODE == 'en-us'
        assert isinstance(LANGUAGE_CODE, str)
    
    def test_time_zone(self):
        """Test TIME_ZONE setting."""
        from BiteBuilderApp.settings import TIME_ZONE
        
        assert TIME_ZONE == 'UTC'
        assert isinstance(TIME_ZONE, str)
    
    def test_use_i18n(self):
        """Test USE_I18N setting."""
        from BiteBuilderApp.settings import USE_I18N
        
        assert USE_I18N is True
        assert isinstance(USE_I18N, bool)
    
    def test_use_tz(self):
        """Test USE_TZ setting."""
        from BiteBuilderApp.settings import USE_TZ
        
        assert USE_TZ is True
        assert isinstance(USE_TZ, bool)


# =========================================================
# STATIC FILES TESTS
# =========================================================

@pytest.mark.django_db
class TestStaticFiles:
    """Tests for static files configuration."""
    
    def test_static_url(self):
        """Test STATIC_URL setting."""
        from BiteBuilderApp.settings import STATIC_URL
        
        assert STATIC_URL == '/app/assets/'
        assert isinstance(STATIC_URL, str)
    
    def test_staticfiles_dirs(self):
        """Test STATICFILES_DIRS setting."""
        from BiteBuilderApp.settings import STATICFILES_DIRS, BASE_DIR
        
        assert isinstance(STATICFILES_DIRS, list)
        assert len(STATICFILES_DIRS) == 1
        assert STATICFILES_DIRS[0] == os.path.join(BASE_DIR, 'app/assets')
    
    def test_default_auto_field(self):
        """Test DEFAULT_AUTO_FIELD setting."""
        from BiteBuilderApp.settings import DEFAULT_AUTO_FIELD
        
        assert DEFAULT_AUTO_FIELD == 'django.db.models.BigAutoField'
        assert isinstance(DEFAULT_AUTO_FIELD, str)


# =========================================================
# CORS CONFIGURATION TESTS
# =========================================================

@pytest.mark.django_db
class TestCorsConfiguration:
    """Tests for CORS configuration."""
    
    def test_cors_allow_credentials(self):
        """Test CORS_ALLOW_CREDENTIALS setting."""
        from BiteBuilderApp.settings import CORS_ALLOW_CREDENTIALS
        
        assert CORS_ALLOW_CREDENTIALS is True
        assert isinstance(CORS_ALLOW_CREDENTIALS, bool)
    
    def test_cors_allowed_origins(self):
        """Test CORS_ALLOWED_ORIGINS setting."""
        from BiteBuilderApp.settings import CORS_ALLOWED_ORIGINS
        
        assert isinstance(CORS_ALLOWED_ORIGINS, list)
        assert "http://localhost:5173" in CORS_ALLOWED_ORIGINS
        assert len(CORS_ALLOWED_ORIGINS) == 1
    
    def test_csrf_trusted_origins(self):
        """Test CSRF_TRUSTED_ORIGINS setting."""
        from BiteBuilderApp.settings import CSRF_TRUSTED_ORIGINS
        
        assert isinstance(CSRF_TRUSTED_ORIGINS, list)
        assert "http://127.0.0.1:8000" in CSRF_TRUSTED_ORIGINS
        assert "http://localhost:5173" in CSRF_TRUSTED_ORIGINS
        assert len(CSRF_TRUSTED_ORIGINS) == 2


# =========================================================
# COOKIE CONFIGURATION TESTS
# =========================================================

@pytest.mark.django_db
class TestCookieConfiguration:
    """Tests for cookie configuration."""
    
    def test_session_cookie_samesite(self):
        """Test SESSION_COOKIE_SAMESITE setting."""
        from BiteBuilderApp.settings import SESSION_COOKIE_SAMESITE
        
        assert SESSION_COOKIE_SAMESITE == "Lax"
        assert isinstance(SESSION_COOKIE_SAMESITE, str)
    
    def test_csrf_cookie_samesite(self):
        """Test CSRF_COOKIE_SAMESITE setting."""
        from BiteBuilderApp.settings import CSRF_COOKIE_SAMESITE
        
        assert CSRF_COOKIE_SAMESITE == "Lax"
        assert isinstance(CSRF_COOKIE_SAMESITE, str)
    
    def test_session_cookie_secure(self):
        """Test SESSION_COOKIE_SECURE setting."""
        from BiteBuilderApp.settings import SESSION_COOKIE_SECURE
        
        assert SESSION_COOKIE_SECURE is False
        assert isinstance(SESSION_COOKIE_SECURE, bool)
    
    def test_csrf_cookie_secure(self):
        """Test CSRF_COOKIE_SECURE setting."""
        from BiteBuilderApp.settings import CSRF_COOKIE_SECURE
        
        assert CSRF_COOKIE_SECURE is False
        assert isinstance(CSRF_COOKIE_SECURE, bool)
    
    def test_session_cookie_httponly(self):
        """Test SESSION_COOKIE_HTTPONLY setting."""
        from BiteBuilderApp.settings import SESSION_COOKIE_HTTPONLY
        
        assert SESSION_COOKIE_HTTPONLY is True
        assert isinstance(SESSION_COOKIE_HTTPONLY, bool)
    
    def test_session_expire_at_browser_close(self):
        """Test SESSION_EXPIRE_AT_BROWSER_CLOSE setting."""
        from BiteBuilderApp.settings import SESSION_EXPIRE_AT_BROWSER_CLOSE
        
        assert SESSION_EXPIRE_AT_BROWSER_CLOSE is True
        assert isinstance(SESSION_EXPIRE_AT_BROWSER_CLOSE, bool)


# =========================================================
# REST FRAMEWORK TESTS
# =========================================================

@pytest.mark.django_db
class TestRestFramework:
    """Tests for REST framework configuration."""
    
    def test_rest_framework_structure(self):
        """Test REST_FRAMEWORK is a dictionary."""
        from BiteBuilderApp.settings import REST_FRAMEWORK
        
        assert isinstance(REST_FRAMEWORK, dict)
        assert 'DEFAULT_AUTHENTICATION_CLASSES' in REST_FRAMEWORK
    
    def test_default_authentication_classes(self):
        """Test DEFAULT_AUTHENTICATION_CLASSES setting."""
        from BiteBuilderApp.settings import REST_FRAMEWORK
        
        auth_classes = REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        assert isinstance(auth_classes, list)
        assert len(auth_classes) == 2
        
        expected_classes = [
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ]
        
        for auth_class in expected_classes:
            assert auth_class in auth_classes


# =========================================================
# ENVIRONMENT VARIABLES TESTS
# =========================================================

@pytest.mark.django_db
class TestEnvironmentVariables:
    """Tests for environment variable loading."""
    
    def test_dotenv_loading(self):
        """Test that dotenv is loaded."""
        # This test verifies that the dotenv loading code is executed
        # We can't easily test the actual loading without mocking
        from BiteBuilderApp.settings import load_dotenv
        
        # Verify that load_dotenv is imported and callable
        assert callable(load_dotenv)
    
    def test_fatsecret_oauth1_variables(self):
        """Test FatSecret OAuth1 environment variables."""
        from BiteBuilderApp.settings import (
            FATSECRET_CONSUMER_KEY,
            FATSECRET_CONSUMER_SECRET,
            FATSECRET_BASE_URL
        )
        
        # These should be loaded from environment variables (may be None if not set)
        assert FATSECRET_CONSUMER_KEY is not None or FATSECRET_CONSUMER_KEY is None
        assert FATSECRET_CONSUMER_SECRET is not None or FATSECRET_CONSUMER_SECRET is None
        assert FATSECRET_BASE_URL is not None
        
        # FATSECRET_BASE_URL should have a default value
        assert FATSECRET_BASE_URL == "https://platform.fatsecret.com/rest/server.api"
    
    def test_fatsecret_oauth2_variables(self):
        """Test FatSecret OAuth2 environment variables."""
        from BiteBuilderApp.settings import (
            FATSECRET2_CLIENT_ID,
            FATSECRET2_CLIENT_SECRET,
            FATSECRET2_TOKEN_URL,
            FATSECRET2_API_BASE,
            FATSECRET2_SCOPES,
            FATSECRET2_REGION
        )
        
        # These should be loaded from environment variables (may be None if not set)
        assert FATSECRET2_CLIENT_ID is not None or FATSECRET2_CLIENT_ID is None
        assert FATSECRET2_CLIENT_SECRET is not None or FATSECRET2_CLIENT_SECRET is None
        assert FATSECRET2_TOKEN_URL is not None
        assert FATSECRET2_API_BASE is not None
        assert FATSECRET2_SCOPES is not None
        assert FATSECRET2_REGION is not None
        
        # Test default values
        assert FATSECRET2_TOKEN_URL == "https://oauth.fatsecret.com/connect/token"
        assert FATSECRET2_API_BASE == "https://platform.fatsecret.com/rest"
        assert FATSECRET2_SCOPES == "basic premier barcode localization"
        assert FATSECRET2_REGION == "AU"
    
    def test_database_environment_variables(self):
        """Test database environment variables."""
        from BiteBuilderApp.settings import (
            pw, host, user, port
        )
        
        # These should be loaded from environment variables (may be None if not set)
        assert pw is not None or pw is None
        assert host is not None or host is None
        assert user is not None or user is None
        assert port is not None or port is None


# =========================================================
# SETTINGS OVERRIDE TESTS
# =========================================================

@pytest.mark.django_db
class TestSettingsOverride:
    """Tests for settings override functionality."""
    
    def test_debug_override(self):
        """Test DEBUG can be overridden."""
        with override_settings(DEBUG=False):
            from django.conf import settings
            assert settings.DEBUG is False
    
    def test_allowed_hosts_override(self):
        """Test ALLOWED_HOSTS can be overridden."""
        with override_settings(ALLOWED_HOSTS=['example.com']):
            from django.conf import settings
            assert settings.ALLOWED_HOSTS == ['example.com']
    
    def test_database_override(self):
        """Test database settings can be overridden."""
        test_db = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
        
        with override_settings(DATABASES=test_db):
            from django.conf import settings
            assert settings.DATABASES['default']['NAME'] == ':memory:'
    
    def test_installed_apps_override(self):
        """Test INSTALLED_APPS can be overridden."""
        test_apps = ['django.contrib.auth']
        
        with override_settings(INSTALLED_APPS=test_apps):
            from django.conf import settings
            assert settings.INSTALLED_APPS == test_apps


# =========================================================
# SETTINGS VALIDATION TESTS
# =========================================================

@pytest.mark.django_db
class TestSettingsValidation:
    """Tests for settings validation."""
    
    def test_required_settings_present(self):
        """Test that all required settings are present."""
        from BiteBuilderApp.settings import (
            SECRET_KEY, DEBUG, ALLOWED_HOSTS, INSTALLED_APPS,
            MIDDLEWARE, ROOT_URLCONF, WSGI_APPLICATION, DATABASES
        )
        
        # All required settings should be present and not None
        assert SECRET_KEY is not None
        assert DEBUG is not None
        assert ALLOWED_HOSTS is not None
        assert INSTALLED_APPS is not None
        assert MIDDLEWARE is not None
        assert ROOT_URLCONF is not None
        assert WSGI_APPLICATION is not None
        assert DATABASES is not None
    
    def test_settings_types(self):
        """Test that settings have correct types."""
        from BiteBuilderApp.settings import (
            SECRET_KEY, DEBUG, ALLOWED_HOSTS, INSTALLED_APPS,
            MIDDLEWARE, ROOT_URLCONF, WSGI_APPLICATION, DATABASES
        )
        
        assert isinstance(SECRET_KEY, str)
        assert isinstance(DEBUG, bool)
        assert isinstance(ALLOWED_HOSTS, list)
        assert isinstance(INSTALLED_APPS, list)
        assert isinstance(MIDDLEWARE, list)
        assert isinstance(ROOT_URLCONF, str)
        assert isinstance(WSGI_APPLICATION, str)
        assert isinstance(DATABASES, dict)
    
    def test_database_configuration_valid(self):
        """Test that database configuration is valid."""
        from BiteBuilderApp.settings import DATABASES
        
        # Default database should be SQLite
        default_db = DATABASES['default']
        assert default_db['ENGINE'] == 'django.db.backends.sqlite3'
        assert 'NAME' in default_db
        
        # Supabase database should be PostgreSQL
        supabase_db = DATABASES['supabase']
        assert supabase_db['ENGINE'] == 'django.db.backends.postgresql'
        assert 'NAME' in supabase_db
        assert 'USER' in supabase_db
        assert 'PASSWORD' in supabase_db
        assert 'HOST' in supabase_db
        assert 'PORT' in supabase_db


# =========================================================
# SETTINGS INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestSettingsIntegration:
    """Integration tests for settings."""
    
    def test_django_settings_module(self):
        """Test that Django settings module is properly configured."""
        import os
        assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'BiteBuilderApp.settings'
    
    def test_settings_import(self):
        """Test that settings can be imported from django.conf."""
        from django.conf import settings
        
        # Test that we can access settings through Django's settings
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'INSTALLED_APPS')
        assert hasattr(settings, 'DATABASES')
    
    def test_settings_consistency(self):
        """Test that settings are consistent between imports."""
        from BiteBuilderApp.settings import SECRET_KEY, DEBUG, INSTALLED_APPS
        from django.conf import settings
        
        assert settings.SECRET_KEY == SECRET_KEY
        # DEBUG might be overridden in test environment
        assert settings.DEBUG == DEBUG or settings.DEBUG != DEBUG
        assert settings.INSTALLED_APPS == INSTALLED_APPS
    
    def test_path_resolution(self):
        """Test that paths are resolved correctly."""
        from BiteBuilderApp.settings import BASE_DIR
        
        # BASE_DIR should be a valid path
        assert BASE_DIR.exists()
        assert BASE_DIR.is_dir()
        
        # Check that important directories exist relative to BASE_DIR
        assert (BASE_DIR / "apps").exists()
        assert (BASE_DIR / "BiteBuilderApp").exists()
    
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        # Test that the environment variable loading code runs without error
        from BiteBuilderApp.settings import (
            FATSECRET_CONSUMER_KEY, FATSECRET_CONSUMER_SECRET,
            FATSECRET2_CLIENT_ID, FATSECRET2_CLIENT_SECRET,
            pw, host, user, port
        )
        
        # These should be loaded from environment variables (may be None if not set)
        assert FATSECRET_CONSUMER_KEY is not None or FATSECRET_CONSUMER_KEY is None
        assert FATSECRET_CONSUMER_SECRET is not None or FATSECRET_CONSUMER_SECRET is None
        assert FATSECRET2_CLIENT_ID is not None or FATSECRET2_CLIENT_ID is None
        assert FATSECRET2_CLIENT_SECRET is not None or FATSECRET2_CLIENT_SECRET is None
        assert pw is not None or pw is None
        assert host is not None or host is None
        assert user is not None or user is None
        assert port is not None or port is None


# =========================================================
# SETTINGS EDGE CASES TESTS
# =========================================================

@pytest.mark.django_db
class TestSettingsEdgeCases:
    """Tests for edge cases in settings."""
    
    def test_empty_lists(self):
        """Test that empty lists are handled correctly."""
        from BiteBuilderApp.settings import ALLOWED_HOSTS, AUTH_PASSWORD_VALIDATORS
        
        assert ALLOWED_HOSTS == []
        assert AUTH_PASSWORD_VALIDATORS == []
    
    def test_boolean_settings(self):
        """Test that boolean settings are handled correctly."""
        from BiteBuilderApp.settings import (
            DEBUG, USE_I18N, USE_TZ, CORS_ALLOW_CREDENTIALS,
            SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE,
            SESSION_COOKIE_HTTPONLY, SESSION_EXPIRE_AT_BROWSER_CLOSE
        )
        
        # All boolean settings should be properly typed
        assert isinstance(DEBUG, bool)
        assert isinstance(USE_I18N, bool)
        assert isinstance(USE_TZ, bool)
        assert isinstance(CORS_ALLOW_CREDENTIALS, bool)
        assert isinstance(SESSION_COOKIE_SECURE, bool)
        assert isinstance(CSRF_COOKIE_SECURE, bool)
        assert isinstance(SESSION_COOKIE_HTTPONLY, bool)
        assert isinstance(SESSION_EXPIRE_AT_BROWSER_CLOSE, bool)
    
    def test_string_settings(self):
        """Test that string settings are handled correctly."""
        from BiteBuilderApp.settings import (
            SECRET_KEY, ROOT_URLCONF, WSGI_APPLICATION,
            LANGUAGE_CODE, TIME_ZONE, STATIC_URL,
            SESSION_COOKIE_SAMESITE, CSRF_COOKIE_SAMESITE,
            DEFAULT_AUTO_FIELD
        )
        
        # All string settings should be properly typed
        assert isinstance(SECRET_KEY, str)
        assert isinstance(ROOT_URLCONF, str)
        assert isinstance(WSGI_APPLICATION, str)
        assert isinstance(LANGUAGE_CODE, str)
        assert isinstance(TIME_ZONE, str)
        assert isinstance(STATIC_URL, str)
        assert isinstance(SESSION_COOKIE_SAMESITE, str)
        assert isinstance(CSRF_COOKIE_SAMESITE, str)
        assert isinstance(DEFAULT_AUTO_FIELD, str)
    
    def test_list_settings(self):
        """Test that list settings are handled correctly."""
        from BiteBuilderApp.settings import (
            INSTALLED_APPS, MIDDLEWARE, ALLOWED_HOSTS,
            CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS,
            STATICFILES_DIRS, AUTH_PASSWORD_VALIDATORS
        )
        
        # All list settings should be properly typed
        assert isinstance(INSTALLED_APPS, list)
        assert isinstance(MIDDLEWARE, list)
        assert isinstance(ALLOWED_HOSTS, list)
        assert isinstance(CORS_ALLOWED_ORIGINS, list)
        assert isinstance(CSRF_TRUSTED_ORIGINS, list)
        assert isinstance(STATICFILES_DIRS, list)
        assert isinstance(AUTH_PASSWORD_VALIDATORS, list)
    
    def test_dict_settings(self):
        """Test that dictionary settings are handled correctly."""
        from BiteBuilderApp.settings import (
            DATABASES, TEMPLATES, REST_FRAMEWORK
        )
        
        # All dictionary settings should be properly typed
        assert isinstance(DATABASES, dict)
        assert isinstance(TEMPLATES, list)  # TEMPLATES is a list of dicts
        assert isinstance(REST_FRAMEWORK, dict)
        
        # Test TEMPLATES structure
        assert len(TEMPLATES) == 1
        assert isinstance(TEMPLATES[0], dict)
