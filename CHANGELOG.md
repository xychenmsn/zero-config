# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-01-23

### Documentation

- **Comprehensive documentation updates**: Updated README.md with multi-level configuration examples
- **New documentation structure**: Added `docs/README.md` as documentation index
- **Enhanced guides**: Updated all documentation to reflect v0.1.5+ features
- **Release notes**: Added `RELEASE_NOTES_0.1.6.md` with complete feature overview
- **Migration guidance**: Updated migration guide for v0.1.5+ features

### Enhanced

- Updated README.md with environment variable filtering explanation
- Enhanced API reference with multi-level configuration methods
- Improved examples showing mixed configuration formats
- Better documentation of package conflict prevention

## [0.1.5] - 2025-01-23

### Added

- **Multi-level configuration support**: Environment variables with double underscores (`DATABASE__DEVELOPE__DB_URL`) are converted to nested structure (`database.develope.db_url`)
- **Enhanced DotDict implementation**: Native dot notation support for nested access and assignment
- **Environment variable filtering**: OS environment variables are only loaded if they have corresponding defaults in configuration
- **Mixed configuration formats**: Support both nested dictionaries and flat dot notation in default configuration
- **Improved section access**: Enhanced section access with multi-level support (`config.get('database.develope')`)
- **New documentation**: Added `docs/MULTI_LEVEL_CONFIGURATION.md` with comprehensive guide
- **Demo script**: Added `demo_multi_level.py` demonstrating all multi-level features

### Enhanced

- `Config.to_flat_dict()` method for getting flat representation with dot notation keys
- Environment file loading now supports multi-level keys with `__` conversion
- Smart type conversion works with multi-level configurations
- Section access now supports arbitrary nesting levels

### Internal

- Refactored configuration storage to use nested dictionaries internally
- Improved environment variable matching algorithm for better performance
- Enhanced `_flatten_nested_dict()` function for mixed format support
- Better logging for multi-level configuration debugging

## [0.1.4] - 2025-01-22

### Added

- Enhanced test coverage for edge cases and real-world scenarios
- Improved error handling and validation
- Better logging and debugging support

## [0.1.3] - 2025-01-22

### Added

- Complete documentation package inclusion via MANIFEST.in
- All documentation files now included in source distribution
- Examples directory with demo scripts included
- CHANGELOG.md and release notes included

### Fixed

- Documentation files (docs/, examples/) now properly included in PyPI package
- Users can now access all guides and examples after installation

## [0.1.2] - 2025-01-22

### Added

- Comprehensive documentation suite including best practices, examples, and troubleshooting guides
- Enhanced test coverage with 48 total tests (24 new tests added)
- Real-world integration tests covering package conflict scenarios
- Demo script tests and validation
- Detailed package conflict prevention documentation

### Enhanced

- README with expanded package conflict prevention section and best practices
- API documentation with clear examples and troubleshooting
- Test isolation and error handling coverage
- Logging validation and debugging information

### Documentation

- `docs/BEST_PRACTICES.md` - Comprehensive guide for using zero-config effectively
- `docs/EXAMPLES.md` - Real-world examples for web apps, data pipelines, and packages
- `docs/PACKAGE_CONFLICT_PREVENTION.md` - Detailed technical documentation
- Enhanced README with migration guide and debugging section

### Testing

- Added 24 new test cases covering edge cases and real-world scenarios
- Integration tests for news app + united_llm scenario
- Demo script validation tests
- Comprehensive error handling and logging tests

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
