import os
import sys
import ast
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Global state
_config = None
_project_root = None
_is_initialized = False
_initialized_by = None

# ========================================
# MINIMAL DEFAULTS - ZERO CONFIG APPROACH
# ========================================
DEFAULTS = {}

class Config:
    def __init__(self, config_data: Dict[str, Any], project_root: Path):
        self._data = config_data
        self._project_root = project_root

    def get(self, key: str, default: Any = None) -> Any:
        # First check if it's a direct key
        if key in self._data:
            return self._data[key]

        # If not found, check if it's a section (e.g., 'llm' for 'llm.*' keys)
        section_prefix = f"{key}."
        section_config = {}

        for config_key, value in self._data.items():
            if config_key.startswith(section_prefix):
                # Remove section prefix: 'llm.models' -> 'models'
                section_key = config_key[len(section_prefix):]
                section_config[section_key] = value

        # If we found section keys, return the section dict
        if section_config:
            return section_config

        # Otherwise return the default
        return default

    def __getitem__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise KeyError(f"Configuration key '{key}' not found")

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()



    def __getattr__(self, name: str) -> Any:
        """Dynamic path helper: any attribute ending with '_path' creates a path helper."""
        if name.endswith('_path'):
            # Extract the directory name (e.g., 'data_path' -> 'data')
            dir_name = name[:-5]  # Remove '_path' suffix

            def path_helper(filename: str = "") -> str:
                path = self._project_root / dir_name
                if filename:
                    path = path / filename
                return str(path)

            return path_helper

        # If not a path helper, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get_db_path(self) -> str:
        """Get database path, using data_path helper."""
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
    # Common project root indicators (in order of preference)
    indicators = [
        '.git',           # Git repository (most reliable)
        'pyproject.toml', # Python project with modern packaging
        'setup.py',       # Python project with traditional packaging
        'requirements.txt', # Python project with pip requirements
        'Pipfile',        # Python project with pipenv
        'poetry.lock',    # Python project with poetry
        'package.json',   # Node.js project
        'Cargo.toml',     # Rust project
        'go.mod',         # Go project
        'pom.xml',        # Java Maven project
        'build.gradle',   # Java Gradle project
        '.env',           # Environment file (less reliable but common)
    ]

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
            for line in f:
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
    """Convert string value based on default type with safe, explicit parsing."""
    # Keep strings as-is
    if isinstance(default_value, str):
        return str_value

    # Try literal_eval first (handles JSON-like formats: True, 3, 3.14, ["a","b"], {"key":"value"})
    try:
        converted = ast.literal_eval(str_value)
        if type(converted) == type(default_value):
            return converted
    except:
        pass

    # Fallback for common types
    if isinstance(default_value, bool):
        return str_value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    elif isinstance(default_value, (int, float)):
        try:
            return type(default_value)(str_value)
        except ValueError:
            return str_value  # Keep as string if conversion fails
    elif isinstance(default_value, list):
        # ONLY support explicit JSON array format for lists
        str_value = str_value.strip()

        # Empty string becomes empty list
        if not str_value:
            return []

        # Only JSON array format: ["item1", "item2"]
        if str_value.startswith('[') and str_value.endswith(']'):
            try:
                return ast.literal_eval(str_value)
            except:
                pass

        # If not JSON format, treat as single-item list
        # This preserves comma-containing strings safely
        return [str_value]
    else:
        return str_value

def apply_environment_variables(config: Dict[str, Any]) -> None:
    """Apply environment variables with smart type conversion and section support."""

    # Search uppercase environment variables and match to config keys
    for env_var, env_value in os.environ.items():
        if env_var.isupper():
            # Handle section headers: LLM__MODELS -> llm.models
            if '__' in env_var:
                section, key = env_var.split('__', 1)
                config_key = f"{section.lower()}.{key.lower()}"
            else:
                # Regular key: TEMPERATURE -> temperature
                config_key = env_var.lower()

            # Skip project_root - it's already set and should not be overridden
            if config_key == 'project_root':
                logging.debug(f"Skipping {env_var} - project_root is handled separately")
                continue

            # Only apply if we have a corresponding config key (from defaults or .env)
            if config_key in config:
                # Use smart conversion based on the existing default value type
                config[config_key] = smart_convert(env_value, config[config_key])
                logging.debug(f"Environment override: {env_var} -> {config_key} = {config[config_key]}")

def _load_env_file_data(project_root: Path, env_files: Optional[Union[str, Path, list[Union[str, Path]]]]) -> Dict[str, str]:
    """Load environment files and return their data as a dictionary."""
    env_data = {}
    files_to_load = []

    if env_files is None:
        # Default: look for .env.zero_config in project root
        default_env_file = project_root / ".env.zero_config"
        if default_env_file.exists():
            files_to_load.append(default_env_file)
    else:
        # Handle single file or list of files
        if isinstance(env_files, (str, Path)):
            env_files = [env_files]

        for env_file in env_files:
            env_path = Path(env_file)
            # If relative path, make it relative to project root
            if not env_path.is_absolute():
                env_path = project_root / env_path

            if env_path.exists():
                files_to_load.append(env_path)
            else:
                logging.warning(f"Environment file not found: {env_path}")

    # Load all found files (later files override earlier ones)
    for env_file in files_to_load:
        file_data = _parse_env_file(env_file)
        env_data.update(file_data)  # Later files override earlier ones
        logging.debug(f"Loaded {len(file_data)} variables from: {env_file}")

    return env_data


