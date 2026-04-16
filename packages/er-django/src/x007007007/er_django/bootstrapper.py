import os
import sys
from pathlib import Path


def _detect_django() -> bool:
    try:
        import django
        return True
    except ImportError:
        return False


def _inject_installed_apps():
    from django.conf import settings
    app_name = 'x007007007.er_django'
    installed_apps = list(settings.INSTALLED_APPS)
    if app_name not in installed_apps:
        installed_apps.append(app_name)
        settings.INSTALLED_APPS = installed_apps


def _discover_settings_module(project_dir: str) -> str:
    project_path = Path(project_dir).resolve()
    parent_dir = str(project_path.parent)
    parent_in_path = parent_dir in sys.path
    if not parent_in_path:
        sys.path.insert(0, parent_dir)

    project_name = project_path.name

    candidates = []

    settings_file = project_path / "settings.py"
    if settings_file.exists():
        candidates.append(f"{project_name}.settings")

    settings_dir = project_path / "settings"
    if settings_dir.is_dir():
        for ext in ("__init__.py", "base.py", "dev.py"):
            candidate_file = settings_dir / ext
            if candidate_file.exists():
                candidates.append(f"{project_name}.settings")
                break

    root_settings = project_path / project_name / "settings.py"
    if root_settings.exists():
        candidates.append(f"{project_name}.{project_name}.settings")

    root_settings_dir = project_path / project_name / "settings"
    if root_settings_dir.is_dir():
        for ext in ("__init__.py", "base.py", "dev.py"):
            candidate_file = root_settings_dir / ext
            if candidate_file.exists():
                candidates.append(f"{project_name}.{project_name}.settings")
                break

    if not candidates:
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                wsgi_file = item / "wsgi.py"
                if wsgi_file.exists():
                    settings_candidate = item / "settings.py"
                    if settings_candidate.exists():
                        candidates.append(f"{item.name}.settings")
                    settings_subdir = item / "settings"
                    if settings_subdir.is_dir():
                        for ext in ("__init__.py", "base.py", "dev.py"):
                            if (settings_subdir / ext).exists():
                                candidates.append(f"{item.name}.settings")
                                break
                    break

    if not candidates:
        if not parent_in_path:
            sys.path.remove(parent_dir)
        raise ValueError(
            f"Could not discover DJANGO_SETTINGS_MODULE in '{project_dir}'. "
            f"Please specify it explicitly via settings_module parameter."
        )

    return candidates[0]


def bootstrap_django(settings_module=None, project_dir=None):
    if not _detect_django():
        raise RuntimeError(
            "Django is not installed. Install it with: pip install django"
        )

    if project_dir:
        settings_module = _discover_settings_module(project_dir)

    if settings_module:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    elif not os.environ.get("DJANGO_SETTINGS_MODULE"):
        raise RuntimeError(
            "No Django settings module found. Provide either settings_module or "
            "project_dir, or set the DJANGO_SETTINGS_MODULE environment variable."
        )

    try:
        _inject_installed_apps()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to inject er_django into INSTALLED_APPS: {exc}"
        ) from exc

    import django
    try:
        django.setup()
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize Django: {exc}") from exc
