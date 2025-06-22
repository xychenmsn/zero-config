# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-01-22

### Added
- **Package Conflict Prevention**: Automatic protection against configuration conflicts when both main projects and dependencies use zero-config
- `is_initialized()` function to check if zero-config has been initialized
- `get_initialization_info()` function to get information about who initialized the configuration
- `force_reinit=True` parameter for `setup_environment()` to allow forced re-initialization in special cases
- Comprehensive logging for initialization events and conflicts
- Caller tracking to identify which file/line initialized the configuration

### Changed
- `setup_environment()` now ignores subsequent calls after the first initialization (unless `force_reinit=True`)
- Enhanced logging with more detailed information about initialization status
- Improved error messages for better debugging

### Fixed
- Package dependencies can no longer accidentally overwrite main project configuration
- Global state conflicts between main applications and their dependencies

### Technical Details
- Added global state tracking with `_is_initialized` and `_initialized_by` variables
- Enhanced test suite with 12 new test cases covering edge cases and error scenarios
- Added `_reset_for_testing()` internal function for proper test isolation

## [0.1.0] - 2025-01-21

### Added
- Initial release of zero-config
- Layered configuration system (defaults → environment variables → environment files)
- Smart type conversion based on default value types
- Dynamic path helpers (Ruby on Rails style)
- Section-based configuration with dot notation
- Project root auto-detection
- Support for custom environment files
- Environment variable section headers with double underscore syntax
- Comprehensive test suite

### Features
- **Configuration Sources**:
  - Application defaults in code
  - Environment variables with automatic type conversion
  - Environment files (`.env.zero_config` or custom files)
  
- **Type Safety**:
  - Automatic conversion of strings to match default types
  - Support for int, float, bool, list, and string types
  - Safe handling of comma-containing strings
  
- **Dynamic Paths**:
  - `config.data_path()`, `config.logs_path()`, etc.
  - Any `{name}_path()` pattern automatically works
  
- **Section Access**:
  - `config.get('llm')` returns all `llm.*` keys as a dictionary
  - Dot notation support in configuration keys
  
- **Project Root Detection**:
  - Automatic detection using `.git`, `pyproject.toml`, etc.
  - Override via `PROJECT_ROOT` environment variable

### Dependencies
- Python 3.8+
- No external dependencies for core functionality
- Optional: `python-dotenv` for enhanced .env file support
