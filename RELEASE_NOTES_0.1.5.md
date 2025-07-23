# Zero Config v0.1.5 Release Notes

## 🎉 What's New

Zero Config v0.1.5 introduces **multi-level configuration support** - a major enhancement that allows you to organize complex configurations with nested structures while maintaining full backward compatibility.

## 🚀 Major New Features

### 1. Multi-Level Configuration Support

Environment variables with double underscores (`__`) are now automatically converted to nested structures:

```bash
# Environment variables
export DATABASE__DEVELOPE__DB_URL="postgresql://localhost:5432/dev"
export DATABASE__DEVELOPE__POOL_SIZE="10"
export LLM__OPENAI__API_KEY="sk-test123"
export LLM__ANTHROPIC__MODEL="claude-3"

# Automatically becomes this nested structure:
{
    "database": {
        "develope": {
            "db_url": "postgresql://localhost:5432/dev",
            "pool_size": 10
        }
    },
    "llm": {
        "openai": {"api_key": "sk-test123"},
        "anthropic": {"model": "claude-3"}
    }
}
```

### 2. Mixed Configuration Formats

You can now define default configuration using both nested dictionaries and flat dot notation:

```python
default_config = {
    # Nested dictionary format
    'database': {
        'develope': {
            'db_url': 'sqlite:///dev.db',
            'pool_size': 5
        }
    },
    
    # Flat dot notation format (existing)
    'llm.openai.api_key': 'default-key',
    'llm.anthropic.model': 'claude-3',
    
    # Simple keys (existing)
    'app_name': 'my-app'
}
```

### 3. Enhanced Environment Variable Filtering

**OS Environment Variables**: Only loaded if they have corresponding defaults (prevents pollution)
**Environment Files**: Load ALL variables regardless of defaults (allows new keys)

```python
# OS env vars: DATABASE__HOST=localhost, RANDOM_VAR=value
# Only DATABASE__HOST is loaded if you have 'database.host' in defaults
# RANDOM_VAR is filtered out to prevent configuration pollution
```

### 4. Advanced Section Access

Access nested configurations with enhanced section support:

```python
config = get_config()

# Direct multi-level access
db_url = config.get('database.develope.db_url')

# Section access (returns entire section)
database_config = config.get('database')
develope_config = config.get('database.develope')
llm_config = config.get('llm')
openai_config = config.get('llm.openai')
```

## 🔧 Enhanced Features

### DotDict Implementation

New internal `DotDict` class provides native dot notation support:

```python
# Both work seamlessly:
value1 = config['database']['develope']['db_url']  # Dictionary style
value2 = config.get('database.develope.db_url')   # Dot notation style
```

### New API Methods

```python
config.to_flat_dict()  # Get flat representation with dot notation keys
```

## 📚 New Documentation

- **`docs/MULTI_LEVEL_CONFIGURATION.md`**: Comprehensive guide to multi-level configuration
- **`demo_multi_level.py`**: Complete working example demonstrating all features
- **Updated README.md**: Enhanced with multi-level examples and filtering explanation

## 🔄 Backward Compatibility

**100% backward compatible!** All existing code continues to work without changes:

```python
# This still works exactly as before
default_config = {
    'database_url': 'sqlite:///app.db',
    'api_key': 'default-key',
    'temperature': 0.7
}
```

## 🎯 Use Cases

### Complex Application Configuration

```python
default_config = {
    'database': {
        'develope': {'db_url': 'sqlite:///dev.db', 'pool_size': 5},
        'production': {'db_url': 'postgresql://prod/db', 'pool_size': 20},
        'test': {'db_url': 'sqlite:///:memory:', 'pool_size': 1}
    },
    'llm': {
        'openai': {'api_key': '', 'model': 'gpt-4', 'temperature': 0.7},
        'anthropic': {'api_key': '', 'model': 'claude-3', 'temperature': 0.5},
        'ollama': {'base_url': 'http://localhost:11434', 'model': 'llama2'}
    },
    'api': {
        'external': {
            'weather': {'key': '', 'timeout': 30},
            'news': {'key': '', 'timeout': 15}
        },
        'rate_limits': {'requests_per_minute': 60}
    }
}
```

### Environment-Specific Overrides

```bash
# Development
export DATABASE__DEVELOPE__DB_URL="postgresql://localhost:5432/dev"
export LLM__OPENAI__API_KEY="sk-dev-key"

# Production  
export DATABASE__PRODUCTION__DB_URL="postgresql://prod.db.com:5432/prod"
export DATABASE__PRODUCTION__POOL_SIZE="50"
export LLM__OPENAI__API_KEY="sk-prod-key"
```

## 🚀 Getting Started

### Installation

```bash
pip install zero-config==0.1.5
```

### Quick Example

```python
from zero_config import setup_environment, get_config

# Define multi-level configuration
default_config = {
    'database': {
        'develope': {'db_url': 'sqlite:///dev.db', 'pool_size': 5}
    },
    'llm.openai.api_key': 'default-key'
}

# Set environment variables
# export DATABASE__DEVELOPE__DB_URL="postgresql://localhost:5432/dev"
# export LLM__OPENAI__API_KEY="sk-real-key"

setup_environment(default_config=default_config)
config = get_config()

# Access nested configuration
db_url = config.get('database.develope.db_url')  # From env var
api_key = config.get('llm.openai.api_key')       # From env var
pool_size = config.get('database.develope.pool_size')  # From defaults

# Access sections
database_config = config.get('database')
llm_config = config.get('llm')
```

## 🔍 Demo and Examples

Run the new demo script to see all features in action:

```bash
python demo_multi_level.py
```

## 📖 Documentation

- **README.md**: Updated with multi-level examples
- **docs/MULTI_LEVEL_CONFIGURATION.md**: Comprehensive guide
- **docs/PACKAGE_CONFLICT_PREVENTION.md**: Package conflict prevention
- **docs/BEST_PRACTICES.md**: Best practices guide

## 🐛 Bug Fixes

- Improved environment variable parsing for complex nested structures
- Better error handling for malformed configuration keys
- Enhanced logging for debugging multi-level configurations

## 🔗 Links

- **GitHub**: https://github.com/xychenmsn/zero-config
- **PyPI**: https://pypi.org/project/zero-config/
- **Documentation**: See `docs/` directory in the repository

## 🙏 Acknowledgments

Thanks to the community for feedback on complex configuration scenarios and the need for better nested structure support. This release addresses those needs while maintaining the simplicity that makes zero-config special.

---

**Full Changelog**: https://github.com/xychenmsn/zero-config/blob/main/CHANGELOG.md
