# Zero Config 🚀

Smart configuration management with layered overrides and type-aware defaults.

## 🎯 Core Concept

Zero Config provides **layered configuration** where each layer can override the previous one:

1. **Application Defaults** → 2. **Environment Variables** → 3. **Environment Files**

```python
from zero_config import setup_environment, get_config

# 1. Define application defaults
default_config = {
    'openai_api_key': '',           # Will be overridden by env var
    'llm.temperature': 0.0,         # Will be overridden by .env file
    'database.host': 'localhost',   # Will stay as default
}

# 2. Set environment variable
# export OPENAI_API_KEY="sk-your-key-here"

# 3. Create .env.zero_config file
# llm.temperature=0.7
# database.port=5432

setup_environment(default_config=default_config)
config = get_config()

# Final configuration:
print(config.get('openai_api_key'))    # "sk-your-key-here" (from env var)
print(config.get('llm.temperature'))   # 0.7 (from .env file, converted to float)
print(config.get('database.host'))     # "localhost" (from defaults)
print(config.get('database.port'))     # 5432 (from .env file, new key as int)
```

## 🏗️ Why Layered Configuration?

- **Defaults in Code**: Your app defines the schema and sensible defaults
- **Environment Variables**: Perfect for deployment-specific overrides (Docker, CI/CD)
- **Environment Files**: Great for local development and secrets management
- **Type Safety**: Environment strings are automatically converted to match your default types

## 🔧 Configuration Sources

### Environment Variables

```bash
# Uppercase env vars automatically override config keys
export OPENAI_API_KEY="sk-your-key-here"    # Becomes: openai_api_key
export DEBUG="true"                         # Becomes: debug (bool)
export MODELS='["gpt-4", "claude-3"]'       # JSON arrays for lists
export DATABASE_URL="host1,host2,host3"     # Strings with commas stay safe

# Section headers with double underscore
export LLM__TEMPERATURE="0.7"               # Becomes: llm.temperature
export DATABASE__HOST="remote.db.com"       # Becomes: database.host
```

### Environment Files

```bash
# .env.zero_config (default) or custom files
openai_api_key=sk-your-local-key
llm.temperature=0.7
database.port=5432
models=["gpt-4", "claude-3"]
```

### Custom Environment Files

```python
setup_environment(
    default_config=default_config,
    env_files="config/production.env"          # Single file
)

setup_environment(
    default_config=default_config,
    env_files=["base.env", "production.env"]   # Multiple files (later wins)
)
```

## 📁 Project Root Detection

**Critical**: Environment files are loaded relative to your project root.

```python
# Auto-detection (looks for .git, pyproject.toml, setup.py, etc.)
setup_environment(default_config=config)

# Override via environment variable
# export PROJECT_ROOT="/path/to/project"
setup_environment(default_config=config)
```

**Why it matters**: Zero Config needs to know your project root to:

- Load `.env.zero_config` from the correct location
- Resolve relative paths in `env_files` parameter
- Provide accurate dynamic path helpers (`config.data_path()`, etc.)

## 🛠️ Advanced Features

### Dynamic Path Helpers

```python
config = get_config()

# Any directory name + '_path' works (Ruby on Rails style)
config.data_path('database.db')      # /project/data/database.db
config.logs_path('app.log')          # /project/logs/app.log
config.cache_path('session.json')    # /project/cache/session.json
config.models_path('gpt4.bin')       # /project/models/gpt4.bin
```

### Section Configuration

```python
# Define sections with dot notation
default_config = {
    'llm.models': ['gpt-4'],
    'llm.temperature': 0.0,
    'database.host': 'localhost',
    'database.port': 5432,
}

config = get_config()
llm_config = config.get('llm')      # {'models': [...], 'temperature': 0.0}
db_config = config.get('database')  # {'host': 'localhost', 'port': 5432}
```

### Type Conversion

Environment variables are automatically converted to match your default types:

- **Numbers**: `"8000"` → `8000` (int), `"0.7"` → `0.7` (float)
- **Booleans**: `"true"` → `True`, `"false"` → `False`
- **Lists**: `'["a","b"]'` → `['a','b']` (JSON only - comma strings stay safe)
- **Strings**: Always preserved as-is (safe for URLs, CSVs, etc.)

## 📦 Installation

```bash
pip install zero-config
```

## 🛡️ Package Conflict Prevention

**Critical for libraries**: Zero Config prevents configuration conflicts when both your main project and its dependencies use zero-config.

### The Problem

