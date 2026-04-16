# Standalone CLI with Dynamic Django Injection Spec

## Why

当前 `er-django` 必须作为 Django app 安装到目标项目的 `INSTALLED_APPS` 中才能使用其 management commands（`er_convert`、`er_export`、`er_makemigrations`、`er_showmigrations`）。这意味着每个 Django 项目都需要修改 `settings.py`，增加了集成成本。参考 Celery 和 Gunicorn 的模式，可以通过独立 CLI 命令 + `DJANGO_SETTINGS_MODULE` 的方式动态引导 Django，无需修改目标项目配置。

## What Changes

- 新增 `er-django` 独立 CLI 入口（`console_scripts` entry point），注册为 `er-django` 命令
- 新增 Django 环境引导模块 `bootstrapper.py`，负责动态调用 `django.setup()` 并将自身注入 `INSTALLED_APPS`
- 将现有 4 个 management commands 的核心逻辑抽取为可复用的服务函数，CLI 入口和服务函数解耦
- CLI 支持通过参数指定 Django 项目的 settings module 或项目目录路径
- **保持向后兼容**：现有的 Django app 安装方式继续有效，management commands 不变

## Impact

- Affected code: `pyproject.toml`（新增 entry_points）、新增 `cli.py` 和 `bootstrapper.py`、现有 management commands 的核心逻辑需要抽取
- 不影响现有 Django app 集成方式
- 不影响现有测试

## ADDED Requirements

### Requirement: Standalone CLI Entry Point

系统 SHALL 提供独立的 `er-django` 命令，通过 `console_scripts` entry point 注册。

#### Scenario: 通过 settings module 运行
- **WHEN** 用户执行 `er-django --settings=myproject.settings er_export --format=toml`
- **THEN** 系统动态引导 Django（调用 `django.setup()`），将 `x007007007.er_django` 注入到 `INSTALLED_APPS`，然后执行对应的 management command

#### Scenario: 通过项目目录运行
- **WHEN** 用户执行 `er-django --project=/path/to/myproject er_export --format=toml`
- **THEN** 系统自动检测项目目录中的 `settings.py` 或 `wsgi.py`，推导 `DJANGO_SETTINGS_MODULE`，然后引导 Django 并执行命令

#### Scenario: 无 Django 环境时友好报错
- **WHEN** 用户在未安装 Django 的环境中执行 `er-django`
- **THEN** 系统输出友好的错误信息，提示需要安装 Django

### Requirement: Django Dynamic Bootstrap

系统 SHALL 提供 Django 动态引导机制，在运行时将自身注入到 Django 的 `INSTALLED_APPS` 中。

#### Scenario: 动态注入 INSTALLED_APPS
- **WHEN** `er-django` CLI 引导 Django
- **THEN** 系统在调用 `django.setup()` 之前，将 `x007007007.er_django` 追加到 `django.conf.settings.INSTALLED_APPS`（如果尚未存在）
- **AND** `django.setup()` 执行后，所有 Django app 机制（management commands、templates、templatetags）均正常工作

#### Scenario: 已在 INSTALLED_APPS 中时不重复添加
- **WHEN** 目标项目的 `INSTALLED_APPS` 已包含 `x007007007.er_django`
- **THEN** 系统不重复添加，直接执行命令

### Requirement: Sub-command Delegation

系统 SHALL 支持将 CLI 子命令委托给对应的 Django management command。

#### Scenario: 支持所有现有 management commands
- **WHEN** 用户执行 `er-django er_export`、`er-django er_convert`、`er-django er_makemigrations` 或 `er-django er_showmigrations`
- **THEN** 系统将命令及其参数完整传递给对应的 Django management command

#### Scenario: 未知子命令报错
- **WHEN** 用户执行 `er-django unknown_command`
- **THEN** 系统输出可用的子命令列表和用法说明

### Requirement: Configuration Flexibility

系统 SHALL 支持多种方式指定 Django settings module。

#### Scenario: 通过 --settings 参数
- **WHEN** 用户通过 `--settings=myproject.settings` 指定 settings module
- **THEN** 系统使用该值设置 `DJANGO_SETTINGS_MODULE` 环境变量

#### Scenario: 通过 --project 参数
- **WHEN** 用户通过 `--project=/path/to/django/project` 指定项目目录
- **THEN** 系统扫描项目目录，查找包含 `BASE_DIR` 或 `ROOT_URLCONF` 的 Python 模块，自动推导 `DJANGO_SETTINGS_MODULE`

#### Scenario: 通过环境变量
- **WHEN** 用户已设置 `DJANGO_SETTINGS_MODULE` 环境变量
- **THEN** 系统直接使用该环境变量，无需额外参数

## MODIFIED Requirements

### Requirement: pyproject.toml Entry Points

pyproject.toml SHALL 新增 `[project.scripts]` 配置，注册 `er-django` 命令：

```toml
[project.scripts]
er-django = "x007007007.er_django.cli:main"
```
