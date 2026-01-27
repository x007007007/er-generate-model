"""
Django settings for ER Django plugin
"""
from django.conf import settings
from pathlib import Path


def get_er_migrations_dir() -> str:
    """
    Get ER migrations directory from Django settings.
    
    Returns:
        Path to ER migrations directory
    """
    # Check if ER_MIGRATIONS_DIR is configured in settings
    if hasattr(settings, 'ER_MIGRATIONS_DIR'):
        migrations_dir = settings.ER_MIGRATIONS_DIR
        
        # If it's a relative path, make it relative to BASE_DIR
        if not Path(migrations_dir).is_absolute():
            base_dir = getattr(settings, 'BASE_DIR', Path.cwd())
            return str(Path(base_dir) / migrations_dir)
        
        return str(migrations_dir)
    
    # Default: BASE_DIR/er_migrations
    base_dir = getattr(settings, 'BASE_DIR', Path.cwd())
    return str(Path(base_dir) / 'er_migrations')


def get_er_export_dir() -> str:
    """
    Get ER export directory from Django settings.
    
    Returns:
        Path to ER export directory
    """
    # Check if ER_EXPORT_DIR is configured in settings
    if hasattr(settings, 'ER_EXPORT_DIR'):
        export_dir = settings.ER_EXPORT_DIR
        
        # If it's a relative path, make it relative to BASE_DIR
        if not Path(export_dir).is_absolute():
            base_dir = getattr(settings, 'BASE_DIR', Path.cwd())
            return str(Path(base_dir) / export_dir)
        
        return str(export_dir)
    
    # Default: BASE_DIR/er_export
    base_dir = getattr(settings, 'BASE_DIR', Path.cwd())
    return str(Path(base_dir) / 'er_export')


def get_er_settings() -> dict:
    """
    Get all ER-related settings with defaults.
    
    Returns:
        Dictionary of ER settings
    """
    return {
        'migrations_dir': get_er_migrations_dir(),
        'export_dir': get_er_export_dir(),
        'auto_create_dirs': getattr(settings, 'ER_AUTO_CREATE_DIRS', True),
        'default_format': getattr(settings, 'ER_DEFAULT_FORMAT', 'mermaid'),
        'include_django_apps': getattr(settings, 'ER_INCLUDE_DJANGO_APPS', False),
        'exclude_apps': getattr(settings, 'ER_EXCLUDE_APPS', []),
        'file_prefix': getattr(settings, 'ER_FILE_PREFIX', ''),
        'file_suffix': getattr(settings, 'ER_FILE_SUFFIX', ''),
    }


def ensure_directory_exists(path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_output_filename(app_label: str, format_type: str, custom_name: str = None) -> str:
    """
    Generate output filename based on settings and parameters.
    
    Args:
        app_label: Django app label
        format_type: Output format (mermaid, plantuml, toml)
        custom_name: Custom filename (optional)
        
    Returns:
        Generated filename
    """
    er_settings = get_er_settings()
    
    if custom_name:
        base_name = custom_name
    else:
        # Use app_label as base name
        base_name = app_label
    
    # Add prefix and suffix
    prefix = er_settings['file_prefix']
    suffix = er_settings['file_suffix']
    
    if prefix:
        base_name = f"{prefix}_{base_name}"
    if suffix:
        base_name = f"{base_name}_{suffix}"
    
    # Add extension based on format
    extensions = {
        'mermaid': '.mmd',
        'plantuml': '.puml',
        'toml': '.toml',
    }
    
    extension = extensions.get(format_type, '.txt')
    return f"{base_name}{extension}"