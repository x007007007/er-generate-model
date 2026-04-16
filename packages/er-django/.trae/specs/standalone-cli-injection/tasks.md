# Tasks

- [x] Task 1: 创建 Django 动态引导模块 `bootstrapper.py`
  - [x] SubTask 1.1: 实现 `_detect_django()` 运行时检测函数
  - [x] SubTask 1.2: 实现 `_inject_installed_apps()` 将 `x007007007.er_django` 动态注入到 `INSTALLED_APPS`
  - [x] SubTask 1.3: 实现 `bootstrap_django(settings_module=None, project_dir=None)` 主引导函数
  - [x] SubTask 1.4: 实现 `_discover_settings_module(project_dir)` 自动检测 settings module

- [x] Task 2: 创建独立 CLI 入口 `cli.py`
  - [x] SubTask 2.1: 使用 `click` 库创建 CLI 框架（项目已有 click 依赖）
  - [x] SubTask 2.2: 实现 `--settings` 和 `--project` 全局参数
  - [x] SubTask 2.3: 实现 `er_export` 子命令，委托给 Django management command
  - [x] SubTask 2.4: 实现 `er_convert` 子命令，委托给 Django management command
  - [x] SubTask 2.5: 实现 `er_makemigrations` 子命令，委托给 Django management command
  - [x] SubTask 2.6: 实现 `er_showmigrations` 子命令，委托给 Django management command
  - [x] SubTask 2.7: 实现 `__main__.py` 支持 `python -m x007007007.er_django` 运行

- [x] Task 3: 更新 `pyproject.toml` 注册 console_scripts
  - [x] SubTask 3.1: 添加 `[project.scripts]` 配置 `er-django = "x007007007.er_django.cli:main"`

- [x] Task 4: 编写测试
  - [x] SubTask 4.1: 测试 `bootstrapper.py` 的 Django 检测、注入和引导逻辑
  - [x] SubTask 4.2: 测试 `cli.py` 的子命令委托逻辑
  - [x] SubTask 4.3: 测试 settings module 自动发现逻辑
  - [x] SubTask 4.4: 测试向后兼容性（作为 Django app 安装时仍正常工作）

# Task Dependencies
- Task 2 depends on Task 1
- Task 4 depends on Task 1 and Task 2
- Task 3 is independent (can be done in parallel with Task 1)