Without protection, packages can accidentally overwrite your main project's configuration:

```python
# ❌ Without protection (old behavior)
# Main project sets up config
setup_environment(default_config={'app_name': 'news_app', 'llm.api_key': 'main-key'})

# Package dependency overwrites everything!
setup_environment(default_config={'package_name': 'united_llm'})

# Main project's config is lost 😱
config = get_config()
print(config.get('app_name'))  # None - lost!
```

### The Solution

Zero Config now automatically prevents this:

```python
# ✅ With protection (new behavior)
# Main project initializes first
setup_environment(default_config={'app_name': 'news_app', 'llm.api_key': 'main-key'})

# Package dependency tries to initialize (safely ignored)
setup_environment(default_config={'package_name': 'united_llm'})  # ← Ignored!

# Main project's config is preserved 🎉
config = get_config()
print(config.get('app_name'))      # "news_app" (preserved)
print(config.get('package_name'))  # None (package config ignored)
```

### How It Works

1. **First Call Wins**: The first `setup_environment()` call initializes the global configuration
2. **Automatic Protection**: Subsequent calls are automatically ignored with helpful logging
3. **Shared Access**: Packages can still access the main project's configuration
4. **Override Available**: Use `force_reinit=True` only for testing or special cases

### Best Practices

**For Main Applications:**

```python
# Initialize early in your main application
def main():
    setup_environment(default_config=your_app_config)
    # ... rest of your app
```

**For Package Libraries:**

```python
# Packages should call setup_environment but expect it might be ignored
def initialize_package():
    # This will be ignored if main app already initialized
    setup_environment(default_config=package_defaults)

    # Always access config this way
    config = get_config()
    return config.get('llm')  # Access main app's LLM config
```

## 🔗 API Reference

```python
# Setup
setup_environment(
    default_config={...},           # Your app's defaults
    env_files="custom.env",         # Optional: custom env file(s)
    force_reinit=False              # Force re-init (use with caution)
)

# Access
config = get_config()
config.get('key', default)         # Safe access with fallback
config['key']                      # Direct access (raises KeyError if missing)
config.get('llm')                 # Get all llm.* keys as dict
config.to_dict()                   # Get all config as dict

# Initialization status
is_initialized()                   # Check if already initialized
get_initialization_info()          # Get info about who initialized

# Dynamic paths (Ruby on Rails style)
config.data_path('file.db')        # /project/data/file.db
config.logs_path('app.log')        # /project/logs/app.log
config.any_name_path('file')       # /project/any_name/file
```

## 🔍 Debugging & Troubleshooting

### Check Initialization Status

```python
from zero_config import is_initialized, get_initialization_info

# Check if zero-config has been initialized
if is_initialized():
    print(f"Initialized by: {get_initialization_info()}")
else:
    print("Not yet initialized")
```

### Common Issues

**Issue**: `RuntimeError: Configuration not initialized`

```python
# ❌ Trying to get config before setup
config = get_config()  # Error!

# ✅ Always call setup_environment first
setup_environment()
config = get_config()  # Works!
```

**Issue**: Package config not working

```python
# ❌ Package trying to override main config
setup_environment(default_config=package_config)  # Ignored!

# ✅ Package accessing main config
setup_environment(default_config=package_config)  # Ignored (expected)
config = get_config()  # Access main app's config
llm_config = config.get('llm')  # Get LLM section from main app
```

**Issue**: Need to reset for testing

```python
# ✅ For testing only
from zero_config.config import _reset_for_testing

def test_something():
    _reset_for_testing()  # Reset global state
    setup_environment(test_config)
    # ... test code
```

### Logging

Zero Config provides helpful logging. Enable it to see what's happening:

```python
import logging
logging.basicConfig(level=logging.INFO)

setup_environment(default_config=config)
# INFO: Auto-detected project root: /path/to/project
# INFO: 🚀 Environment setup complete
```

## 🚀 Migration Guide

### From v0.1.0 to v0.1.1+

**No breaking changes!** Your existing code continues to work. New features:

- ✅ Automatic package conflict prevention
- ✅ New `is_initialized()` and `get_initialization_info()` functions
- ✅ New `force_reinit=True` parameter for special cases

### Upgrading Your Package

If you maintain a package that uses zero-config:

```python
# Before (still works)
def initialize():
    setup_environment(default_config=defaults)

# After (recommended - more explicit)
def initialize():
    if not is_initialized():
        setup_environment(default_config=defaults)
    return get_config()
```
