import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from zero_config import setup_environment, get_config
from zero_config.config import (
    Config,
    smart_convert,
    find_project_root,
    load_domain_env_file,
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
                    # Test single env file
                    setup_environment(env_files=env1)
                    config = get_config()

                    assert config.get('key1') == 'value1'
                    assert config.get('shared_key') == 'from_env1'
                    assert config.get('key2') is None

                    # Reset for next test
                    import zero_config.config
                    zero_config.config._config = None

                    # Test multiple env files (later files override earlier ones)
                    setup_environment(env_files=[env1, env2])
                    config = get_config()

                    assert config.get('key1') == 'value1'
                    assert config.get('key2') == 'value2'
                    assert config.get('shared_key') == 'from_env2'  # env2 overrides env1


if __name__ == "__main__":
    pytest.main([__file__])
