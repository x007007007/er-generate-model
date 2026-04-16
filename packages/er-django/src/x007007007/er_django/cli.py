import sys
import click

_bootstrapped = False


def _ensure_django_ready(settings_module=None, project_dir=None):
    global _bootstrapped
    if _bootstrapped:
        return
    from x007007007.er_django.bootstrapper import bootstrap_django
    try:
        bootstrap_django(settings_module=settings_module, project_dir=project_dir)
    except RuntimeError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    _bootstrapped = True


@click.group(context_settings=dict(ignore_unknown_options=True))
@click.option('--settings', default=None, help='Django settings module path')
@click.option('--project', default=None, help='Path to Django project directory')
@click.pass_context
def cli(ctx, settings, project):
    ctx.ensure_object(dict)
    ctx.obj['settings'] = settings
    ctx.obj['project'] = project


def _run_management_command(ctx, command_name, args):
    _ensure_django_ready(
        settings_module=ctx.obj.get('settings'),
        project_dir=ctx.obj.get('project'),
    )
    from django.core.management import call_command

    call_command(command_name, *args)


@cli.command('er_export', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def er_export(ctx, args):
    _run_management_command(ctx, 'er_export', args)


@cli.command('er_convert', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def er_convert(ctx, args):
    _run_management_command(ctx, 'er_convert', args)


@cli.command('er_makemigrations', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def er_makemigrations(ctx, args):
    _run_management_command(ctx, 'er_makemigrations', args)


@cli.command('er_showmigrations', context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def er_showmigrations(ctx, args):
    _run_management_command(ctx, 'er_showmigrations', args)


def main():
    cli()
