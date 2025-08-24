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

class DotDict(dict):
    """Dictionary that supports dot notation for nested access and assignment."""

    def __init__(self, data=None):
        super().__init__()
        if data:
            for key, value in data.items():
                self[key] = value

    def __getitem__(self, key):
        if '.' in key:
            return self._get_nested(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if '.' in key:
            self._set_nested(key, value)
        else:
            super().__setitem__(key, value)

    def __contains__(self, key):
        if '.' in key:
            try:
                self._get_nested(key)
                return True
            except KeyError:
                return False
        return super().__contains__(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _get_nested(self, key):
        """Get value using dot notation."""
        parts = key.split('.')
        current = self
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise KeyError(key)
        return current

    def _set_nested(self, key, value):
        """Set value using dot notation."""
        parts = key.split('.')
        current = self
        for part in parts[:-1]:
            if part not in current:
                current[part] = DotDict()
            elif not isinstance(current[part], dict):
                current[part] = DotDict()
            current = current[part]
        current[parts[-1]] = value


class Config:
    def __init__(self, config_data: Dict[str, Any], project_root: Path):
        self._data = DotDict(config_data)  # Use DotDict for native dot notation support
        self._project_root = project_root

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with support for nested keys and sections."""
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def to_dict(self) -> Dict[str, Any]:
        """Return the nested dictionary representation."""
        return dict(self._data)

    def to_flat_dict(self) -> Dict[str, Any]:
        """Return the flat dictionary with dot notation keys."""
        def _flatten(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        return _flatten(self._data)

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

def _flatten_nested_dict(nested_dict: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary into a flat dictionary with dot notation keys.

    Args:
        nested_dict: The nested dictionary to flatten
        parent_key: The parent key prefix (used for recursion)
        separator: The separator to use between keys (default: '.')

    Returns:
        A flat dictionary with dot notation keys

    Example:
        {'database': {'develop': {'db_url': 'test'}}} -> {'database.develop.db_url': 'test'}
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.extend(_flatten_nested_dict(value, new_key, separator).items())
        else:
            # Keep the value as-is
            items.append((new_key, value))
    return dict(items)


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
        str_lower = str_value.lower()
        if str_lower in ('true', '1', 'yes', 'on', 'enabled'):
            return True
        elif str_lower in ('false', '0', 'no', 'off', 'disabled'):
            return False
        else:
            # If it's not a recognized boolean value, keep the default
            return default_value
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

def _create_env_mapping(nested_dict: Dict[str, Any], path: list = None) -> Dict[str, list]:
    """
    Create mapping from ENV_VAR format to nested path in dictionary.

    Args:
        nested_dict: The nested dictionary to map
        path: Current path (used for recursion)

    Returns:
        Dictionary mapping ENV_VAR_FORMAT to list of keys representing path

    Example:
        {'database': {'develop': {'db_url': 'test'}}}
        -> {'DATABASE__DEVELOP__DB_URL': ['database', 'develop', 'db_url']}
    """
    if path is None:
        path = []

    mapping = {}
    for key, value in nested_dict.items():
        current_path = path + [key]
        env_key = '__'.join([p.upper() for p in current_path])

        if isinstance(value, dict):
            # Recursively process nested dicts
            mapping.update(_create_env_mapping(value, current_path))
        else:
            # Store the path to this value
            mapping[env_key] = current_path

    return mapping


def apply_environment_variables(config: DotDict) -> None:
    """
    Apply environment variables using the optimal approach:

    1. Flatten config keys to ENV_VAR format (DATABASE__DEVELOPE__DB_URL)
    2. Loop through flattened keys and directly check os.environ[key]
    3. If found, use dot notation to directly set config[dot_key] = value

    This is much more efficient than looping through all environment variables.
    """

    # Step 1: Get all flat keys from config and convert to ENV_VAR format
    flat_keys = _get_all_flat_keys(config)

    # Always add PROJECT_ROOT to be checked, even if not in default config
    if 'project_root' not in flat_keys:
        flat_keys.append('project_root')

    env_var_keys = set()

    for dot_key in flat_keys:
        # Convert dot notation to ENV_VAR format
        env_var = dot_key.replace('.', '__').upper()
        env_var_keys.add(env_var)

    # Step 2: Loop through ENV_VAR keys and check if they exist in os.environ
    for env_var in env_var_keys:
        if env_var in os.environ:
            env_value = os.environ[env_var]

            # Parse ENV_VAR back to dot notation
            dot_key = env_var.replace('__', '.').lower()

            # Skip PROJECT_ROOT - it's handled separately with proper priority order
            if dot_key == 'project_root':
                logging.debug(f"Skipping {env_var} - PROJECT_ROOT handled separately with priority order")
            elif dot_key in config:
                # Update existing config value using dot notation
                old_value = config[dot_key]
                new_value = smart_convert(env_value, old_value)
                config[dot_key] = new_value  # DotDict handles the nested assignment
                logging.debug(f"Environment override: {env_var} -> {dot_key} = {new_value}")
            else:
                # This shouldn't happen since we only check keys from our config
                logging.debug(f"Skipping {env_var} - not in config")

    logging.debug(f"Checked {len(env_var_keys)} potential environment variables")


def _get_all_flat_keys(config: DotDict) -> list:
    """Get all flat keys from a nested config structure."""
    def _flatten_keys(d, parent_key='', sep='.'):
        keys = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                keys.extend(_flatten_keys(v, new_key, sep=sep))
            else:
                keys.append(new_key)
        return keys
    return _flatten_keys(config)


def _build_nested_dict_from_flat(flat_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build nested dictionary from flat dictionary with dot notation keys.

    Args:
        flat_dict: Dictionary with dot notation keys

    Returns:
        Nested dictionary structure

    Example:
        {'database.develop.db_url': 'test'} -> {'database': {'develop': {'db_url': 'test'}}}
    """
    nested_dict = {}
    for key, value in flat_dict.items():
        if '.' in key:
            parts = key.split('.')
            current = nested_dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            nested_dict[key] = value
    return nested_dict

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
    """Parse a single env file and return its data with support for multi-level sections."""
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
                        
                        # Convert double underscores to dots for consistency with env vars
                        if '__' in key:
                            key = key.replace('__', '.')
                            
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

    # 1. Determine project root (OS environment has priority over auto-detection)
    # .env files CANNOT override project root due to chicken-and-egg problem
    if 'PROJECT_ROOT' in os.environ:
        _project_root = Path(os.environ['PROJECT_ROOT']).resolve()
        logging.info(f"Using PROJECT_ROOT from environment: {_project_root}")
    else:
        _project_root = find_project_root()
        logging.info(f"Auto-detected project root: {_project_root}")

    # 2. Load environment files (using determined project root)
    _load_env_files(_project_root, env_files)

    # Configuration priority (low to high):
    # 2. Default values (user-provided or empty)
    # Create DotDict from default configuration (supports both nested and flat formats)
    raw_default_config = (default_config or {}).copy()
    config_data = DotDict()

    # Add flattened default config to DotDict
    flattened_defaults = _flatten_nested_dict(raw_default_config)
    for key, value in flattened_defaults.items():
        config_data[key] = value

    # 3. Add project_root to config (already determined above)
    config_data['project_root'] = str(_project_root)

    # 4. OS environment variables (excluding PROJECT_ROOT which is handled above)
    apply_environment_variables(config_data)

    # 5. Load env files and apply configuration
    # .env files CANNOT override project_root (chicken-and-egg problem)
    env_data = _load_env_file_data(_project_root, env_files)
    for key, str_value in env_data.items():
        # Skip project_root - .env files cannot override project root
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

