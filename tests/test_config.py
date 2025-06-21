import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from zero_config import (
    setup_environment, 
    get_config, 
    data_path, 
    logs_path,
    DEFAULTS,
    smart_convert,
    find_project_root,
    load_domain_env_file
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
        assert smart_convert("false", True) == False
        assert smart_convert("0", True) == False
    
    def test_list_conversion(self):
        assert smart_convert("a,b,c", []) == ["a", "b", "c"]
        assert smart_convert("a, b , c", []) == ["a", "b", "c"]  # strips whitespace


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

            # Create a .env.zero_config file
            (tmpdir_path / ".env.zero_config").touch()

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


class TestConfiguration:
    """Test the main configuration functionality."""
    
    def test_defaults_loaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                setup_environment()
                config = get_config()
                
                # Check some default values
                assert config.get('default_model') == 'gpt-4o-mini'
                assert config.get('temperature') == 0.0
                assert config.get('max_tokens') == 1024
                assert isinstance(config.get('openai_models'), list)
    
    def test_environment_variable_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                with patch.dict(os.environ, {
                    'OPENAI_API_KEY': 'sk-test-key',
                    'ZERO_CONFIG_TEMPERATURE': '0.8',
                    'ZERO_CONFIG_MAX_TOKENS': '2048'
                }):
                    setup_environment()
                    config = get_config()
                    
                    assert config.get('openai_api_key') == 'sk-test-key'
                    assert config.get('temperature') == 0.8
                    assert config.get('max_tokens') == 2048
    
    def test_config_methods(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                setup_environment()
                config = get_config()
                
                # Test __getitem__
                assert config['default_model'] == 'gpt-4o-mini'
                
                # Test __contains__
                assert 'default_model' in config
                assert 'nonexistent_key' not in config
                
                # Test get with default
                assert config.get('nonexistent_key', 'default_value') == 'default_value'
                
                # Test to_dict
                config_dict = config.to_dict()
                assert isinstance(config_dict, dict)
                assert 'default_model' in config_dict
    
    def test_path_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('zero_config.config.find_project_root', return_value=Path(tmpdir)):
                setup_environment()
                
                # Test data_path
                data_dir = data_path()
                assert data_dir == str(Path(tmpdir) / "data")
                
                data_file = data_path("test.db")
                assert data_file == str(Path(tmpdir) / "data" / "test.db")
                
                # Test logs_path
                logs_dir = logs_path()
                assert logs_dir == str(Path(tmpdir) / "logs")
                
                log_file = logs_path("app.log")
                assert log_file == str(Path(tmpdir) / "logs" / "app.log")


if __name__ == "__main__":
    pytest.main([__file__])
