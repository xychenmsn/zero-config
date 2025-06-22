# Zero Config Examples

This document provides practical examples of using zero-config in different scenarios.

## 🚀 Quick Start

### Basic Usage

```python
from zero_config import setup_environment, get_config

# Define your application's configuration schema
config = {
    'app_name': 'my_app',
    'database.host': 'localhost',
    'database.port': 5432,
    'api_key': '',
    'debug': False
}

# Initialize zero-config
setup_environment(default_config=config)

# Access configuration anywhere in your app
config = get_config()
print(f"App: {config.get('app_name')}")
print(f"DB: {config.get('database.host')}:{config.get('database.port')}")
```

### With Environment Variables

```bash
# Set environment variables
export APP_NAME="Production App"
export DATABASE__HOST="prod.db.com"
export DATABASE__PORT="5432"
export API_KEY="sk-your-api-key"
export DEBUG="true"
```

```python
# Same code - environment variables automatically override defaults
setup_environment(default_config=config)
config = get_config()

print(config.get('app_name'))      # "Production App" (from env var)
print(config.get('database.host')) # "prod.db.com" (from env var)
print(config.get('debug'))         # True (from env var, converted to bool)
```

## 🏢 Real-World Applications

### Web Application (FastAPI)

```python
# app/config.py
from zero_config import setup_environment, get_config

# Application configuration schema
APP_CONFIG = {
    'app.name': 'My Web App',
    'app.version': '1.0.0',
    'app.debug': False,
    
    'server.host': '0.0.0.0',
    'server.port': 8000,
    'server.workers': 1,
    
    'database.url': 'sqlite:///./app.db',
    'database.echo': False,
    
    'auth.secret_key': '',
    'auth.algorithm': 'HS256',
    'auth.expire_minutes': 30,
    
    'logging.level': 'INFO',
    'logging.format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

def init_config():
    setup_environment(default_config=APP_CONFIG)
    return get_config()

# app/main.py
from fastapi import FastAPI
from app.config import init_config

# Initialize configuration
config = init_config()

# Create FastAPI app
app = FastAPI(
    title=config.get('app.name'),
    version=config.get('app.version'),
    debug=config.get('app.debug')
)

# Use configuration throughout the app
@app.get("/health")
def health_check():
    return {
        "app": config.get('app.name'),
        "version": config.get('app.version'),
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.get('server.host'),
        port=config.get('server.port'),
        workers=config.get('server.workers')
    )
```

### Data Processing Pipeline

```python
# pipeline/config.py
PIPELINE_CONFIG = {
    'input.source': 'local',
    'input.path': './data/input',
    'input.format': 'csv',
    
    'processing.batch_size': 1000,
    'processing.parallel': True,
    'processing.workers': 4,
    
    'output.destination': 'local',
    'output.path': './data/output',
    'output.format': 'parquet',
    
    'llm.provider': 'openai',
    'llm.model': 'gpt-3.5-turbo',
    'llm.api_key': '',
    'llm.temperature': 0.1,
    'llm.max_tokens': 1000,
    
    'monitoring.enabled': True,
    'monitoring.interval': 60
}

# pipeline/main.py
from zero_config import setup_environment, get_config
from pipeline.config import PIPELINE_CONFIG

def main():
    # Initialize configuration
    setup_environment(default_config=PIPELINE_CONFIG)
    config = get_config()
    
    # Get configuration sections
    input_config = config.get('input')
    processing_config = config.get('processing')
    llm_config = config.get('llm')
    
    # Initialize components
    data_loader = DataLoader(**input_config)
    processor = DataProcessor(**processing_config)
    llm_client = LLMClient(**llm_config)
    
    # Run pipeline
    for batch in data_loader.load_batches():
        processed_batch = processor.process(batch)
        enhanced_batch = llm_client.enhance(processed_batch)
        save_batch(enhanced_batch)

if __name__ == "__main__":
    main()
```

## 📦 Package Development

### Creating a Zero-Config Package

