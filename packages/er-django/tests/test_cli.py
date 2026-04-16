import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


class TestCLIHelp:
    def test_main_help(self):
        from x007007007.er_django.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert '--settings' in result.output
        assert '--project' in result.output

    def test_er_export_help(self):
        from x007007007.er_django.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ['er_export', '--help'])
        assert result.exit_code == 0

    def test_er_convert_help(self):
        from x007007007.er_django.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ['er_convert', '--help'])
        assert result.exit_code == 0

    def test_er_makemigrations_help(self):
        from x007007007.er_django.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ['er_makemigrations', '--help'])
        assert result.exit_code == 0

    def test_er_showmigrations_help(self):
        from x007007007.er_django.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ['er_showmigrations', '--help'])
        assert result.exit_code == 0


class TestCLISubcommands:
    def test_er_export_calls_management_command(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = True

        with patch('django.core.management.call_command') as mock_call:
            runner = CliRunner()
            result = runner.invoke(cli.cli, ['--settings=test.settings', 'er_export', '--format=toml'])
            mock_call.assert_called_once()
            assert mock_call.call_args[0][0] == 'er_export'

        cli_module._bootstrapped = False

    def test_er_convert_calls_management_command(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = True

        with patch('django.core.management.call_command') as mock_call:
            runner = CliRunner()
            result = runner.invoke(cli.cli, ['--settings=test.settings', 'er_convert', '--framework=django'])
            mock_call.assert_called_once()
            assert mock_call.call_args[0][0] == 'er_convert'

        cli_module._bootstrapped = False

    def test_er_makemigrations_calls_management_command(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = True

        with patch('django.core.management.call_command') as mock_call:
            runner = CliRunner()
            result = runner.invoke(cli.cli, ['--settings=test.settings', 'er_makemigrations'])
            mock_call.assert_called_once()
            assert mock_call.call_args[0][0] == 'er_makemigrations'

        cli_module._bootstrapped = False

    def test_er_showmigrations_calls_management_command(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = True

        with patch('django.core.management.call_command') as mock_call:
            runner = CliRunner()
            result = runner.invoke(cli.cli, ['--settings=test.settings', 'er_showmigrations'])
            mock_call.assert_called_once()
            assert mock_call.call_args[0][0] == 'er_showmigrations'

        cli_module._bootstrapped = False


class TestCLIBootstrap:
    def test_bootstrap_called_once(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = False

        with patch('x007007007.er_django.bootstrapper.bootstrap_django') as mock_bootstrap, \
             patch('django.core.management.call_command'):
            runner = CliRunner()
            runner.invoke(cli.cli, ['--settings=test.settings', 'er_export'])
            mock_bootstrap.assert_called_once_with(settings_module='test.settings', project_dir=None)

        cli_module._bootstrapped = False

    def test_bootstrap_with_project_dir(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = False

        with patch('x007007007.er_django.bootstrapper.bootstrap_django') as mock_bootstrap, \
             patch('django.core.management.call_command'):
            runner = CliRunner()
            runner.invoke(cli.cli, ['--project=/tmp/myproject', 'er_export'])
            mock_bootstrap.assert_called_once_with(settings_module=None, project_dir='/tmp/myproject')

        cli_module._bootstrapped = False

    def test_bootstrap_error_exits(self):
        from x007007007.er_django import cli
        import x007007007.er_django.cli as cli_module

        cli_module._bootstrapped = False

        with patch('x007007007.er_django.bootstrapper.bootstrap_django', side_effect=RuntimeError("Django not found")):
            runner = CliRunner()
            result = runner.invoke(cli.cli, ['--settings=test.settings', 'er_export'])
            assert result.exit_code != 0

        cli_module._bootstrapped = False


class TestMainFunction:
    def test_main_calls_cli(self):
        from x007007007.er_django.cli import main
        with patch('x007007007.er_django.cli.cli') as mock_cli:
            main()
            mock_cli.assert_called_once()
