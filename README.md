# Zero Config 🚀

A zero-configuration library with smart environment variable support and type-aware defaults. Perfect for LLM applications, APIs, and any Python project that needs intelligent configuration management.

## ✨ Features

- **Zero Configuration**: Works out of the box with sensible defaults
- **Smart Type Conversion**: Automatically converts environment variables to the correct Python types
- **Multiple Configuration Sources**: Environment variables, `.env.zero_config` files, and programmatic overrides
- **LLM-Ready**: Pre-configured with popular LLM providers (OpenAI, Anthropic, Google)
- **Project Root Detection**: Automatically finds your project root
- **Path Helpers**: Built-in data and logs directory management

## 🚀 Quick Start

```python
from zero_config import setup_environment, get_config

# Initialize (call once at startup)
setup_environment()

# Use anywhere in your code
config = get_config()

# Access configuration values
model = config.get('default_model')  # 'gpt-4o-mini'
api_key = config['openai_api_key']   # Raises KeyError if not found
temperature = config.get('temperature', 0.5)  # 0.0 (from defaults)

# Check if key exists
if 'anthropic_api_key' in config:
    print("Anthropic API key is configured")

# Get all config as dict
all_config = config.to_dict()
```

## 📁 Configuration Sources (Priority Order)

1. **Defaults** - Comprehensive built-in defaults for LLM applications
2. **Environment Variables** - `OPENAI_API_KEY`, `ZERO_CONFIG_*` prefixed vars
3. **Domain Environment File** - `.env.zero_config` in your project root

### Environment Variables

```bash
# Standard API keys (automatically detected)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."

# Zero Config prefixed variables
export ZERO_CONFIG_DEFAULT_MODEL="gpt-4o"
export ZERO_CONFIG_TEMPERATURE="0.7"
export ZERO_CONFIG_LOG_LEVEL="DEBUG"
```

### Domain Environment File

Create `.env.zero_config` in your project root:

```bash
# API Keys
openai_api_key=sk-your-key-here
anthropic_api_key=sk-ant-your-key-here

# LLM Settings
default_model=claude-3-5-sonnet-20241022
temperature=0.2
max_tokens=2048

# Logging
log_level=DEBUG
log_calls=true
```

## 🎯 Built-in Defaults

Zero Config comes with comprehensive defaults for LLM applications:

```python
DEFAULTS = {
    # Core LLM Settings
    'default_model': 'gpt-4o-mini',
    'fallback_models': ['gpt-4o-mini', 'claude-3-5-sonnet-20241022'],
    'temperature': 0.0,
    'max_tokens': 1024,
    'timeout': 30,
    'max_retries': 3,

    # Provider Settings
    'ollama_base_url': 'http://localhost:11434/v1',
    'openai_base_url': '',
    'anthropic_base_url': '',

    # Model Lists
    'openai_models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    'anthropic_models': ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
    'google_models': ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'],

    # Logging & Database
    'log_calls': False,
    'log_to_db': True,
    'db_path': 'llm_calls.db',

    # API Server
    'api_host': '0.0.0.0',
    'api_port': 8818,
    # ... and more
}
```

## 🛠️ Advanced Usage

### Path Helpers

```python
from zero_config import data_path, logs_path

# Get data directory path
db_file = data_path('database.db')  # /project/data/database.db
cache_dir = data_path()             # /project/data/

# Get logs directory path
log_file = logs_path('app.log')     # /project/logs/app.log
logs_dir = logs_path()              # /project/logs/
```

### Type-Aware Conversion

Zero Config automatically converts string values to the correct Python types:

```bash
# Environment variables
export ZERO_CONFIG_TEMPERATURE="0.7"        # → float: 0.7
export ZERO_CONFIG_MAX_TOKENS="2048"        # → int: 2048
export ZERO_CONFIG_LOG_CALLS="true"         # → bool: True
export ZERO_CONFIG_MODELS="gpt-4,claude-3"  # → list: ['gpt-4', 'claude-3']
```

### Custom Project Root

```python
from zero_config import setup_environment
from pathlib import Path

# Specify custom project root
setup_environment(start_path="/path/to/my/project")
```

## 📦 Installation

```bash
pip install zero-config
```

## 🧪 Development

```bash
# Clone the repository
git clone https://github.com/zero-config/zero-config.git
cd zero-config

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black zero_config/

# Type checking
mypy zero_config/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