```python
# my_llm_package/__init__.py
from zero_config import setup_environment, get_config, is_initialized

# Package defaults
PACKAGE_DEFAULTS = {
    'llm.temperature': 0.7,
    'llm.max_tokens': 1000,
    'llm.timeout': 30,
    'llm.retries': 3,
    'package.name': 'my_llm_package',
    'package.version': '1.0.0'
}

def get_llm_config():
    """Get LLM configuration, with package defaults as fallback."""
    # This will be ignored if main app already initialized zero-config
    setup_environment(default_config=PACKAGE_DEFAULTS)
    
    config = get_config()
    return config.get('llm', {})

class LLMClient:
    def __init__(self, custom_config=None):
        # Get configuration
        if custom_config:
            self.config = custom_config
        else:
            self.config = get_llm_config()
        
        # Initialize with config
        self.api_key = self.config.get('api_key', '')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        if not self.api_key:
            raise ValueError("LLM API key not configured")
    
    def generate(self, prompt):
        # Use self.config for LLM calls
        pass

# Usage in main application
def main():
    # Main app initializes zero-config first
    main_config = {
        'app_name': 'my_app',
        'llm.api_key': 'sk-main-app-key',
        'llm.temperature': 0.5,  # Override package default
        'llm.model': 'gpt-4'
    }
    setup_environment(default_config=main_config)
    
    # Package uses main app's configuration
    llm = LLMClient()  # Will use main app's LLM config
    result = llm.generate("Hello, world!")
```

### Package with Graceful Fallbacks

```python
# smart_package/__init__.py
from zero_config import get_config, is_initialized
import os

def get_package_config():
    """Get configuration with multiple fallback strategies."""
    
    # Strategy 1: Use zero-config if available
    if is_initialized():
        config = get_config()
        return {
            'api_key': config.get('api_key', ''),
            'timeout': config.get('timeout', 30),
            'retries': config.get('retries', 3)
        }
    
    # Strategy 2: Use environment variables directly
    env_config = {
        'api_key': os.getenv('API_KEY', ''),
        'timeout': int(os.getenv('TIMEOUT', '30')),
        'retries': int(os.getenv('RETRIES', '3'))
    }
    
    if env_config['api_key']:
        return env_config
    
    # Strategy 3: Use package defaults
    return {
        'api_key': '',
        'timeout': 30,
        'retries': 3
    }

class SmartClient:
    def __init__(self):
        self.config = get_package_config()
        
        if not self.config['api_key']:
            print("Warning: No API key configured. Some features may not work.")
    
    def call_api(self):
        if not self.config['api_key']:
            return {"error": "No API key configured"}
        
        # Make API call with configuration
        pass
```

## 🔧 Advanced Configuration Patterns

### Multi-Environment Setup

```python
# config/environments.py
import os
from zero_config import setup_environment

# Base configuration
BASE_CONFIG = {
    'app.name': 'My App',
    'app.version': '1.0.0',
    'database.host': 'localhost',
    'database.port': 5432,
    'redis.host': 'localhost',
    'redis.port': 6379,
    'logging.level': 'INFO'
}

# Environment-specific configurations
ENVIRONMENTS = {
    'development': {
        'app.debug': True,
        'database.echo': True,
        'logging.level': 'DEBUG'
    },
    'testing': {
        'app.debug': False,
        'database.url': 'sqlite:///:memory:',
        'logging.level': 'WARNING'
    },
    'production': {
        'app.debug': False,
        'database.ssl': True,
        'logging.level': 'ERROR'
    }
}

def setup_config():
    """Setup configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Merge base config with environment-specific config
    config = BASE_CONFIG.copy()
    if env in ENVIRONMENTS:
        config.update(ENVIRONMENTS[env])
    
    # Setup environment files
    env_files = ['.env.zero_config']
    env_file = f'.env.{env}'
    if os.path.exists(env_file):
        env_files.append(env_file)
    
    setup_environment(default_config=config, env_files=env_files)
    return get_config()
```

