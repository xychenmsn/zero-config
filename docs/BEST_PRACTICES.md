# Zero Config Best Practices

This guide covers best practices for using zero-config effectively in different scenarios.

## 🏗️ Application Architecture

### Main Applications

**Initialize Early and Once**
```python
# main.py or app.py
from zero_config import setup_environment

def main():
    # Initialize configuration as early as possible
    config = {
        'app_name': 'my_awesome_app',
        'database.host': 'localhost',
        'database.port': 5432,
        'llm.api_key': '',
        'llm.temperature': 0.7,
        'debug': False
    }
    
    setup_environment(default_config=config)
    
    # Rest of your application
    start_application()

if __name__ == "__main__":
    main()
```

**Environment-Specific Configuration**
```python
# Use different env files for different environments
import os

env = os.getenv('ENVIRONMENT', 'development')
env_files = [
    '.env.zero_config',           # Base configuration
    f'.env.{env}'                 # Environment-specific overrides
]

setup_environment(
    default_config=base_config,
    env_files=env_files
)
```

### Package Libraries

**Safe Initialization Pattern**
```python
# your_package/__init__.py
from zero_config import setup_environment, get_config, is_initialized

def get_package_config():
    """Get configuration for this package."""
    # Try to initialize with package defaults
    # This will be ignored if main app already initialized
    package_defaults = {
        'package.timeout': 30,
        'package.retries': 3,
        'llm.temperature': 0.5  # Fallback if main app doesn't set this
    }
    
    setup_environment(default_config=package_defaults)
    
    # Always get the actual config (from main app or package defaults)
    return get_config()

def initialize():
    """Initialize the package."""
    config = get_package_config()
    
    # Access configuration
    timeout = config.get('package.timeout', 30)
    llm_config = config.get('llm', {})
    
    return SomePackageClass(timeout=timeout, llm_config=llm_config)
```

**Defensive Configuration Access**
```python
def get_llm_config():
    """Get LLM configuration with sensible fallbacks."""
    try:
        config = get_config()
        llm_section = config.get('llm', {})
        
        return {
            'api_key': llm_section.get('api_key', ''),
            'temperature': llm_section.get('temperature', 0.7),
            'max_tokens': llm_section.get('max_tokens', 1000),
            'model': llm_section.get('model', 'gpt-3.5-turbo')
        }
    except RuntimeError:
        # Zero-config not initialized, return defaults
        return {
            'api_key': '',
            'temperature': 0.7,
            'max_tokens': 1000,
            'model': 'gpt-3.5-turbo'
        }
```

## 🔧 Configuration Design

### Naming Conventions

**Use Descriptive, Hierarchical Names**
```python
# ✅ Good - Clear hierarchy and purpose
config = {
    'database.host': 'localhost',
    'database.port': 5432,
    'database.ssl.enabled': True,
    'database.ssl.cert_path': '/path/to/cert',
    
    'llm.openai.api_key': '',
    'llm.openai.model': 'gpt-4',
    'llm.anthropic.api_key': '',
    'llm.anthropic.model': 'claude-3',
    
    'logging.level': 'INFO',
    'logging.format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# ❌ Avoid - Flat, unclear names
config = {
    'db_host': 'localhost',
    'openai_key': '',
    'log_level': 'INFO'
}
```

**Environment Variable Mapping**
```bash
# Hierarchical config maps to env vars with double underscore
export DATABASE__HOST="production.db.com"
export DATABASE__PORT="5432"
export LLM__OPENAI__API_KEY="sk-your-key"
export LLM__OPENAI__MODEL="gpt-4"
```

### Type Safety

**Define Types Through Defaults**
```python
# ✅ Good - Types are clear from defaults
config = {
    'port': 8000,              # int
    'temperature': 0.7,        # float
    'debug': False,            # bool
    'models': ['gpt-4'],       # list
    'api_key': '',             # string
}

# Environment variables will be converted to match these types
# PORT="3000" → 3000 (int)
# TEMPERATURE="0.8" → 0.8 (float)
# DEBUG="true" → True (bool)
# MODELS='["gpt-4", "claude-3"]' → ['gpt-4', 'claude-3'] (list)
```

