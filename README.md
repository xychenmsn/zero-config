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

# Define your application's default configuration
default_config = {
    'temperature': 0.0,
    'max_tokens': 1024,
    'timeout': 30,
    'debug': False,
    'models': ['gpt-4o-mini'],
}

# Initialize with your defaults (call once at startup)
setup_environment(default_config=default_config)

# Use anywhere in your code
config = get_config()

# Access configuration values with smart type conversion
temperature = config.get('temperature')  # 0.0 (float from defaults)
api_key = config.get('openai_api_key')   # From OPENAI_API_KEY env var
debug = config.get('debug')              # False (bool from defaults)

# Environment variables override defaults with type conversion
# export TEMPERATURE="0.7"  -> becomes float 0.7
# export DEBUG="true"       -> becomes bool True
# export MODELS="gpt-4,claude-3" -> becomes list ['gpt-4', 'claude-3']

# Get all config as dict
all_config = config.to_dict()
```

## 📁 Configuration Sources (Priority Order)

1. **Default Config** - Your application's default configuration passed to `setup_environment()`
2. **Environment Variables** - Any uppercase environment variable matching config keys
3. **Domain Environment File** - `.env.zero_config` in your project root

### Environment Variables

```bash
# Any uppercase environment variable is automatically detected
export OPENAI_API_KEY="sk-..."              # Becomes: openai_api_key
export ANTHROPIC_API_KEY="sk-ant-..."       # Becomes: anthropic_api_key
export TEMPERATURE="0.7"                    # Becomes: temperature (with type conversion)
export MAX_TOKENS="2048"                    # Becomes: max_tokens (with type conversion)
export DEBUG="true"                         # Becomes: debug (with type conversion)

# Lists support multiple formats:
export MODELS='["gpt-4", "claude-3"]'       # JSON array (preferred)
export MODELS="gpt-4,claude-3"              # Comma-separated
export MODELS="gpt-4 claude-3"              # Space-separated
```

### Domain Environment File

Create `.env.zero_config` in your project root:

```bash
# API Keys
openai_api_key=sk-your-key-here
anthropic_api_key=sk-ant-your-key-here

# Configuration with smart type conversion
temperature=0.2
max_tokens=2048
debug=true

# Lists support multiple formats:
models=["gpt-4", "claude-3", "gemini-pro"]  # JSON array (recommended)
# models=gpt-4,claude-3,gemini-pro          # Comma-separated
# models=gpt-4 claude-3 gemini-pro          # Space-separated

# Any key defined in your default config gets type conversion
# New keys are added as strings
```

## 🎯 Smart Configuration Philosophy

Zero Config provides intelligent configuration management with:

1. **Your Defaults First** - You define what configuration your application needs
2. **Smart Type Conversion** - Environment variables are automatically converted to match your default types
3. **Flexible Override** - Any uppercase environment variable can override configuration
4. **No Prefixes Required** - Clean environment variable names without artificial prefixes

This approach gives you full control over your application's configuration while providing maximum flexibility for deployment and testing.

## 🛠️ Advanced Usage

### Dynamic Path Helpers

Zero Config provides dynamic path helpers - any attribute ending with `_path` automatically creates a path helper:

```python
from zero_config import setup_environment, get_config, data_path, logs_path

setup_environment()
config = get_config()

# Built-in path helpers (for backward compatibility)
db_file = data_path('database.db')  # /project/data/database.db
log_file = logs_path('app.log')     # /project/logs/app.log

# Dynamic path helpers - any directory name + '_path'
cache_file = config.cache_path('session.json')    # /project/cache/session.json
temp_dir = config.temp_path()                     # /project/temp/
models_file = config.models_path('gpt4.bin')      # /project/models/gpt4.bin
uploads_dir = config.uploads_path()               # /project/uploads/
static_file = config.static_path('style.css')     # /project/static/style.css

# Any directory name works!
config.backups_path('backup.tar.gz')             # /project/backups/backup.tar.gz
config.downloads_path('file.pdf')                # /project/downloads/file.pdf
```

### Smart Type Conversion

Zero Config automatically converts environment variables to match your default config types:

```python
# Your default config defines the types
default_config = {
    'temperature': 0.0,      # float
    'max_tokens': 1024,      # int
    'debug': False,          # bool
    'models': ['gpt-4']      # list
}

# Environment variables are converted to match
# export TEMPERATURE="0.7"                    → float: 0.7
# export MAX_TOKENS="2048"                    → int: 2048
# export DEBUG="true"                         → bool: True
# export MODELS='["gpt-4", "claude-3"]'       → list: ['gpt-4', 'claude-3'] (JSON)
# export MODELS="gpt-4,claude-3"              → list: ['gpt-4', 'claude-3'] (comma)
# export MODELS="gpt-4 claude-3"              → list: ['gpt-4', 'claude-3'] (space)
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