### Dynamic Configuration

```python
# config/dynamic.py
from zero_config import setup_environment, get_config
import json
import os

def load_dynamic_config():
    """Load configuration from multiple sources dynamically."""
    
    # Start with base configuration
    config = {
        'app.name': 'Dynamic App',
        'features.enabled': []
    }
    
    # Load feature flags from JSON file
    features_file = 'config/features.json'
    if os.path.exists(features_file):
        with open(features_file) as f:
            features = json.load(f)
            config.update(features)
    
    # Load database configuration from separate file
    db_config_file = 'config/database.json'
    if os.path.exists(db_config_file):
        with open(db_config_file) as f:
            db_config = json.load(f)
            for key, value in db_config.items():
                config[f'database.{key}'] = value
    
    setup_environment(default_config=config)
    return get_config()

# Usage
config = load_dynamic_config()
enabled_features = config.get('features.enabled', [])
if 'new_ui' in enabled_features:
    # Enable new UI
    pass
```

### Configuration Validation

```python
# config/validation.py
from zero_config import setup_environment, get_config
from typing import Dict, Any
import sys

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration values."""
    
    required_keys = [
        'app.name',
        'database.host',
        'api_key'
    ]
    
    # Check required keys
    for key in required_keys:
        if not config.get(key):
            print(f"Error: Required configuration key '{key}' is missing or empty")
            return False
    
    # Validate types
    if not isinstance(config.get('database.port'), int):
        print("Error: database.port must be an integer")
        return False
    
    # Validate ranges
    port = config.get('database.port', 0)
    if not (1 <= port <= 65535):
        print(f"Error: database.port must be between 1 and 65535, got {port}")
        return False
    
    return True

def setup_validated_config(default_config: Dict[str, Any]):
    """Setup configuration with validation."""
    setup_environment(default_config=default_config)
    config = get_config()
    
    if not validate_config(config.to_dict()):
        print("Configuration validation failed")
        sys.exit(1)
    
    print("✅ Configuration validation passed")
    return config

# Usage
config = setup_validated_config({
    'app.name': 'Validated App',
    'database.host': 'localhost',
    'database.port': 5432,
    'api_key': ''  # Will be set via environment
})
```

## 🧪 Testing Examples

### Test Configuration

```python
# tests/conftest.py
import pytest
from zero_config.config import _reset_for_testing
from zero_config import setup_environment

@pytest.fixture(autouse=True)
def reset_config():
    """Reset zero-config state before each test."""
    _reset_for_testing()
    yield
    _reset_for_testing()

@pytest.fixture
def test_config():
    """Provide test configuration."""
    config = {
        'app.name': 'Test App',
        'database.url': 'sqlite:///:memory:',
        'api_key': 'test-key',
        'debug': True
    }
    setup_environment(default_config=config)
    return get_config()

# tests/test_app.py
def test_app_initialization(test_config):
    """Test app initialization with test config."""
    from myapp import create_app
    
    app = create_app()
    assert app.config['app_name'] == 'Test App'
    assert app.config['debug'] is True

def test_database_connection(test_config):
    """Test database connection with test config."""
    from myapp.database import get_connection
    
    conn = get_connection()
    assert conn is not None
    # Test with in-memory SQLite database
```

### Mocking Environment Variables

```python
# tests/test_env_vars.py
import os
from unittest.mock import patch
from zero_config import setup_environment, get_config
from zero_config.config import _reset_for_testing

def test_environment_variable_override():
    """Test that environment variables override defaults."""
    _reset_for_testing()
    
    with patch.dict(os.environ, {
        'APP__NAME': 'Env App',
        'DATABASE__PORT': '3306',
        'DEBUG': 'true'
    }, clear=True):
        setup_environment(default_config={
            'app.name': 'Default App',
            'database.port': 5432,
            'debug': False
        })
        
        config = get_config()
        assert config.get('app.name') == 'Env App'
        assert config.get('database.port') == 3306
        assert config.get('debug') is True
```
