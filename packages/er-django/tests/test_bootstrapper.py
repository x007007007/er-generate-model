import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

pytest.importorskip("django")

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'x007007007.er_django',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()


class TestDetectDjango:
    def test_returns_true_when_django_available(self):
        from x007007007.er_django.bootstrapper import _detect_django
        assert _detect_django() is True

    def test_returns_false_when_django_unavailable(self):
        with patch.dict('sys.modules', {'django': None}):
            import importlib
            import x007007007.er_django.bootstrapper as bm
            importlib.reload(bm)
            assert bm._detect_django() is False


class TestInjectInstalledApps:
    def test_injects_when_not_present(self):
        from x007007007.er_django.bootstrapper import _inject_installed_apps
        original = list(settings.INSTALLED_APPS)
        if 'x007007007.er_django' in original:
            original.remove('x007007007.er_django')
        settings.INSTALLED_APPS = original

        _inject_installed_apps()

        assert 'x007007007.er_django' in settings.INSTALLED_APPS
        settings.INSTALLED_APPS = original

    def test_does_not_duplicate(self):
        from x007007007.er_django.bootstrapper import _inject_installed_apps
        original = list(settings.INSTALLED_APPS)
        if 'x007007007.er_django' not in original:
            original.append('x007007007.er_django')
        settings.INSTALLED_APPS = original

        _inject_installed_apps()

        count = settings.INSTALLED_APPS.count('x007007007.er_django')
        assert count == 1
        settings.INSTALLED_APPS = original


class TestDiscoverSettingsModule:
    def test_discovers_settings_in_project_root(self, tmp_path):
        settings_file = tmp_path / "settings.py"
        settings_file.write_text("SECRET_KEY = 'test'\nBASE_DIR = '/test'\n")

        from x007007007.er_django.bootstrapper import _discover_settings_module
        result = _discover_settings_module(str(tmp_path))

        assert result == f"{tmp_path.name}.settings"

    def test_discovers_settings_in_subdir_with_wsgi(self, tmp_path):
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()
        (project_dir / "wsgi.py").write_text("")
        (project_dir / "settings.py").write_text("SECRET_KEY = 'test'\n")

        from x007007007.er_django.bootstrapper import _discover_settings_module
        result = _discover_settings_module(str(tmp_path))

        assert result == "myproject.settings"

    def test_raises_when_no_settings_found(self, tmp_path):
        from x007007007.er_django.bootstrapper import _discover_settings_module
        with pytest.raises(ValueError, match="Could not discover"):
            _discover_settings_module(str(tmp_path))


class TestBootstrapDjango:
    def test_raises_when_no_settings_or_env(self):
        from x007007007.er_django.bootstrapper import bootstrap_django
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('DJANGO_SETTINGS_MODULE', None)
            with pytest.raises(RuntimeError, match="No Django settings module found"):
                bootstrap_django(settings_module=None, project_dir=None)

    def test_raises_when_django_not_installed(self):
        with patch('x007007007.er_django.bootstrapper._detect_django', return_value=False):
            from x007007007.er_django.bootstrapper import bootstrap_django
            with pytest.raises(RuntimeError, match="Django is not installed"):
                bootstrap_django(settings_module="test.settings")

    def test_sets_env_and_calls_setup(self):
        with patch('x007007007.er_django.bootstrapper._detect_django', return_value=True), \
             patch('x007007007.er_django.bootstrapper._inject_installed_apps'), \
             patch('django.setup') as mock_setup:
            import importlib
            import x007007007.er_django.bootstrapper as bm
            importlib.reload(bm)

            bm.bootstrap_django(settings_module="myproject.settings")

            assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'myproject.settings'
            mock_setup.assert_called_once()
