# Zero Config Documentation

Welcome to the Zero Config documentation! This directory contains comprehensive guides for using zero-config effectively.

## 📚 Documentation Index

### Core Guides

- **[Multi-Level Configuration](MULTI_LEVEL_CONFIGURATION.md)** ⭐ **NEW in v0.1.5+**
  - Complete guide to nested configuration support
  - Environment variable conversion with `__` syntax
  - Mixed configuration formats (nested dicts + flat dot notation)
  - Environment variable filtering
  - Advanced section access

- **[Package Conflict Prevention](PACKAGE_CONFLICT_PREVENTION.md)**
  - How zero-config prevents configuration conflicts
  - Main application vs package dependency scenarios
  - Initialization protection mechanism
  - Best practices for package developers

- **[Best Practices](BEST_PRACTICES.md)**
  - Application architecture patterns
  - Configuration design principles
  - Security considerations
  - Testing strategies
  - Deployment patterns

- **[Examples](EXAMPLES.md)**
  - Real-world usage examples
  - Web application configurations
  - Data pipeline setups
  - Package development patterns

## 🚀 Quick Start

If you're new to zero-config, start with the main [README.md](../README.md) in the project root, then explore these guides based on your needs:

1. **Basic Usage**: Start with the main README
2. **Complex Configurations**: Read [Multi-Level Configuration](MULTI_LEVEL_CONFIGURATION.md)
3. **Package Development**: Read [Package Conflict Prevention](PACKAGE_CONFLICT_PREVENTION.md)
4. **Production Deployment**: Read [Best Practices](BEST_PRACTICES.md)
5. **Real Examples**: Browse [Examples](EXAMPLES.md)

## 🔄 Version-Specific Features

### v0.1.5+ Features
- ✅ Multi-level configuration with `DATABASE__DEVELOPE__DB_URL` → `database.develope.db_url`
- ✅ Mixed configuration formats (nested dicts + flat dot notation)
- ✅ Environment variable filtering (OS env vars only loaded if defaults exist)
- ✅ Enhanced section access with arbitrary nesting levels

### v0.1.1+ Features
- ✅ Package conflict prevention
- ✅ Initialization tracking with `is_initialized()` and `get_initialization_info()`
- ✅ Force re-initialization with `force_reinit=True`

### v0.1.0 Features
- ✅ Layered configuration (defaults → env vars → env files)
- ✅ Smart type conversion
- ✅ Dynamic path helpers (`config.data_path()`, etc.)
- ✅ Section access (`config.get('llm')`)
- ✅ Project root auto-detection

## 🛠️ Advanced Topics

### Configuration Architecture

For complex applications, consider organizing your configuration by domain:

```python
default_config = {
    'database': {
        'develope': {...},
        'production': {...},
        'test': {...}
    },
    'llm': {
        'openai': {...},
        'anthropic': {...},
        'ollama': {...}
    },
    'api': {
        'external': {...},
        'internal': {...}
    }
}
```

### Environment Variable Strategy

- **OS Environment Variables**: Use for deployment-specific overrides (Docker, CI/CD)
- **Environment Files**: Use for local development and secrets management
- **Defaults in Code**: Define schema and sensible fallbacks

### Package Integration

When developing packages that use zero-config:

```python
def initialize_package():
    # This will be ignored if main app already initialized
    setup_environment(default_config=package_defaults)
    
    # Always access config this way
    config = get_config()
    return config.get('package_section')
```

## 🔍 Debugging and Troubleshooting

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

setup_environment(default_config=config)
# INFO: Auto-detected project root: /path/to/project
# INFO: 🚀 Environment setup complete
```

### Check Initialization Status

```python
from zero_config import is_initialized, get_initialization_info

if is_initialized():
    print(f"Initialized by: {get_initialization_info()}")
else:
    print("Not yet initialized")
```

### Common Issues

See the main README.md for troubleshooting common issues.

## 📖 External Resources

- **GitHub Repository**: https://github.com/xychenmsn/zero-config
- **PyPI Package**: https://pypi.org/project/zero-config/
- **Issue Tracker**: https://github.com/xychenmsn/zero-config/issues

## 🤝 Contributing

Found an issue or want to improve the documentation? Please:

1. Check existing issues on GitHub
2. Create a new issue with details
3. Submit a pull request with improvements

## 📝 License

Zero Config is released under the MIT License. See the LICENSE file in the project root for details.
