# Multi-Level Configuration

This document explains zero-config's multi-level configuration support introduced in v0.1.5+.

## 🎯 Overview

Zero-config now supports complex nested configurations with multiple levels of hierarchy. This allows you to organize your configuration in a structured way while maintaining backward compatibility.

## 🔧 Key Features

### 1. Environment Variable Conversion

Environment variables with double underscores (`__`) are automatically converted to nested structure:

```bash
# Environment variables
export DATABASE__DEVELOPE__DB_URL="postgresql://localhost:5432/dev"
export DATABASE__DEVELOPE__POOL_SIZE="10"
export DATABASE__PRODUCTION__DB_URL="postgresql://prod.db.com:5432/prod"
export LLM__OPENAI__API_KEY="sk-test123"
export LLM__OPENAI__MODEL="gpt-4"
export LLM__ANTHROPIC__API_KEY="claude-key"

# Becomes this nested structure:
{
    "database": {
        "develope": {
            "db_url": "postgresql://localhost:5432/dev",
            "pool_size": 10  # Automatically converted to int
        },
        "production": {
            "db_url": "postgresql://prod.db.com:5432/prod"
        }
    },
    "llm": {
        "openai": {
            "api_key": "sk-test123",
            "model": "gpt-4"
        },
        "anthropic": {
            "api_key": "claude-key"
        }
    }
}
```

### 2. Mixed Configuration Formats

You can define default configuration using both nested dictionaries and flat dot notation:

```python
default_config = {
    # Nested dictionary format
    'database': {
        'develope': {
            'db_url': 'sqlite:///dev.db',
            'pool_size': 5,
            'timeout': 30
        }
    },
    
    # Flat dot notation format
    'llm.openai.api_key': 'default-openai-key',
    'llm.openai.model': 'gpt-3.5-turbo',
    'llm.anthropic.api_key': 'default-anthropic-key',
    
    # Simple keys
    'app_name': 'my-app',
    'debug': False
}
```

### 3. Dot Notation Access

Access nested configuration using dot notation:

```python
config = get_config()

# Direct access to nested values
db_url = config.get('database.develope.db_url')
api_key = config.get('llm.openai.api_key')
pool_size = config.get('database.develope.pool_size')

# Section access (returns entire section as dict)
database_config = config.get('database')
llm_config = config.get('llm')
develope_config = config.get('database.develope')
openai_config = config.get('llm.openai')

# Traditional access still works
app_name = config.get('app_name')
debug = config.get('debug')
```

## 🔄 Environment Variable Filtering

### OS Environment Variables (Filtered)

OS environment variables are only loaded if they have corresponding defaults:

```python
# You have these OS environment variables:
# DATABASE__DEVELOPE__DB_URL=postgresql://localhost:5432/dev  ← Will be loaded
# DATABASE__DEVELOPE__POOL_SIZE=10                           ← Will be loaded
# RANDOM_SYSTEM_VAR=some_value                               ← Will be IGNORED
# PATH=/usr/bin:/bin                                         ← Will be IGNORED

default_config = {
    'database.develope.db_url': 'sqlite:///default.db',  # Has default
    'database.develope.pool_size': 5,                    # Has default
    # No default for RANDOM_SYSTEM_VAR or PATH
}

setup_environment(default_config=default_config)
config = get_config()

# Only variables with defaults are loaded
print(config.get('database.develope.db_url'))    # "postgresql://localhost:5432/dev"
print(config.get('database.develope.pool_size')) # 10
print(config.get('random_system_var'))           # None (filtered out)
```

### Environment Files (Load All)

Environment files load ALL variables regardless of defaults:

```bash
# .env.zero_config
DATABASE__DEVELOPE__DB_URL=postgresql://localhost:5432/env
DATABASE__DEVELOPE__POOL_SIZE=15
NEW_VAR_FROM_ENV=should_be_loaded
ANOTHER_NEW_VAR=also_should_be_loaded
```

```python
# All variables from env files are loaded, even without defaults
config = get_config()
print(config.get('new_var_from_env'))    # "should_be_loaded"
print(config.get('another_new_var'))     # "also_should_be_loaded"
```

## 🏗️ Internal Implementation

### DotDict Class

Zero-config uses a custom `DotDict` class that supports both dictionary and dot notation access:

```python
# Both of these work:
value1 = config['database']['develope']['db_url']  # Dictionary style
value2 = config.get('database.develope.db_url')   # Dot notation style
```

### Configuration Storage

Internally, all configuration is stored as a multi-level nested dictionary, but you can access it using:

- Dot notation: `config.get('database.develope.db_url')`
- Dictionary access: `config['database']['develope']['db_url']`
- Section access: `config.get('database')` returns the entire database section
- Flat representation: `config.to_flat_dict()` returns all keys in dot notation

## 📋 Best Practices

### 1. Organize by Domain

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
        'external': {
            'weather': {...},
            'news': {...}
        },
        'internal': {...}
    }
}
```

### 2. Use Environment Variables for Deployment

```bash
# Development
export DATABASE__DEVELOPE__DB_URL="postgresql://localhost:5432/dev"

# Production
export DATABASE__PRODUCTION__DB_URL="postgresql://prod.db.com:5432/prod"
export DATABASE__PRODUCTION__POOL_SIZE="20"
```

### 3. Use Environment Files for Local Development

```bash
# .env.zero_config
database.develope.db_url=postgresql://localhost:5432/local_dev
llm.openai.api_key=sk-local-dev-key
debug=true
```

## 🔍 Examples

See `examples/demo_multi_level.py` for a complete working example demonstrating all multi-level configuration features.

## 🚀 Migration from Flat Configuration

Existing flat configurations continue to work without changes:

```python
# This still works exactly as before
default_config = {
    'database_url': 'sqlite:///app.db',
    'llm_api_key': 'default-key',
    'temperature': 0.7
}
```

You can gradually migrate to multi-level configuration:

```python
# Gradual migration
default_config = {
    # Old flat style (still works)
    'database_url': 'sqlite:///app.db',
    
    # New multi-level style
    'llm': {
        'openai': {
            'api_key': 'default-key',
            'temperature': 0.7
        }
    }
}
```
