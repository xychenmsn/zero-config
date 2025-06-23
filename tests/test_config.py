import os
import tempfile
import pytest
import logging
from pathlib import Path
from unittest.mock import patch

from zero_config import setup_environment, get_config, is_initialized, get_initialization_info
from zero_config.config import (
    smart_convert,
    find_project_root,
    load_domain_env_file,
    _reset_for_testing,
)


class TestSmartConvert:
    """Test the smart_convert function."""
    
    def test_string_conversion(self):
        assert smart_convert("hello", "default") == "hello"
    
    def test_int_conversion(self):
        assert smart_convert("42", 0) == 42
        assert smart_convert("invalid", 0) == "invalid"  # fallback
    
    def test_float_conversion(self):
        assert smart_convert("3.14", 0.0) == 3.14
        assert smart_convert("invalid", 0.0) == "invalid"  # fallback
    
    def test_bool_conversion(self):
        assert smart_convert("true", False) == True
        assert smart_convert("True", False) == True
        assert smart_convert("1", False) == True
        assert smart_convert("yes", False) == True
        assert smart_convert("on", False) == True
        assert smart_convert("enabled", False) == True
        assert smart_convert("false", True) == False
        assert smart_convert("0", True) == False
        assert smart_convert("invalid", False) == False  # Invalid bool returns default

    def test_number_conversion(self):
        # Integer conversion
        assert smart_convert("42", 0) == 42
        assert smart_convert("-123", 0) == -123
        assert smart_convert("invalid", 0) == "invalid"  # Invalid int stays string

        # Float conversion
        assert smart_convert("3.14", 0.0) == 3.14
        assert smart_convert("-2.5", 0.0) == -2.5
        assert smart_convert("invalid", 0.0) == "invalid"  # Invalid float stays string
    
    def test_list_conversion(self):
        # JSON array format (only supported format)
        assert smart_convert('["a", "b", "c"]', []) == ["a", "b", "c"]
        assert smart_convert('["item1", "item2"]', []) == ["item1", "item2"]

        # Comma-separated strings are treated as single items (safe!)
        assert smart_convert("a,b,c", []) == ["a,b,c"]  # Single item with commas
        assert smart_convert("host1,host2,host3", []) == ["host1,host2,host3"]  # Database URL safe

        # Space-separated strings are treated as single items (safe!)
        assert smart_convert("hello world", []) == ["hello world"]  # Natural language safe

        # Single item
        assert smart_convert("single-item", []) == ["single-item"]

        # Empty string
        assert smart_convert("", []) == []
        assert smart_convert("   ", []) == []

        # Complex strings with commas are preserved
        assert smart_convert("postgresql://host1,host2,host3/db", []) == ["postgresql://host1,host2,host3/db"]
        assert smart_convert("Hello, welcome to our app!", []) == ["Hello, welcome to our app!"]


