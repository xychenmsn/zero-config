from zero_config import setup_environment, get_config

# Simple usage - automatically finds project root
setup_environment()
config = get_config()

# With project-specific defaults
setup_environment(
    project_defaults={
        'news_api_key': '',
        'news_sources': ['cnn', 'bbc', 'reuters'],
    }
)

# With multiple environment files
setup_environment(
    env_files=[
        ".env.llm",       # LLM-specific settings
        ".env.news",      # News-specific settings
        ".env.local"      # Local overrides (not in version control)
    ]
)

# Using environment variable to specify project root
# $ export PROJECT_ROOT=/path/to/project
# This takes precedence over automatic detection