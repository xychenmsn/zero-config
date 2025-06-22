#!/usr/bin/env python3
"""
Integration tests for zero-config package conflict prevention.

These tests simulate real-world scenarios where main applications and
package dependencies both use zero-config.
"""

import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch

from zero_config import setup_environment, get_config, is_initialized, get_initialization_info
from zero_config.config import _reset_for_testing


class TestRealWorldIntegration:
    """Test real-world integration scenarios."""
    
    def setup_method(self):
        """Reset state before each test."""
        _reset_for_testing()
    
    def teardown_method(self):
        """Reset state after each test."""
        _reset_for_testing()
    
    def test_news_app_with_united_llm_scenario(self):
        """Test the exact scenario described in the original issue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Simulate news app (main project) initialization
                news_config = {
                    'app_name': 'news_app',
                    'app_version': '1.0.0',
                    'database.host': 'localhost',
                    'database.port': 5432,
                    'database.name': 'news_db',
                    'llm.provider': 'openai',
                    'llm.api_key': 'sk-news-app-key',
                    'llm.model': 'gpt-4',
                    'llm.temperature': 0.3,
                    'cache.enabled': True,
                    'cache.ttl': 3600
                }
                
                # News app initializes zero-config
                setup_environment(default_config=news_config)
                
                # Verify news app config is set
                config = get_config()
                assert config.get('app_name') == 'news_app'
                assert config.get('llm.api_key') == 'sk-news-app-key'
                assert config.get('llm.temperature') == 0.3
                
                # Simulate united_llm package trying to initialize
                united_llm_config = {
                    'package_name': 'united_llm',
                    'package_version': '2.1.0',
                    'llm.provider': 'anthropic',  # Different from news app
                    'llm.api_key': 'sk-united-llm-key',  # Different from news app
                    'llm.model': 'claude-3',  # Different from news app
                    'llm.temperature': 0.7,  # Different from news app
                    'llm.max_tokens': 2048,
                    'llm.timeout': 30
                }
                
                # united_llm tries to initialize (should be ignored)
                setup_environment(default_config=united_llm_config)
                
                # Verify news app config is preserved
                config = get_config()
                assert config.get('app_name') == 'news_app'  # News app config preserved
                assert config.get('llm.api_key') == 'sk-news-app-key'  # News app key preserved
                assert config.get('llm.temperature') == 0.3  # News app temperature preserved
                assert config.get('llm.model') == 'gpt-4'  # News app model preserved
                
                # united_llm config should NOT be present
                assert config.get('package_name') is None
                assert config.get('package_version') is None
                assert config.get('llm.max_tokens') is None
                assert config.get('llm.timeout') is None
                
                # But united_llm can still access news app's LLM config
                llm_config = config.get('llm')
                assert llm_config is not None
                assert llm_config['api_key'] == 'sk-news-app-key'
                assert llm_config['temperature'] == 0.3
                assert llm_config['model'] == 'gpt-4'
                assert llm_config['provider'] == 'openai'
    
    def test_multiple_packages_with_main_app(self):
        """Test scenario with main app and multiple package dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Main application config
                main_config = {
                    'app_name': 'data_pipeline',
                    'database.host': 'prod.db.com',
                    'database.port': 5432,
                    'llm.api_key': 'sk-main-key',
                    'llm.temperature': 0.2,
                    'storage.bucket': 'main-bucket',
                    'monitoring.enabled': True
                }
                
                # Main app initializes
                setup_environment(default_config=main_config)
                
                # Package 1: LLM processing package
                llm_package_config = {
                    'llm.max_tokens': 4000,
                    'llm.timeout': 60,
                    'package1.name': 'llm_processor'
                }
                setup_environment(default_config=llm_package_config)  # Ignored
                
                # Package 2: Data storage package
                storage_package_config = {
                    'storage.compression': 'gzip',
                    'storage.encryption': True,
                    'package2.name': 'data_storage'
                }
                setup_environment(default_config=storage_package_config)  # Ignored
                
                # Package 3: Monitoring package
                monitoring_package_config = {
                    'monitoring.interval': 30,
                    'monitoring.alerts': True,
                    'package3.name': 'monitoring'
                }
                setup_environment(default_config=monitoring_package_config)  # Ignored
                
                # Verify only main app config is present
                config = get_config()
                assert config.get('app_name') == 'data_pipeline'
                assert config.get('database.host') == 'prod.db.com'
                assert config.get('llm.api_key') == 'sk-main-key'
                assert config.get('storage.bucket') == 'main-bucket'
                assert config.get('monitoring.enabled') is True
                
                # Package-specific configs should not be present
                assert config.get('llm.max_tokens') is None
                assert config.get('storage.compression') is None
                assert config.get('monitoring.interval') is None
                assert config.get('package1.name') is None
                assert config.get('package2.name') is None
                assert config.get('package3.name') is None
                
                # But packages can access relevant sections
                llm_section = config.get('llm')
                storage_section = config.get('storage')
                monitoring_section = config.get('monitoring')
                
                assert llm_section['api_key'] == 'sk-main-key'
                assert storage_section['bucket'] == 'main-bucket'
                assert monitoring_section['enabled'] is True
    
    def test_package_without_main_app(self):
        """Test package behavior when no main app has initialized zero-config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Package initializes first (no main app)
                package_config = {
                    'package_name': 'standalone_package',
                    'llm.api_key': 'sk-package-key',
                    'llm.temperature': 0.8,
                    'timeout': 30
                }
                
                # Package should be able to initialize successfully
                setup_environment(default_config=package_config)
                
                config = get_config()
                assert config.get('package_name') == 'standalone_package'
                assert config.get('llm.api_key') == 'sk-package-key'
                assert config.get('llm.temperature') == 0.8
                assert config.get('timeout') == 30
                
                # Subsequent package initialization should be ignored
                another_package_config = {
                    'another_package': 'test',
                    'llm.model': 'different-model'
                }
                setup_environment(default_config=another_package_config)
                
                # Original package config should be preserved
                config = get_config()
                assert config.get('package_name') == 'standalone_package'
                assert config.get('another_package') is None
                assert config.get('llm.model') is None
    
    def test_initialization_tracking_across_packages(self):
        """Test that initialization tracking works correctly across packages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Check initial state
                assert not is_initialized()
                assert get_initialization_info() is None
                
                # Main app initializes
                setup_environment(default_config={'main': True})
                
                assert is_initialized()
                init_info = get_initialization_info()
                assert init_info is not None
                assert 'test_integration.py' in init_info
                
                # Package tries to initialize
                original_init_info = init_info
                setup_environment(default_config={'package': True})
                
                # Initialization info should remain the same (from main app)
                assert get_initialization_info() == original_init_info
                
                # Config should still be from main app
                config = get_config()
                assert config.get('main') is True
                assert config.get('package') is None
    
    def test_logging_during_package_conflicts(self, caplog):
        """Test that appropriate logging occurs during package conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with caplog.at_level(logging.INFO):
                    # Main app initializes
                    setup_environment(default_config={'main_app': True})
                    
                    # Should log successful initialization
                    assert "🚀 Environment setup complete" in caplog.text
                    assert "Initialized by:" in caplog.text
                    
                    # Clear logs
                    caplog.clear()
                    
                    # Package tries to initialize
                    with caplog.at_level(logging.INFO):
                        setup_environment(default_config={'package': True})
                    
                    # Should log that initialization was skipped
                    assert "Zero-config already initialized" in caplog.text
                    assert "Skipping re-initialization to prevent conflicts" in caplog.text
                    assert "Subsequent call from:" in caplog.text
    
    def test_force_reinit_in_package_scenario(self):
        """Test force re-initialization in package scenario (not recommended)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Main app initializes
                setup_environment(default_config={'main_app': 'original'})
                
                config = get_config()
                assert config.get('main_app') == 'original'
                
                # Package force re-initializes (not recommended!)
                setup_environment(
                    default_config={'package': 'override'}, 
                    force_reinit=True
                )
                
                # Config should now be from package (main app config lost)
                config = get_config()
                assert config.get('main_app') is None
                assert config.get('package') == 'override'


if __name__ == "__main__":
    pytest.main([__file__])
