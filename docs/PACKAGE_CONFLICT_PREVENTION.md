# Package Conflict Prevention

This document explains zero-config's package conflict prevention mechanism in detail.

## 🎯 The Problem

When both a main application and its package dependencies use zero-config, there's a risk of configuration conflicts:

```python
# Main application
setup_environment(default_config={
    'app_name': 'news_app',
    'llm.api_key': 'sk-main-key',
    'llm.temperature': 0.3
})

# Package dependency (united_llm) accidentally overwrites config
setup_environment(default_config={
    'package_name': 'united_llm',
    'llm.temperature': 0.7  # Overwrites main app's setting!
})

# Main app's configuration is lost! 😱
config = get_config()
print(config.get('app_name'))  # None - lost!
print(config.get('llm.temperature'))  # 0.7 - overwritten!
```

## 🛡️ The Solution

Zero-config v0.1.1+ automatically prevents this with **initialization protection**:

1. **First Call Wins**: The first `setup_environment()` call initializes the global configuration
2. **Subsequent Calls Ignored**: Later calls are automatically ignored with helpful logging
3. **Shared Access**: All packages can still access the configuration
4. **Override Available**: `force_reinit=True` available for special cases

## 🔧 How It Works

### Global State Tracking

Zero-config maintains global state to track initialization:

```python
# Internal global variables
_is_initialized = False      # Tracks if setup_environment has been called
_initialized_by = None       # Tracks who called it (file:line)
_config = None              # The actual configuration object
_project_root = None        # The project root path
```

### Protection Logic

```python
def setup_environment(default_config=None, env_files=None, force_reinit=False):
    global _is_initialized, _initialized_by
    
    # Check if already initialized
    if _is_initialized and not force_reinit:
        # Log helpful information and return early
        logging.info("🔄 Zero-config already initialized")
        logging.info("   Skipping re-initialization to prevent conflicts")
        return
    
    # Record who is initializing
    _initialized_by = get_caller_info()
    
    # Proceed with initialization...
    _is_initialized = True
```

### Caller Tracking

Zero-config tracks who initialized the configuration for debugging:

```python
from zero_config import get_initialization_info

print(get_initialization_info())
# Output: "/path/to/main.py:25"
```

## 📋 API Reference

### New Functions

```python
# Check initialization status
is_initialized() -> bool
# Returns True if setup_environment has been called

get_initialization_info() -> Optional[str]
# Returns "file:line" of who initialized, or None if not initialized

# Force re-initialization (use with caution)
setup_environment(force_reinit=True)
# Allows overriding existing configuration
```

### Enhanced Functions

```python
setup_environment(
    default_config={...},
    env_files="custom.env",
    force_reinit=False  # New parameter
)
```

## 🚀 Usage Patterns

### For Main Applications

```python
# main.py
from zero_config import setup_environment

def main():
    # Initialize configuration early
    config = {
        'app_name': 'my_app',
        'database.host': 'localhost',
        'llm.api_key': '',
    }
    
    setup_environment(default_config=config)
    
    # Rest of application...
    start_app()

if __name__ == "__main__":
    main()
```

### For Package Libraries

```python
# my_package/__init__.py
from zero_config import setup_environment, get_config

def get_package_config():
    """Get configuration for this package."""
    # Define package defaults
    package_defaults = {
        'llm.temperature': 0.7,
        'llm.timeout': 30,
        'package.retries': 3
    }
    
    # This will be ignored if main app already initialized
    setup_environment(default_config=package_defaults)
    
    # Always get the actual config (from main app or package defaults)
    return get_config()

class MyPackageClass:
    def __init__(self):
        config = get_package_config()
        
        # Access configuration
        self.temperature = config.get('llm.temperature', 0.7)
        self.timeout = config.get('llm.timeout', 30)
        
        # Access main app's LLM section if available
        llm_config = config.get('llm', {})
        self.api_key = llm_config.get('api_key', '')
```

### Defensive Programming

```python
from zero_config import get_config, is_initialized

def get_safe_config():
    """Get configuration with fallbacks."""
    if is_initialized():
        return get_config()
    else:
        # Fallback to environment variables or defaults
        return {
            'llm.temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
            'llm.timeout': int(os.getenv('LLM_TIMEOUT', '30'))
        }
```

## 🧪 Testing

### Test Isolation

Always reset state between tests:

```python
import pytest
from zero_config.config import _reset_for_testing

class TestMyFeature:
    def setup_method(self):
        """Reset zero-config state before each test."""
        _reset_for_testing()
    
    def test_something(self):
        setup_environment(default_config=test_config)
        # ... test code
```

### Testing Package Conflicts

```python
def test_package_conflict_prevention():
    _reset_for_testing()
    
    # Main app initializes
    setup_environment(default_config={'main': True, 'key': 'main_value'})
    
    # Package tries to initialize (should be ignored)
    setup_environment(default_config={'package': True, 'key': 'package_value'})
    
    # Verify main app config is preserved
    config = get_config()
    assert config.get('main') is True
    assert config.get('key') == 'main_value'
    assert config.get('package') is None
```

## 🔍 Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

setup_environment(default_config=config)
# INFO: 🚀 Environment setup complete
# INFO:    Initialized by: /path/to/main.py:25

# Later package initialization
setup_environment(default_config=package_config)
# INFO: 🔄 Zero-config already initialized by /path/to/main.py:25
# INFO:    Subsequent call from: /path/to/package.py:15
# INFO:    Skipping re-initialization to prevent conflicts
```

### Check Status

```python
from zero_config import is_initialized, get_initialization_info

if is_initialized():
    print(f"Zero-config initialized by: {get_initialization_info()}")
else:
    print("Zero-config not yet initialized")
```

## ⚠️ Important Notes

### When to Use force_reinit=True

**Rarely!** Only use `force_reinit=True` in these specific cases:

1. **Testing**: When you need to reset configuration between tests
2. **Development Tools**: When building configuration management tools
3. **Error Recovery**: When you need to recover from a misconfigured state

**Never use in production packages** - it will break the main application's configuration.

### Backward Compatibility

The package conflict prevention is **100% backward compatible**:

- Existing code continues to work unchanged
- No breaking changes to the API
- New features are opt-in

### Performance Impact

The protection mechanism has minimal performance impact:

- Simple boolean check on subsequent calls
- No additional overhead for the first initialization
- Logging is only enabled when explicitly configured

## 🎯 Real-World Example

Here's how the news app + united_llm scenario works with protection:

```python
# news_app/main.py
setup_environment(default_config={
    'app_name': 'news_app',
    'llm.api_key': 'sk-news-key',
    'llm.temperature': 0.3,
    'database.host': 'news.db.com'
})

# united_llm package (imported by news app)
# This call is automatically ignored
setup_environment(default_config={
    'package_name': 'united_llm',
    'llm.temperature': 0.7,  # Would override news app's setting
    'llm.timeout': 30
})

# Result: News app's configuration is preserved
config = get_config()
print(config.get('app_name'))        # "news_app" ✅
print(config.get('llm.temperature')) # 0.3 ✅ (news app's value)
print(config.get('package_name'))    # None ✅ (package config ignored)

# But united_llm can still access news app's LLM config
llm_config = config.get('llm')
api_key = llm_config.get('api_key')  # "sk-news-key" ✅
```

This ensures that:
- ✅ Main application controls the configuration
- ✅ Packages can't accidentally break the main app
- ✅ Packages can still access the configuration they need
- ✅ Clear logging shows what's happening
- ✅ No breaking changes to existing code
