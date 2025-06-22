#!/usr/bin/env python3
"""
Tests for the package conflict demo script.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from zero_config.config import _reset_for_testing


class TestPackageConflictDemo:
    """Test the package conflict demo functionality."""
    
    def setup_method(self):
        """Reset state before each test."""
        _reset_for_testing()
    
    def teardown_method(self):
        """Reset state after each test."""
        _reset_for_testing()
    
    def test_demo_functions_work(self):
        """Test that demo functions work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                # Import demo functions
                import sys
                import os
                
                # Add examples directory to path
                examples_dir = Path(__file__).parent.parent / "examples"
                sys.path.insert(0, str(examples_dir))
                
                try:
                    from package_conflict_demo import (
                        simulate_main_project,
                        simulate_package_dependency,
                        demonstrate_force_reinit
                    )
                    
                    # Test main project simulation
                    simulate_main_project()
                    
                    from zero_config import get_config, is_initialized
                    assert is_initialized()
                    
                    config = get_config()
                    assert config.get('app_name') == 'news_app'
                    assert config.get('llm.api_key') == 'main-project-key'
                    
                    # Test package dependency simulation
                    simulate_package_dependency()
                    
                    # Config should still be from main project
                    config = get_config()
                    assert config.get('app_name') == 'news_app'
                    assert config.get('package_name') is None  # Package config ignored
                    
                    # Test force reinit
                    demonstrate_force_reinit()
                    
                    # Config should now be different
                    config = get_config()
                    assert config.get('forced') is True
                    assert config.get('app_name') is None  # Original config gone
                    
                finally:
                    # Clean up sys.path
                    if str(examples_dir) in sys.path:
                        sys.path.remove(str(examples_dir))
    
    def test_demo_script_runs(self):
        """Test that the demo script can be executed."""
        import subprocess
        import sys
        
        # Get path to demo script
        demo_script = Path(__file__).parent.parent / "examples" / "package_conflict_demo.py"
        
        # Run the demo script
        result = subprocess.run(
            [sys.executable, str(demo_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check that it ran successfully
        assert result.returncode == 0, f"Demo script failed with stderr: {result.stderr}"
        
        # Check for expected output
        output = result.stdout
        assert "🚀 Zero-Config Package Conflict Prevention Demo" in output
        assert "Main Project: Initializing zero-config" in output
        assert "Package (united_llm): Attempting to initialize" in output
        assert "Demo complete!" in output
        
        # Check that no errors occurred
        assert "Error" not in result.stderr
        assert "Exception" not in result.stderr
    
    def test_demo_logging_output(self, caplog):
        """Test that demo produces expected logging output."""
        import logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                import sys
                examples_dir = Path(__file__).parent.parent / "examples"
                sys.path.insert(0, str(examples_dir))
                
                try:
                    with caplog.at_level(logging.INFO):
                        from package_conflict_demo import simulate_main_project, simulate_package_dependency
                        
                        # Simulate main project
                        simulate_main_project()
                        
                        # Should have initialization logs
                        assert "🚀 Environment setup complete" in caplog.text
                        
                        # Clear logs
                        caplog.clear()
                        
                        # Simulate package dependency
                        with caplog.at_level(logging.INFO):
                            simulate_package_dependency()
                        
                        # Should have conflict prevention logs
                        assert "Zero-config already initialized" in caplog.text
                        
                finally:
                    if str(examples_dir) in sys.path:
                        sys.path.remove(str(examples_dir))
    
    def test_demo_section_access(self):
        """Test that demo correctly demonstrates section access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                import sys
                examples_dir = Path(__file__).parent.parent / "examples"
                sys.path.insert(0, str(examples_dir))
                
                try:
                    from package_conflict_demo import simulate_main_project
                    from zero_config import get_config
                    
                    # Run main project simulation
                    simulate_main_project()
                    
                    # Test section access
                    config = get_config()
                    llm_section = config.get('llm')
                    database_section = config.get('database')
                    
                    # Verify sections are accessible
                    assert llm_section is not None
                    assert 'api_key' in llm_section
                    assert 'temperature' in llm_section
                    assert llm_section['api_key'] == 'main-project-key'
                    assert llm_section['temperature'] == 0.5
                    
                    assert database_section is not None
                    assert 'host' in database_section
                    assert 'port' in database_section
                    assert database_section['host'] == 'localhost'
                    assert database_section['port'] == 5432
                    
                finally:
                    if str(examples_dir) in sys.path:
                        sys.path.remove(str(examples_dir))


class TestDemoEdgeCases:
    """Test edge cases in the demo."""
    
    def setup_method(self):
        """Reset state before each test."""
        _reset_for_testing()
    
    def teardown_method(self):
        """Reset state after each test."""
        _reset_for_testing()
    
    def test_demo_with_missing_config_keys(self):
        """Test demo behavior when accessing missing config keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                from zero_config import setup_environment, get_config
                
                # Setup minimal config
                setup_environment(default_config={'minimal': True})
                
                config = get_config()
                
                # Test accessing missing keys returns None
                assert config.get('nonexistent_key') is None
                assert config.get('llm.nonexistent') is None
                assert config.get('database.nonexistent') is None
                
                # Test accessing missing sections returns None
                assert config.get('nonexistent_section') is None
    
    def test_demo_initialization_info_format(self):
        """Test that initialization info has correct format in demo context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                from zero_config import setup_environment, get_initialization_info
                
                # Setup config
                setup_environment(default_config={'test': True})
                
                # Get initialization info
                init_info = get_initialization_info()
                
                # Verify format
                assert init_info is not None
                assert '.py:' in init_info
                assert init_info.split(':')[-1].isdigit()  # Line number should be numeric


if __name__ == "__main__":
    pytest.main([__file__])