**Handle Lists Carefully**
```python
# ✅ For lists, use JSON format in env vars
export MODELS='["gpt-4", "claude-3", "gemini-pro"]'

# ✅ Comma-containing strings are preserved safely
export DATABASE_URL="host1,host2,host3"  # Stays as single string

# ❌ Avoid comma-separated lists - they're not supported
# export MODELS="gpt-4,claude-3"  # This becomes ["gpt-4,claude-3"]
```

## 🛡️ Security Best Practices

### Sensitive Data

**Use Environment Variables for Secrets**
```python
# ✅ Good - Secrets come from environment
config = {
    'api_key': '',              # Empty default, set via env var
    'database_password': '',    # Empty default, set via env var
    'jwt_secret': '',          # Empty default, set via env var
}

# Set in environment or .env file (not in version control)
# export API_KEY="sk-your-secret-key"
```

**Separate Public and Private Config**
```python
# config/base.py - Safe to commit
BASE_CONFIG = {
    'app_name': 'my_app',
    'database.host': 'localhost',
    'database.port': 5432,
    'api_key': '',  # Will be set via environment
}

# .env.local - NOT in version control
# API_KEY=sk-your-secret-key
# DATABASE_PASSWORD=your-secret-password
```

### Environment Files

**Use Multiple Environment Files**
```
.env.zero_config      # Base configuration (can be committed)
.env.local           # Local overrides (never commit)
.env.production      # Production settings (deploy separately)
.env.test           # Test environment settings
```

```python
# Load appropriate files based on environment
import os

env = os.getenv('ENVIRONMENT', 'development')
env_files = ['.env.zero_config']

if env == 'production':
    env_files.append('.env.production')
elif env == 'test':
    env_files.append('.env.test')
else:
    env_files.append('.env.local')  # Development

setup_environment(default_config=config, env_files=env_files)
```

## 🧪 Testing

### Test Isolation

**Always Reset State in Tests**
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

**Use Fixtures for Common Setup**
```python
@pytest.fixture
def clean_config():
    """Provide a clean zero-config state."""
    _reset_for_testing()
    yield
    _reset_for_testing()

def test_with_clean_config(clean_config):
    setup_environment(default_config={'test': True})
    # ... test code
```

### Mock Environment Variables

```python
from unittest.mock import patch

def test_env_var_override():
    _reset_for_testing()
    
    with patch.dict(os.environ, {
        'API_KEY': 'test-key',
        'DEBUG': 'true'
    }, clear=True):
        setup_environment(default_config={
            'api_key': '',
            'debug': False
        })
        
        config = get_config()
        assert config.get('api_key') == 'test-key'
        assert config.get('debug') is True
```

## 🚀 Deployment

### Docker

```dockerfile
# Dockerfile
FROM python:3.11

# Set environment variables
ENV ENVIRONMENT=production
ENV DATABASE__HOST=prod.db.com
ENV DATABASE__PORT=5432

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run application
CMD ["python", "main.py"]
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE__HOST
          value: "postgres-service"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api-key
```

## 🔍 Debugging

### Enable Logging

```python
import logging

# Enable zero-config logging
logging.basicConfig(level=logging.INFO)

setup_environment(default_config=config)
# INFO: Auto-detected project root: /path/to/project
# INFO: 🚀 Environment setup complete
# INFO: Initialized by: /path/to/main.py:25
```

### Check Initialization Status

```python
from zero_config import is_initialized, get_initialization_info

if is_initialized():
    print(f"Zero-config initialized by: {get_initialization_info()}")
    config = get_config()
    print(f"Current config keys: {list(config.to_dict().keys())}")
else:
    print("Zero-config not yet initialized")
```

### Common Issues

**Issue**: Configuration not loading
```python
# Check if files exist and are readable
import os
from pathlib import Path

config_file = Path('.env.zero_config')
if config_file.exists():
    print(f"Config file exists: {config_file.absolute()}")
    print(f"Content: {config_file.read_text()}")
else:
    print(f"Config file not found at: {config_file.absolute()}")
```

**Issue**: Package conflicts
```python
# Check who initialized first
if is_initialized():
    print(f"Already initialized by: {get_initialization_info()}")
    print("Subsequent setup_environment calls will be ignored")
```
