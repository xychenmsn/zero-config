from .config import (
    setup_environment,
    get_config,
    is_initialized,
    get_initialization_info,
)

__version__ = "0.1.5"

# Public API - what users should import
__all__ = [
    'setup_environment',
    'get_config',
    'is_initialized',
    'get_initialization_info',
]