def _parse_env_file(env_file: Path) -> Dict[str, str]:
    """Parse a single env file and return its data."""
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        env_vars[key] = value
    except Exception as e:
        logging.error(f"Failed to load {env_file}: {e}")

    return env_vars


def _load_env_files(project_root: Path, env_files: Optional[Union[str, Path, list[Union[str, Path]]]]) -> None:
    """Load environment files with flexible input handling."""
    files_to_load = []

    if env_files is None:
        # Default: look for .env.zero_config in project root
        default_env_file = project_root / ".env.zero_config"
        if default_env_file.exists():
            files_to_load.append(default_env_file)
    else:
        # Handle single file or list of files
        if isinstance(env_files, (str, Path)):
            env_files = [env_files]

        for env_file in env_files:
            env_path = Path(env_file)
            # If relative path, make it relative to project root
            if not env_path.is_absolute():
                env_path = project_root / env_path

            if env_path.exists():
                files_to_load.append(env_path)
            else:
                logging.warning(f"Environment file not found: {env_path}")

    # Load all found files
    for env_file in files_to_load:
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logging.debug(f"Loaded environment from: {env_file}")
        except ImportError:
            logging.debug(f"python-dotenv not available, skipping: {env_file}")


def setup_environment(
    default_config: Optional[Dict[str, Any]] = None,
    env_files: Optional[Union[str, Path, list[Union[str, Path]]]] = None,
    force_reinit: bool = False
) -> None:
    """Setup environment with flexible configuration layers.

    Args:
        default_config: Default configuration values to start with
        env_files: Optional .env file(s) to load. Can be a single file path or list of file paths.
                  If not provided, will look for .env.zero_config in project root.
        force_reinit: If True, force re-initialization even if already initialized.
                     Use with caution as this can break package dependencies.
    """
    global _config, _project_root, _is_initialized, _initialized_by

    # Check if already initialized
    if _is_initialized and not force_reinit:
        # Get caller information for better debugging
        import inspect
        caller_frame = inspect.currentframe().f_back
        caller_info = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"

        logging.info(f"🔄 Zero-config already initialized by {_initialized_by}")
        logging.info(f"   Subsequent call from: {caller_info}")
        logging.info(f"   Skipping re-initialization to prevent conflicts")
        logging.info(f"   Current project root: {_project_root}")
        logging.info(f"   Use force_reinit=True to override (not recommended)")
        return

    # Record who is initializing this
    import inspect
    caller_frame = inspect.currentframe().f_back
    _initialized_by = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"

    # 1. Determine project root (env var override or auto-detection)
    if 'PROJECT_ROOT' in os.environ:
        _project_root = Path(os.environ['PROJECT_ROOT']).resolve()
        logging.info(f"Using PROJECT_ROOT from environment: {_project_root}")
    else:
        _project_root = find_project_root()
        logging.info(f"Auto-detected project root: {_project_root}")

    # 2. Load environment files
    _load_env_files(_project_root, env_files)

    # Configuration priority (low to high):
    # 2. Default values (user-provided or empty)
    config_data = (default_config or {}).copy()

    # 3. Always add project_root (from env or auto-detected, as absolute path)
    config_data['project_root'] = str(_project_root)

    # 4. OS environment variables
    apply_environment_variables(config_data)

    # 5. Load env files (custom files or default .env.zero_config)
    env_data = _load_env_file_data(_project_root, env_files)
    for key, str_value in env_data.items():
        # Skip project_root - it's already set and should not be overridden by .env file
        if key == 'project_root':
            logging.warning(f"Ignoring project_root in env file - use PROJECT_ROOT env var instead")
            continue

        # Env file keys are already in the correct format (llm.models)
        if key in config_data:
            # Use smart conversion based on existing default value type
            config_data[key] = smart_convert(str_value, config_data[key])
            logging.debug(f"Env file override: {key} = {config_data[key]}")
        else:
            # Add new key as string
            config_data[key] = str_value
            logging.debug(f"Env file addition: {key} = {str_value}")

    # 6. Create config object
    _config = Config(config_data, _project_root)

    # 7. Mark as initialized
    _is_initialized = True

    logging.info(f"🚀 Environment setup complete")
    logging.info(f"   Initialized by: {_initialized_by}")
    logging.info(f"   Project root: {_project_root}")
    logging.info(f"   Configuration keys: {list(config_data.keys())}")

def get_config() -> Config:
    """Get the global configuration object."""
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call setup_environment() first.")
    return _config


def is_initialized() -> bool:
    """Check if zero-config has been initialized."""
    return _is_initialized


def get_initialization_info() -> Optional[str]:
    """Get information about who initialized zero-config."""
    return _initialized_by if _is_initialized else None


def _reset_for_testing() -> None:
    """Reset global state for testing purposes. Internal use only."""
    global _config, _project_root, _is_initialized, _initialized_by
    _config = None
    _project_root = None
    _is_initialized = False
    _initialized_by = None

