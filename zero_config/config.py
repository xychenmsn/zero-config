import os
import sys
import ast
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Global state
_config = None
_project_root = None

# ========================================
# COMPLETE DEFAULTS - TYPE-AWARE
# ========================================
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
    'openai_base_url': '',  # Empty means use default
    'anthropic_base_url': '',  # Empty means use default

    # API Keys (empty by default, loaded from env/config)
    'openai_api_key': '',
    'anthropic_api_key': '',
    'google_api_key': '',

    # Model Lists (comprehensive for 0-config)
    'openai_models': [
        'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'
    ],
    'anthropic_models': [
        'claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307',
        'claude-sonnet-4-20250514', 'claude-3-7-sonnet-20250219'
    ],
    'google_models': [
        'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest',
        'gemini-2.5-pro-preview-05-06', 'gemini-2.5-flash-preview-05-20'
    ],

    # Logging Settings
    'log_calls': False,
    'log_to_db': True,
    'log_json': False,
    'log_level': 'INFO',
    'db_path': 'llm_calls.db',

    # Search Settings
    'duckduckgo_max_results': 5,
    'duckduckgo_timeout': 10,

    # API Server Settings
    'api_host': '0.0.0.0',
    'api_port': 8818,
    'admin_username': 'admin',
    'admin_password': 'admin',
}

class Config:
    def __init__(self, config_data: Dict[str, Any], project_root: Path):
        self._data = config_data
        self._project_root = project_root

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Configuration key '{key}' not found")

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()

    def data_path(self, filename: str = "") -> str:
        path = self._project_root / "data"
        if filename:
            path = path / filename
        return str(path)

    def logs_path(self, filename: str = "") -> str:
        path = self._project_root / "logs"
        if filename:
            path = path / filename
        return str(path)

    def get_db_path(self) -> str:
        db_path = self.get('db_path', 'llm_calls.db')
        if os.path.isabs(db_path):
            return db_path
        else:
            return self.data_path(db_path)


def find_project_root(start_path: Optional[Union[str, Path]] = None) -> Path:
    """Find project root by looking for common indicators."""
    if start_path is None:
        start_path = Path.cwd()
    elif isinstance(start_path, str):
        start_path = Path(start_path)

    if start_path.is_file():
        start_path = start_path.parent

    current = start_path.resolve()
    indicators = ['.env.zero_config', '.env', 'pyproject.toml', 'requirements.txt', '.git']

    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent

    return Path.cwd()

def load_domain_env_file(project_root: Path) -> Dict[str, str]:
    """Load .env.zero_config file if it exists."""
    env_file = project_root / ".env.zero_config"
    if not env_file.exists():
        return {}

    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        env_vars[key] = value

        logging.info(f"Loaded {len(env_vars)} variables from .env.zero_config")
    except Exception as e:
        logging.error(f"Failed to load .env.zero_config: {e}")

    return env_vars

def smart_convert(str_value: str, default_value: Any) -> Any:
    """Convert string value based on default type - SUPER SIMPLE."""
    # Keep strings as-is
    if isinstance(default_value, str):
        return str_value

    # Try literal_eval first (handles most cases: True, 3, 3.14, [1,2,3])
    try:
        converted = ast.literal_eval(str_value)
        if type(converted) == type(default_value):
            return converted
    except:
        pass

    # Fallback for common types
    if isinstance(default_value, bool):
        return str_value.lower() in ('true', '1', 'yes', 'on')
    elif isinstance(default_value, list):
        return [item.strip() for item in str_value.split(',')]
    else:
        return str_value

def apply_environment_variables(config: Dict[str, Any]) -> None:
    """Apply environment variables with smart type conversion."""

    # 1. Hard-coded API keys (for 0-config experience)
    api_key_mappings = {
        'openai_api_key': 'OPENAI_API_KEY',
        'anthropic_api_key': 'ANTHROPIC_API_KEY',
        'google_api_key': 'GOOGLE_API_KEY',
    }

    for config_key, env_var in api_key_mappings.items():
        if env_var in os.environ:
            config[config_key] = os.environ[env_var]
            logging.debug(f"Found API key: {env_var}")

    # 2. Smart ZERO_CONFIG_* prefix matching
    for env_var, env_value in os.environ.items():
        if env_var.startswith('ZERO_CONFIG_'):
            # Strip prefix and convert to config key
            config_key = env_var[12:].lower()  # Remove 'ZERO_CONFIG_'

            # Only override if it's a known default value
            if config_key in config:
                config[config_key] = smart_convert(env_value, config[config_key])
                logging.debug(f"Environment override: {env_var} -> {config_key}")

def setup_environment(start_path: Optional[Union[str, Path]] = None) -> None:
    """Setup environment with clean 4-layer configuration."""
    global _config, _project_root

    # Find project root
    _project_root = find_project_root(start_path)

    # Load .env.zero_config if exists (for python-dotenv compatibility)
    env_file = _project_root / ".env.zero_config"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logging.debug(f"Loaded environment from: {env_file}")
        except ImportError:
            logging.debug("python-dotenv not available, loading manually")

    # Configuration priority (low to high):
    # 1. Default values (always complete)
    config_data = DEFAULTS.copy()

    # 2. OS environment variables
    apply_environment_variables(config_data)

    # 3. .env.zero_config file (highest priority)
    domain_env = load_domain_env_file(_project_root)
    for key, str_value in domain_env.items():
        if key in config_data:
            config_data[key] = smart_convert(str_value, config_data[key])
            logging.debug(f"Domain env override: {key}")

    # 4. Create config object
    _config = Config(config_data, _project_root)

    logging.info(f"🚀 Environment setup complete")
    logging.info(f"   Project root: {_project_root}")

def get_config() -> Config:
    """Get the global configuration object."""
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call setup_environment() first.")
    return _config

def data_path(filename: str = "") -> str:
    """Get data directory path."""
    return get_config().data_path(filename)

def logs_path(filename: str = "") -> str:
    """Get logs directory path."""
    return get_config().logs_path(filename)