class TestProjectRoot:
    """Test project root detection."""
    
    def test_find_project_root_with_pyproject(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            # Create a pyproject.toml file
            (tmpdir_path / "pyproject.toml").touch()

            # Create a subdirectory
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Should find the root from subdirectory
            root = find_project_root(subdir)
            assert root.resolve() == tmpdir_path

    def test_find_project_root_with_env_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            # Create a .env file (since .env.zero_config is no longer a project root indicator)
            (tmpdir_path / ".env").touch()

            # Should find the root
            root = find_project_root(tmpdir_path)
            assert root.resolve() == tmpdir_path


class TestDomainEnvFile:
    """Test .env.zero_config file loading."""
    
    def test_load_domain_env_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_file = tmpdir_path / ".env.zero_config"
            
            # Create test env file
            env_content = """
# Comment line
openai_api_key=sk-test-key
temperature=0.7
log_calls=true
models=gpt-4,claude-3
"""
            env_file.write_text(env_content)
            
            # Load the file
            env_vars = load_domain_env_file(tmpdir_path)
            
            assert env_vars["openai_api_key"] == "sk-test-key"
            assert env_vars["temperature"] == "0.7"
            assert env_vars["log_calls"] == "true"
            assert env_vars["models"] == "gpt-4,claude-3"
    
    def test_load_nonexistent_env_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_vars = load_domain_env_file(tmpdir_path)
            assert env_vars == {}

    def test_domain_env_with_smart_conversion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_file = tmpdir_path / ".env.zero_config"

            # Create test env file with various types
            env_content = """
# Test configuration
temperature=0.7
max_tokens=2048
debug=true
models=["gpt-4", "claude-3"]
api_key=sk-test-key
"""
            env_file.write_text(env_content)

            # Test with default config for type conversion
            default_config = {
                'temperature': 0.0,  # float
                'max_tokens': 1024,  # int
                'debug': False,      # bool
                'models': ['gpt-4']  # list
            }

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test smart type conversion from .env file
                    assert config.get('temperature') == 0.7  # converted to float
                    assert config.get('max_tokens') == 2048  # converted to int
                    assert config.get('debug') == True       # converted to bool
                    assert config.get('models') == ['gpt-4', 'claude-3']  # converted to list
                    assert config.get('api_key') == 'sk-test-key'  # added as string


class TestConfiguration:
    """Test the main configuration functionality."""
    
    def test_defaults_loaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Clear environment variables that might interfere
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment()
                    config = get_config()

                    # Zero config starts with only project_root (automatically added)
                    expected = {'project_root': str(tmpdir_path)}
                    assert config.to_dict() == expected

                    # But can still access non-existent keys with defaults
                    assert config.get('nonexistent_key', 'default') == 'default'
    
    def test_environment_variable_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Test with default config that has typed values
                default_config = {
                    'temperature': 0.0,  # float
                    'max_tokens': 1024,  # int
                    'debug': False,      # bool
                    'models': ['gpt-4'],  # list
                    'openai_api_key': ''  # string (so env var can override)
                }

                with patch.dict(os.environ, {
                    'OPENAI_API_KEY': 'sk-test-key',
                    'TEMPERATURE': '0.8',
                    'MAX_TOKENS': '2048',
                    'DEBUG': 'true',
                    'MODELS': '["gpt-4", "claude-3"]'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test API key (has default, overridden by env var)
                    assert config.get('openai_api_key') == 'sk-test-key'

                    # Test smart type conversion based on defaults
                    assert config.get('temperature') == 0.8  # converted to float
                    assert config.get('max_tokens') == 2048  # converted to int
                    assert config.get('debug') == True       # converted to bool
                    assert config.get('models') == ['gpt-4', 'claude-3']  # converted to list
    
    def test_config_methods(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Provide default config with test_key so env var can override it
                default_config = {'test_key': 'default_value'}

                with patch.dict(os.environ, {'TEST_KEY': 'test_value'}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test __getitem__
                    assert config['test_key'] == 'test_value'

                    # Test __contains__
                    assert 'test_key' in config
                    assert 'nonexistent_key' not in config

                    # Test get with default
                    assert config.get('nonexistent_key', 'default_value') == 'default_value'

                    # Test to_dict
                    config_dict = config.to_dict()
                    assert isinstance(config_dict, dict)
                    assert 'test_key' in config_dict
    
    def test_path_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Reset state first
                _reset_for_testing()

                setup_environment()
                config = get_config()

                # Test data_path via dynamic path helper
                data_dir = config.data_path()
                assert data_dir == str(Path(tmpdir) / "data")

                data_file = config.data_path("test.db")
                assert data_file == str(Path(tmpdir) / "data" / "test.db")

                # Test logs_path via dynamic path helper
                logs_dir = config.logs_path()
                assert logs_dir == str(Path(tmpdir) / "logs")

                log_file = config.logs_path("app.log")
                assert log_file == str(Path(tmpdir) / "logs" / "app.log")

    def test_dynamic_path_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Reset state first
                _reset_for_testing()

                setup_environment()
                config = get_config()

                # Test dynamic path helpers
                cache_dir = config.cache_path()
                assert cache_dir == str(Path(tmpdir) / "cache")

                cache_file = config.cache_path("session.json")
                assert cache_file == str(Path(tmpdir) / "cache" / "session.json")

                # Test various dynamic paths
                assert config.temp_path() == str(Path(tmpdir) / "temp")
                assert config.models_path("gpt4.bin") == str(Path(tmpdir) / "models" / "gpt4.bin")
                assert config.uploads_path() == str(Path(tmpdir) / "uploads")
                assert config.static_path("style.css") == str(Path(tmpdir) / "static" / "style.css")

                # Test that non-path attributes raise AttributeError
                try:
                    config.invalid_attribute
                    assert False, "Should have raised AttributeError"
                except AttributeError:
                    pass

    def test_section_headers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Test with section headers in default config
                default_config = {
                    'llm.models': ['gpt-4'],
                    'llm.temperature': 0.0,
                    'database.host': 'localhost',
                    'database.port': 5432,
                    'simple_key': 'value'
                }

                with patch.dict(os.environ, {
                    'LLM__MODELS': '["gpt-4", "claude-3"]',
                    'LLM__TEMPERATURE': '0.7',
                    'DATABASE__HOST': 'remote.db.com',
                    'DATABASE__PORT': '3306',
                    'SIMPLE_KEY': 'overridden'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test section header environment variable conversion
                    assert config.get('llm.models') == ['gpt-4', 'claude-3']
                    assert config.get('llm.temperature') == 0.7
                    assert config.get('database.host') == 'remote.db.com'
                    assert config.get('database.port') == 3306  # converted to int
                    assert config.get('simple_key') == 'overridden'

    def test_section_access(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Test with section headers in default config
                default_config = {
                    'llm.models': ['gpt-4'],
                    'llm.temperature': 0.0,
                    'llm.max_tokens': 1024,
                    'database.host': 'localhost',
                    'database.port': 5432,
                    'database.ssl': True,
                    'simple_key': 'value',
                    'cache.enabled': True,
                    'cache.ttl': 3600
                }

                # Reset state first
                _reset_for_testing()

                setup_environment(default_config=default_config)
                config = get_config()

                # Test getting LLM section via config.get('llm')
                llm_config = config.get('llm')
                expected_llm = {
                    'models': ['gpt-4'],
                    'temperature': 0.0,
                    'max_tokens': 1024
                }
                assert llm_config == expected_llm

                # Test getting database section via config.get('database')
                db_config = config.get('database')
                expected_db = {
                    'host': 'localhost',
                    'port': 5432,
                    'ssl': True
                }
                assert db_config == expected_db

                # Test getting cache section via config.get('cache')
                cache_config = config.get('cache')
                expected_cache = {
                    'enabled': True,
                    'ttl': 3600
                }
                assert cache_config == expected_cache

                # Test getting non-existent section returns default
                empty_config = config.get('nonexistent')
                assert empty_config is None

                # Test with custom default
                empty_config = config.get('nonexistent', {})
                assert empty_config == {}

                # Test that simple keys are not included in sections
                simple_config = config.get('simple')
                assert simple_config is None  # 'simple_key' doesn't match 'simple.*'

    def test_edge_cases_and_safety(self):
        """Test edge cases and safety features of type conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                # Test with edge case values
                default_config = {
                    'database_url': '',
                    'welcome_message': '',
                    'api_endpoint': '',
                    'csv_data': '',
                    'models': [],
                    'port': 8000,
                    'temperature': 0.0,
                    'debug': False,
                }

                with patch.dict(os.environ, {
                    # Test comma-containing strings stay safe
                    'DATABASE_URL': 'postgresql://host1,host2,host3/db',
                    'WELCOME_MESSAGE': 'Hello, welcome to our app!',
                    'API_ENDPOINT': 'https://api.com/search?q=item1,item2&format=json',
                    'CSV_DATA': 'name,age,city',

                    # Test JSON lists work
                    'MODELS': '["gpt-4", "claude-3"]',

                    # Test number edge cases
                    'PORT': '3000',
                    'TEMPERATURE': '0.7',

                    # Test boolean edge cases
                    'DEBUG': 'enabled',
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Verify comma-containing strings are preserved
                    assert config.get('database_url') == 'postgresql://host1,host2,host3/db'
                    assert config.get('welcome_message') == 'Hello, welcome to our app!'
                    assert config.get('api_endpoint') == 'https://api.com/search?q=item1,item2&format=json'
                    assert config.get('csv_data') == 'name,age,city'

                    # Verify JSON lists work
                    assert config.get('models') == ['gpt-4', 'claude-3']

                    # Verify number conversions
                    assert config.get('port') == 3000
                    assert isinstance(config.get('port'), int)
                    assert config.get('temperature') == 0.7
                    assert isinstance(config.get('temperature'), float)

                    # Verify boolean conversion
                    assert config.get('debug') == True
                    assert isinstance(config.get('debug'), bool)

    def test_invalid_conversions_fallback(self):
        """Test that invalid conversions fall back gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                default_config = {
                    'port': 8000,
                    'temperature': 0.0,
                    'debug': False,
                }

                with patch.dict(os.environ, {
                    'PORT': 'not-a-number',
                    'TEMPERATURE': 'not-a-float',
                    'DEBUG': 'not-a-boolean',
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Invalid numbers should stay as strings
                    assert config.get('port') == 'not-a-number'
                    assert config.get('temperature') == 'not-a-float'

                    # Invalid booleans should default to False
                    assert config.get('debug') == False

    def test_project_root_in_config(self):
        """Test that project_root is always available in config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()  # Resolve symlinks for consistent comparison
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment()
                    config = get_config()

                    # project_root should always be in config
                    assert 'project_root' in config
                    assert config.get('project_root') == str(tmpdir_path)
                    assert config['project_root'] == str(tmpdir_path)

                    # project_root should be in to_dict()
                    config_dict = config.to_dict()
                    assert 'project_root' in config_dict
                    assert config_dict['project_root'] == str(tmpdir_path)

    def test_project_root_env_override(self):
        """Test that PROJECT_ROOT environment variable overrides auto-detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            custom_root = tmpdir_path / "custom_project_root"
            custom_root.mkdir()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'PROJECT_ROOT': str(custom_root)
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment()
                    config = get_config()

                    # Should use PROJECT_ROOT env var, not auto-detected
                    expected_root = str(custom_root.resolve())
                    assert config.get('project_root') == expected_root
                    assert config['project_root'] == expected_root

                    # Should be in to_dict()
                    config_dict = config.to_dict()
                    assert config_dict['project_root'] == expected_root

    def test_project_root_env_file_ignored(self):
        """Test that project_root in .env.zero_config is ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            env_file = tmpdir_path / ".env.zero_config"

            # Create .env file with project_root (should be ignored)
            env_content = """
project_root=/should/be/ignored
other_key=should_work
"""
            env_file.write_text(env_content)

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment()
                    config = get_config()

                    # project_root should be auto-detected, not from .env file
                    assert config.get('project_root') == str(tmpdir_path)

                    # other_key should work normally
                    assert config.get('other_key') == 'should_work'

    def test_custom_env_files(self):
        """Test loading custom env files via env_files parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            # Create custom env files
            env1 = tmpdir_path / "custom1.env"
            env1.write_text("key1=value1\nshared_key=from_env1")

            env2 = tmpdir_path / "custom2.env"
            env2.write_text("key2=value2\nshared_key=from_env2")

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Test single env file
                    setup_environment(env_files=env1)
                    config = get_config()

                    assert config.get('key1') == 'value1'
                    assert config.get('shared_key') == 'from_env1'
                    assert config.get('key2') is None

                    # Reset for next test
                    _reset_for_testing()

                    # Test multiple env files (later files override earlier ones)
                    setup_environment(env_files=[env1, env2])
                    config = get_config()

                    assert config.get('key1') == 'value1'
                    assert config.get('key2') == 'value2'
                    assert config.get('shared_key') == 'from_env2'  # env2 overrides env1


class TestInitializationProtection:
    """Test the initialization protection mechanism."""

    def test_multiple_setup_calls_protection(self):
        """Test that subsequent setup_environment calls are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # First call should work
                    assert not is_initialized()
                    setup_environment(default_config={'key1': 'value1'})
                    assert is_initialized()

                    config = get_config()
                    assert config.get('key1') == 'value1'

                    # Second call should be ignored
                    setup_environment(default_config={'key2': 'value2'})

                    # Config should still have only the first setup
                    config = get_config()
                    assert config.get('key1') == 'value1'
                    assert config.get('key2') is None  # Should not be added

    def test_force_reinit_parameter(self):
        """Test that force_reinit=True allows re-initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # First call
                    setup_environment(default_config={'key1': 'value1'})
                    config = get_config()
                    assert config.get('key1') == 'value1'

                    # Second call with force_reinit=True should work
                    setup_environment(default_config={'key2': 'value2'}, force_reinit=True)

                    # Config should now have the new setup
                    config = get_config()
                    assert config.get('key1') is None  # Should be gone
                    assert config.get('key2') == 'value2'  # Should be added

    def test_initialization_info_tracking(self):
        """Test that initialization info is properly tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Before initialization
                    assert not is_initialized()
                    assert get_initialization_info() is None

                    # After initialization
                    setup_environment()
                    assert is_initialized()

                    init_info = get_initialization_info()
                    assert init_info is not None
                    assert 'test_config.py' in init_info  # Should contain this test file
                    assert ':' in init_info  # Should have line number

    def test_package_dependency_scenario(self):
        """Test the main use case: main project + package both using zero-config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Simulate main project initialization
                    main_config = {
                        'app_name': 'news_app',
                        'database.host': 'localhost',
                        'llm.api_key': 'main-key'
                    }
                    setup_environment(default_config=main_config)

                    # Verify main project config
                    config = get_config()
                    assert config.get('app_name') == 'news_app'
                    assert config.get('database.host') == 'localhost'
                    assert config.get('llm.api_key') == 'main-key'

                    # Simulate package (united_llm) trying to initialize
                    package_config = {
                        'llm.temperature': 0.7,
                        'llm.max_tokens': 2048,
                        'package_name': 'united_llm'
                    }
                    setup_environment(default_config=package_config)  # Should be ignored

                    # Config should still be from main project
                    config = get_config()
                    assert config.get('app_name') == 'news_app'  # Main project config preserved
                    assert config.get('database.host') == 'localhost'  # Main project config preserved
                    assert config.get('llm.api_key') == 'main-key'  # Main project config preserved

                    # Package-specific config should NOT be added
                    assert config.get('package_name') is None
                    assert config.get('llm.temperature') is None
                    assert config.get('llm.max_tokens') is None

                    # But package can still access the main project's config
                    llm_section = config.get('llm')
                    assert llm_section == {'api_key': 'main-key'}

    def test_logging_output(self, caplog):
        """Test that helpful logging messages are generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # First initialization should log success
                    with caplog.at_level(logging.INFO):
                        setup_environment(default_config={'key1': 'value1'})

                    assert "🚀 Environment setup complete" in caplog.text
                    assert "Initialized by:" in caplog.text

                    # Clear logs
                    caplog.clear()

                    # Second initialization should log that it's skipped
                    with caplog.at_level(logging.INFO):
                        setup_environment(default_config={'key2': 'value2'})

                    assert "Zero-config already initialized" in caplog.text
                    assert "Skipping re-initialization to prevent conflicts" in caplog.text

    def test_multiple_packages_scenario(self):
        """Test scenario with multiple packages trying to initialize."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Main project initializes
                    main_config = {
                        'app_name': 'main_app',
                        'llm.api_key': 'main-key',
                        'database.host': 'localhost'
                    }
                    setup_environment(default_config=main_config)

                    # First package tries to initialize
                    package1_config = {
                        'package1.name': 'united_llm',
                        'package1.version': '1.0.0',
                        'llm.temperature': 0.7  # Different from main
                    }
                    setup_environment(default_config=package1_config)  # Should be ignored

                    # Second package tries to initialize
                    package2_config = {
                        'package2.name': 'data_processor',
                        'package2.version': '2.0.0',
                        'database.timeout': 30  # Different from main
                    }
                    setup_environment(default_config=package2_config)  # Should be ignored

                    # Verify only main config is present
                    config = get_config()
                    assert config.get('app_name') == 'main_app'
                    assert config.get('llm.api_key') == 'main-key'
                    assert config.get('database.host') == 'localhost'

                    # Package configs should not be present
                    assert config.get('package1.name') is None
                    assert config.get('package2.name') is None
                    assert config.get('llm.temperature') is None
                    assert config.get('database.timeout') is None

    def test_force_reinit_with_different_project_root(self):
        """Test force re-initialization with different project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path1 = Path(tmpdir) / "project1"
            tmpdir_path2 = Path(tmpdir) / "project2"
            tmpdir_path1.mkdir()
            tmpdir_path2.mkdir()

            # First initialization
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path1):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment(default_config={'project': 'first'})
                    config = get_config()
                    assert config.get('project') == 'first'
                    assert config.get('project_root') == str(tmpdir_path1)

            # Force re-initialization with different project root
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path2):
                with patch.dict(os.environ, {}, clear=True):
                    setup_environment(
                        default_config={'project': 'second'},
                        force_reinit=True
                    )
                    config = get_config()
                    assert config.get('project') == 'second'
                    assert config.get('project_root') == str(tmpdir_path2)

    def test_initialization_info_format(self):
        """Test that initialization info has the expected format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    setup_environment()

                    init_info = get_initialization_info()
                    assert init_info is not None

                    # Should contain file path and line number
                    assert '.py:' in init_info
                    assert 'test_config.py' in init_info

                    # Should be a valid file:line format
                    parts = init_info.split(':')
                    assert len(parts) >= 2
                    assert parts[-1].isdigit()  # Line number should be numeric


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""

    def test_get_config_before_setup(self):
        """Test that get_config raises error before setup."""
        # Reset state first
        _reset_for_testing()

        with pytest.raises(RuntimeError, match="Configuration not initialized"):
            get_config()

    def test_is_initialized_before_setup(self):
        """Test is_initialized returns False before setup."""
        # Reset state first
        _reset_for_testing()

        assert not is_initialized()
        assert get_initialization_info() is None

    def test_force_reinit_false_with_existing_config(self):
        """Test that force_reinit=False doesn't override existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # First setup
                    setup_environment(default_config={'key': 'original'})
                    assert get_config().get('key') == 'original'

                    # Second setup with force_reinit=False (default)
                    setup_environment(default_config={'key': 'new'}, force_reinit=False)
                    assert get_config().get('key') == 'original'  # Should remain unchanged

    def test_empty_default_config(self):
        """Test setup with empty or None default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Test with None
                    setup_environment(default_config=None)
                    config = get_config()
                    assert 'project_root' in config.to_dict()  # Should have project_root

                    # Reset and test with empty dict
                    _reset_for_testing()
                    setup_environment(default_config={})
                    config = get_config()
                    assert 'project_root' in config.to_dict()  # Should have project_root


class TestMultiLevelConfiguration:
    """Test multi-level configuration support."""

    def test_multi_level_environment_variables(self):
        """Test that DATABASE__DEVELOPE__DB_URL becomes database.develope.db_url."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__DEVELOPE__DB_URL': 'postgresql://localhost:5432/dev',
                    'DATABASE__DEVELOPE__POOL_SIZE': '10',
                    'DATABASE__PRODUCTION__DB_URL': 'postgresql://prod.db.com:5432/prod',
                    'LLM__OPENAI__API_KEY': 'sk-test123',
                    'LLM__OPENAI__MODEL': 'gpt-4',
                    'LLM__ANTHROPIC__API_KEY': 'claude-key',
                    'SIMPLE_KEY': 'simple_value'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Setup with defaults for all environment variables we want to test
                    default_config = {
                        'database.develope.db_url': 'sqlite:///default.db',
                        'database.develope.pool_size': 5,  # int default
                        'database.production.db_url': 'sqlite:///prod.db',
                        'llm.openai.api_key': 'default-openai-key',
                        'llm.openai.model': 'gpt-3.5-turbo',
                        'llm.anthropic.api_key': 'default-anthropic-key',
                        'simple_key': 'default'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test multi-level access
                    assert config.get('database.develope.db_url') == 'postgresql://localhost:5432/dev'
                    assert config.get('database.develope.pool_size') == 10  # Should be converted to int
                    assert config.get('database.production.db_url') == 'postgresql://prod.db.com:5432/prod'
                    assert config.get('llm.openai.api_key') == 'sk-test123'
                    assert config.get('llm.openai.model') == 'gpt-4'
                    assert config.get('llm.anthropic.api_key') == 'claude-key'
                    assert config.get('simple_key') == 'simple_value'

                    # Test section access
                    database_section = config.get('database')
                    assert database_section == {
                        'develope': {
                            'db_url': 'postgresql://localhost:5432/dev',
                            'pool_size': 10
                        },
                        'production': {
                            'db_url': 'postgresql://prod.db.com:5432/prod'
                        }
                    }

                    llm_section = config.get('llm')
                    assert llm_section == {
                        'openai': {
                            'api_key': 'sk-test123',
                            'model': 'gpt-4'
                        },
                        'anthropic': {
                            'api_key': 'claude-key'
                        }
                    }

                    # Test subsection access
                    database_develope = config.get('database.develope')
                    assert database_develope == {
                        'db_url': 'postgresql://localhost:5432/dev',
                        'pool_size': 10
                    }

                    llm_openai = config.get('llm.openai')
                    assert llm_openai == {
                        'api_key': 'sk-test123',
                        'model': 'gpt-4'
                    }

    def test_multi_level_default_config(self):
        """Test that default config can be provided in both flat and nested formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Mix of flat and nested default config
                    default_config = {
                        'database.develope.db_url': 'sqlite:///dev.db',
                        'database.develope.pool_size': 5,
                        'llm': {
                            'openai': {
                                'api_key': 'default-key',
                                'model': 'gpt-3.5-turbo'
                            }
                        },
                        'simple_key': 'simple_value'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test that both formats work
                    assert config.get('database.develope.db_url') == 'sqlite:///dev.db'
                    assert config.get('database.develope.pool_size') == 5
                    assert config.get('llm.openai.api_key') == 'default-key'
                    assert config.get('llm.openai.model') == 'gpt-3.5-turbo'
                    assert config.get('simple_key') == 'simple_value'

                    # Test section access
                    database_section = config.get('database')
                    assert database_section == {
                        'develope': {
                            'db_url': 'sqlite:///dev.db',
                            'pool_size': 5
                        }
                    }

                    llm_section = config.get('llm')
                    assert llm_section == {
                        'openai': {
                            'api_key': 'default-key',
                            'model': 'gpt-3.5-turbo'
                        }
                    }

    def test_env_file_multi_level_support(self):
        """Test that .env files support multi-level configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            env_file = tmpdir_path / ".env.zero_config"

            # Create env file with multi-level keys
            env_content = """
# Database configuration
DATABASE__DEVELOPE__DB_URL=postgresql://localhost:5432/dev
DATABASE__DEVELOPE__POOL_SIZE=10
DATABASE__PRODUCTION__DB_URL=postgresql://prod.db.com:5432/prod

# LLM configuration
LLM__OPENAI__API_KEY=sk-env-key
LLM__OPENAI__MODEL=gpt-4
LLM__ANTHROPIC__API_KEY=claude-env-key

# Simple key
SIMPLE_KEY=env_value
"""
            env_file.write_text(env_content.strip())

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Setup with some defaults
                    default_config = {
                        'database.develope.pool_size': 5,  # int default
                        'simple_key': 'default'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test that env file values are loaded correctly
                    assert config.get('database.develope.db_url') == 'postgresql://localhost:5432/dev'
                    assert config.get('database.develope.pool_size') == 10  # Should be converted to int
                    assert config.get('database.production.db_url') == 'postgresql://prod.db.com:5432/prod'
                    assert config.get('llm.openai.api_key') == 'sk-env-key'
                    assert config.get('llm.openai.model') == 'gpt-4'
                    assert config.get('llm.anthropic.api_key') == 'claude-env-key'
                    assert config.get('simple_key') == 'env_value'


class TestEnvironmentVariableFiltering:
    """Test that OS environment variables are only loaded if they have defaults."""

    def test_os_env_vars_only_loaded_with_defaults(self):
        """Test that OS environment variables are only loaded if they exist in default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__URL': 'postgresql://localhost:5432/test',  # Has default
                    'DATABASE__POOL_SIZE': '10',  # Has default
                    'RANDOM_UNRELATED_VAR': 'should_not_be_loaded',  # No default
                    'ANOTHER_RANDOM_VAR': 'also_should_not_be_loaded',  # No default
                    'API_KEY': 'sk-test123'  # Has default
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Only provide defaults for some of the env vars
                    default_config = {
                        'database.url': 'sqlite:///default.db',
                        'database.pool_size': 5,
                        'api_key': 'default-key'
                        # Note: no defaults for RANDOM_UNRELATED_VAR or ANOTHER_RANDOM_VAR
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # These should be loaded (have defaults)
                    assert config.get('database.url') == 'postgresql://localhost:5432/test'
                    assert config.get('database.pool_size') == 10
                    assert config.get('api_key') == 'sk-test123'

                    # These should NOT be loaded (no defaults)
                    assert config.get('random_unrelated_var') is None
                    assert config.get('another_random_var') is None

                    # Verify they're not in the config at all
                    assert 'random_unrelated_var' not in config.to_flat_dict()
                    assert 'another_random_var' not in config.to_flat_dict()

    def test_env_files_load_all_variables(self):
        """Test that env files load ALL variables regardless of defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            env_file = tmpdir_path / ".env.zero_config"

            # Create env file with variables that don't have defaults
            env_content = """
DATABASE__URL=postgresql://localhost:5432/env
DATABASE__POOL_SIZE=15
NEW_VAR_FROM_ENV=should_be_loaded
ANOTHER_NEW_VAR=also_should_be_loaded
API_KEY=sk-env-key
"""
            env_file.write_text(env_content.strip())

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Only provide defaults for some variables
                    default_config = {
                        'database.url': 'sqlite:///default.db',
                        'api_key': 'default-key'
                        # Note: no defaults for pool_size or the new vars
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # These should be loaded from env file (have defaults)
                    assert config.get('database.url') == 'postgresql://localhost:5432/env'
                    assert config.get('api_key') == 'sk-env-key'

                    # These should ALSO be loaded from env file (even without defaults)
                    assert config.get('database.pool_size') == '15'  # String since no default type
                    assert config.get('new_var_from_env') == 'should_be_loaded'
                    assert config.get('another_new_var') == 'also_should_be_loaded'


class TestAllRequirements:
    """Test all 5 requirements comprehensively."""

    def test_all_requirements_comprehensive(self):
        """Test all 5 requirements in one comprehensive test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            env_file = tmpdir_path / ".env.zero_config"

            # Create env file with multi-level keys
            env_content = """
# These should be loaded (from env file)
DATABASE__MAIN__URL=postgresql://env.db.com:5432/main
DATABASE__CACHE__URL=redis://env.cache.com:6379
NEW_ENV_VAR=loaded_from_env_file
"""
            env_file.write_text(env_content.strip())

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    # These should be loaded (have defaults)
                    'DATABASE__MAIN__POOL_SIZE': '20',
                    'API__OPENAI__KEY': 'sk-os-env-key',
                    # These should NOT be loaded (no defaults)
                    'RANDOM_OS_VAR': 'should_not_be_loaded',
                    'UNRELATED_VAR': 'also_should_not_be_loaded'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Requirement 1: Store everything as dict with multiple levels
                    # Requirement 3: Default config can be nested or flat
                    default_config = {
                        # Nested format
                        'database': {
                            'main': {
                                'url': 'sqlite:///default.db',
                                'pool_size': 10
                            }
                        },
                        # Flat format
                        'api.openai.key': 'default-openai-key',
                        'simple_key': 'default_value'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Requirement 1: Internally all data is in a big dict of multiple levels
                    nested_dict = config.to_dict()
                    assert isinstance(nested_dict, dict)
                    assert isinstance(nested_dict['database'], dict)
                    assert isinstance(nested_dict['database']['main'], dict)
                    assert isinstance(nested_dict['api'], dict)
                    assert isinstance(nested_dict['api']['openai'], dict)

                    # Requirement 2: All __ in environment or env files are converted into the big dict
                    # From OS env vars (with defaults)
                    assert config.get('database.main.pool_size') == 20  # DATABASE__MAIN__POOL_SIZE
                    assert config.get('api.openai.key') == 'sk-os-env-key'  # API__OPENAI__KEY

                    # From env file
                    assert config.get('database.main.url') == 'postgresql://env.db.com:5432/main'  # DATABASE__MAIN__URL
                    assert config.get('database.cache.url') == 'redis://env.cache.com:6379'  # DATABASE__CACHE__URL

                    # Requirement 3: OS env vars only loaded if they have defaults, env files load all
                    # OS env vars without defaults should NOT be loaded
                    assert config.get('random_os_var') is None
                    assert config.get('unrelated_var') is None
                    assert 'random_os_var' not in config.to_flat_dict()
                    assert 'unrelated_var' not in config.to_flat_dict()

                    # Env file vars should be loaded even without defaults
                    assert config.get('new_env_var') == 'loaded_from_env_file'

                    # Requirement 4: Accessing variables should always use dot separated keys
                    assert config.get('database.main.url') == 'postgresql://env.db.com:5432/main'
                    assert config.get('database.main.pool_size') == 20
                    assert config.get('database.cache.url') == 'redis://env.cache.com:6379'
                    assert config.get('api.openai.key') == 'sk-os-env-key'
                    assert config.get('simple_key') == 'default_value'

                    # Requirement 5: We can get section of config and access with remaining part of keys
                    database_section = config.get('database')
                    assert database_section.get('main').get('url') == 'postgresql://env.db.com:5432/main'
                    assert database_section.get('main').get('pool_size') == 20
                    assert database_section.get('cache').get('url') == 'redis://env.cache.com:6379'

                    api_section = config.get('api')
                    assert api_section.get('openai').get('key') == 'sk-os-env-key'

                    # Alternative access pattern for requirement 5
                    database_main = config.get('database.main')
                    assert database_main.get('url') == 'postgresql://env.db.com:5432/main'
                    assert database_main.get('pool_size') == 20

                    # Verify the structure is exactly as expected
                    expected_structure = {
                        'database': {
                            'main': {
                                'url': 'postgresql://env.db.com:5432/main',
                                'pool_size': 20
                            },
                            'cache': {
                                'url': 'redis://env.cache.com:6379'
                            }
                        },
                        'api': {
                            'openai': {
                                'key': 'sk-os-env-key'
                            }
                        },
                        'simple_key': 'default_value',
                        'new_env_var': 'loaded_from_env_file',
                        'project_root': str(tmpdir_path)
                    }

                    actual_structure = config.to_dict()
                    # Remove any extra environment variables that might be present
                    filtered_actual = {k: v for k, v in actual_structure.items()
                                     if k in expected_structure}

                    assert filtered_actual == expected_structure


class TestEnvironmentVariableMatchingApproaches:
    """Test different approaches for matching environment variables to config keys."""

    def test_current_approach_vs_alternative(self):
        """Demonstrate current approach vs alternative approach for env var matching."""
        from zero_config.config import _flatten_nested_dict

        # Sample nested config
        nested_config = {
            'database': {
                'develope': {
                    'db_url': 'sqlite:///default.db',
                    'pool_size': 5
                },
                'production': {
                    'db_url': 'postgresql://prod.db.com:5432/prod'
                }
            },
            'llm': {
                'openai': {
                    'api_key': 'default-key',
                    'model': 'gpt-3.5-turbo'
                }
            },
            'simple_key': 'default_value'
        }

        # Sample environment variables
        env_vars = {
            'DATABASE__DEVELOPE__DB_URL': 'postgresql://localhost:5432/dev',
            'DATABASE__DEVELOPE__POOL_SIZE': '10',
            'LLM__OPENAI__API_KEY': 'sk-test123',
            'UNRELATED_VAR': 'should_not_match',  # No corresponding config
            'SIMPLE_KEY': 'overridden_value'
        }

        print("\n🔍 Demonstrating Environment Variable Matching Approaches")
        print("=" * 65)

        # CURRENT APPROACH: Flatten config to dot notation, convert env vars to dot notation
        print("\n📊 Current Approach:")
        print("1. Flatten config to dot notation")
        flattened_config = _flatten_nested_dict(nested_config)
        print(f"   Flattened config keys: {list(flattened_config.keys())}")

        print("2. Convert env vars to dot notation and match")
        current_matches = {}
        for env_var, env_value in env_vars.items():
            if env_var.isupper():
                if '__' in env_var:
                    config_key = '.'.join([part.lower() for part in env_var.split('__')])
                else:
                    config_key = env_var.lower()

                if config_key in flattened_config:
                    current_matches[env_var] = config_key
                    print(f"   ✅ {env_var} → {config_key} (MATCH)")
                else:
                    print(f"   ❌ {env_var} → {config_key} (NO MATCH)")

        # ALTERNATIVE APPROACH: Flatten config to __ notation, direct lookup
        print("\n📊 Alternative Approach (Your Suggestion):")
        print("1. Flatten config to __ notation")

        def _flatten_to_env_format(nested_dict: dict, parent_key: str = '', separator: str = '__') -> dict:
            """Flatten nested dict to environment variable format (UPPER__CASE__KEYS)."""
            items = []
            for key, value in nested_dict.items():
                new_key = f"{parent_key}{separator}{key.upper()}" if parent_key else key.upper()
                if isinstance(value, dict):
                    items.extend(_flatten_to_env_format(value, new_key, separator).items())
                else:
                    items.append((new_key, value))
            return dict(items)

        env_format_config = _flatten_to_env_format(nested_config)
        print(f"   Env format config keys: {list(env_format_config.keys())}")

        print("2. Direct lookup of env vars")
        alternative_matches = {}
        for env_var, env_value in env_vars.items():
            if env_var.isupper():
                if env_var in env_format_config:
                    alternative_matches[env_var] = env_var
                    print(f"   ✅ {env_var} (DIRECT MATCH)")
                else:
                    print(f"   ❌ {env_var} (NO MATCH)")

        # Both approaches should yield the same results
        print(f"\n📈 Results Comparison:")
        print(f"   Current approach matches: {len(current_matches)}")
        print(f"   Alternative approach matches: {len(alternative_matches)}")

        # Convert alternative matches to same format for comparison
        alternative_converted = {}
        for env_var in alternative_matches:
            if '__' in env_var:
                config_key = '.'.join([part.lower() for part in env_var.split('__')])
            else:
                config_key = env_var.lower()
            alternative_converted[env_var] = config_key

        assert current_matches == alternative_converted, "Both approaches should yield same results"

        print("   ✅ Both approaches yield identical results!")

        # Performance consideration
        print(f"\n⚡ Performance Considerations:")
        print(f"   Current: O(E) where E = number of env vars")
        print(f"   Alternative: O(E) where E = number of env vars")
        print(f"   Both are O(E) but alternative has simpler lookup logic")


def _demonstrate_alternative_implementation():
    """Show how the alternative approach could be implemented."""

    def apply_environment_variables_alternative(config: dict) -> None:
        """Alternative implementation using __ format flattening."""

        # Step 1: Create a reverse mapping from ENV_VAR format to dot notation
        def _flatten_to_env_format(nested_dict: dict, parent_key: str = '', separator: str = '__') -> dict:
            """Flatten nested dict to environment variable format."""
            items = []
            for key, value in nested_dict.items():
                new_key = f"{parent_key}{separator}{key.upper()}" if parent_key else key.upper()
                if isinstance(value, dict):
                    items.extend(_flatten_to_env_format(value, new_key, separator).items())
                else:
                    # Store the dot notation key as the value for reverse lookup
                    dot_key = f"{parent_key.lower().replace('__', '.')}.{key}" if parent_key else key
                    items.append((new_key, dot_key))
            return dict(items)

        # Step 2: Build the reverse mapping
        env_to_dot_mapping = {}

        # We need to reconstruct the nested structure from flat config first
        # This is more complex, so the current approach is actually simpler!

        # Step 3: Direct lookup
        for env_var, env_value in os.environ.items():
            if env_var.isupper() and env_var in env_to_dot_mapping:
                dot_key = env_to_dot_mapping[env_var]
                if dot_key in config:
                    # Apply the override
                    pass

    return apply_environment_variables_alternative


class TestImprovedEnvironmentVariableMatching:
    """Test the improved environment variable matching approach."""

    def test_direct_nested_override_approach(self):
        """Test that the improved approach directly overrides nested structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__DEVELOPE__DB_URL': 'postgresql://localhost:5432/dev',
                    'DATABASE__DEVELOPE__POOL_SIZE': '25',
                    'LLM__OPENAI__API_KEY': 'sk-improved-test',
                    'UNRELATED_VAR': 'should_not_be_loaded'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Nested default config
                    default_config = {
                        'database': {
                            'develope': {
                                'db_url': 'sqlite:///default.db',
                                'pool_size': 10,
                                'timeout': 30
                            }
                        },
                        'llm': {
                            'openai': {
                                'api_key': 'default-key',
                                'model': 'gpt-3.5-turbo'
                            }
                        }
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Test that environment variables properly override nested values
                    assert config.get('database.develope.db_url') == 'postgresql://localhost:5432/dev'
                    assert config.get('database.develope.pool_size') == 25  # Should be converted to int
                    assert config.get('database.develope.timeout') == 30  # Should remain default
                    assert config.get('llm.openai.api_key') == 'sk-improved-test'
                    assert config.get('llm.openai.model') == 'gpt-3.5-turbo'  # Should remain default

                    # Test that unrelated env vars are not loaded
                    assert config.get('unrelated_var') is None

                    # Test that nested structure is preserved
                    nested_dict = config.to_dict()
                    assert isinstance(nested_dict['database'], dict)
                    assert isinstance(nested_dict['database']['develope'], dict)
                    assert nested_dict['database']['develope']['db_url'] == 'postgresql://localhost:5432/dev'
                    assert nested_dict['database']['develope']['pool_size'] == 25

                    # Test section access works perfectly
                    database_section = config.get('database')
                    assert database_section['develope']['db_url'] == 'postgresql://localhost:5432/dev'
                    assert database_section['develope']['pool_size'] == 25

                    # Test subsection access
                    develope_section = config.get('database.develope')
                    assert develope_section['db_url'] == 'postgresql://localhost:5432/dev'
                    assert develope_section['pool_size'] == 25

    def test_env_mapping_creation(self):
        """Test the environment variable mapping creation."""
        from zero_config.config import _create_env_mapping, _build_nested_dict_from_flat

        # Test flat config to nested conversion
        flat_config = {
            'database.develope.db_url': 'sqlite:///default.db',
            'database.develope.pool_size': 10,
            'llm.openai.api_key': 'default-key',
            'simple_key': 'value'
        }

        nested_config = _build_nested_dict_from_flat(flat_config)
        expected_nested = {
            'database': {
                'develope': {
                    'db_url': 'sqlite:///default.db',
                    'pool_size': 10
                }
            },
            'llm': {
                'openai': {
                    'api_key': 'default-key'
                }
            },
            'simple_key': 'value'
        }

        assert nested_config == expected_nested

        # Test environment mapping creation
        env_mapping = _create_env_mapping(nested_config)
        expected_mapping = {
            'DATABASE__DEVELOPE__DB_URL': ['database', 'develope', 'db_url'],
            'DATABASE__DEVELOPE__POOL_SIZE': ['database', 'develope', 'pool_size'],
            'LLM__OPENAI__API_KEY': ['llm', 'openai', 'api_key'],
            'SIMPLE_KEY': ['simple_key']
        }

        assert env_mapping == expected_mapping

    def test_advantages_of_improved_approach(self):
        """Demonstrate the advantages of the improved approach."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__CACHE__REDIS__HOST': 'redis.example.com',
                    'DATABASE__CACHE__REDIS__PORT': '6379',
                    'API__EXTERNAL__WEATHER__KEY': 'weather-api-key',
                    'API__EXTERNAL__WEATHER__TIMEOUT': '30'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Complex nested default config
                    default_config = {
                        'database': {
                            'cache': {
                                'redis': {
                                    'host': 'localhost',
                                    'port': 6379,
                                    'db': 0
                                }
                            }
                        },
                        'api': {
                            'external': {
                                'weather': {
                                    'key': 'default-weather-key',
                                    'timeout': 10,
                                    'retries': 3
                                }
                            }
                        }
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Advantage 1: Direct nested access works perfectly
                    assert config.get('database.cache.redis.host') == 'redis.example.com'
                    assert config.get('database.cache.redis.port') == 6379  # Type converted
                    assert config.get('database.cache.redis.db') == 0  # Default preserved

                    assert config.get('api.external.weather.key') == 'weather-api-key'
                    assert config.get('api.external.weather.timeout') == 30  # Type converted
                    assert config.get('api.external.weather.retries') == 3  # Default preserved

                    # Advantage 2: Section access is natural and intuitive
                    redis_config = config.get('database.cache.redis')
                    assert redis_config == {
                        'host': 'redis.example.com',
                        'port': 6379,
                        'db': 0
                    }

                    weather_config = config.get('api.external.weather')
                    assert weather_config == {
                        'key': 'weather-api-key',
                        'timeout': 30,
                        'retries': 3
                    }

                    # Advantage 3: Nested structure is preserved perfectly
                    full_config = config.to_dict()
                    assert full_config['database']['cache']['redis']['host'] == 'redis.example.com'
                    assert full_config['api']['external']['weather']['key'] == 'weather-api-key'

                    # Advantage 4: No complex reconstruction needed - it's already nested!
                    # The config object maintains both flat and nested representations seamlessly





class TestProjectRootCorrectBehavior:
    """Test that PROJECT_ROOT behaves correctly (OS env > auto-detection, .env files ignored)."""

    def test_os_env_project_root_overrides_auto_detection(self):
        """Test that OS environment PROJECT_ROOT overrides auto-detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            custom_project_root = tmpdir_path / "custom_project_root"
            custom_project_root.mkdir()

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'PROJECT_ROOT': str(custom_project_root),
                    'DATABASE__URL': 'postgresql://localhost:5432/test'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Default config
                    default_config = {
                        'database.url': 'sqlite:///default.db'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # OS environment PROJECT_ROOT should override auto-detection
                    assert config.get('project_root') == str(custom_project_root)
                    assert config.get('database.url') == 'postgresql://localhost:5432/test'

    def test_env_file_project_root_ignored(self):
        """Test that PROJECT_ROOT in .env files is ignored (chicken-and-egg problem)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            env_file_root = tmpdir_path / "env_file_root"
            env_file_root.mkdir()

            # Create .env file with PROJECT_ROOT (should be ignored)
            env_file = tmpdir_path / ".env.zero_config"
            env_content = f"""
PROJECT_ROOT={env_file_root}
DATABASE__URL=postgresql://env.db.com:5432/test
"""
            env_file.write_text(env_content.strip())

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {}, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Default config
                    default_config = {
                        'database.url': 'sqlite:///default.db'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # Should use auto-detected project root, NOT the .env file value
                    assert config.get('project_root') == str(tmpdir_path)
                    # But other .env file values should work
                    assert config.get('database.url') == 'postgresql://env.db.com:5432/test'

    def test_project_root_priority_order(self):
        """Test the correct priority order: OS env > auto-detection (.env files ignored)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            custom_os_root = tmpdir_path / "custom_os_root"
            env_file_root = tmpdir_path / "env_file_root"
            custom_os_root.mkdir()
            env_file_root.mkdir()

            # Create .env file in the OS environment PROJECT_ROOT location
            # (since that's where the system will look for it)
            env_file = custom_os_root / ".env.zero_config"
            env_content = f"""
PROJECT_ROOT={env_file_root}
DATABASE__URL=postgresql://env.db.com:5432/test
API__KEY=env-file-key
"""
            env_file.write_text(env_content.strip())

            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'PROJECT_ROOT': str(custom_os_root),  # Should win
                    'DATABASE__POOL_SIZE': '20'
                }, clear=True):
                    # Reset state first
                    _reset_for_testing()

                    # Default config
                    default_config = {
                        'database.url': 'sqlite:///default.db',
                        'database.pool_size': 5,
                        'api.key': 'default-key'
                    }

                    setup_environment(default_config=default_config)
                    config = get_config()

                    # OS environment PROJECT_ROOT should win (not .env file)
                    assert config.get('project_root') == str(custom_os_root)
                    # Other .env file values should work normally
                    assert config.get('database.url') == 'postgresql://env.db.com:5432/test'
                    assert config.get('api.key') == 'env-file-key'
                    # OS env vars should work
                    assert config.get('database.pool_size') == 20


if __name__ == "__main__":
    pytest.main([__file__])
