* [x] `bootstrapper.py` 实现了 `_detect_django()` 运行时检测

* [x] `bootstrapper.py` 实现了 `_inject_installed_apps()` 动态注入到 `INSTALLED_APPS`

* [x] `bootstrapper.py` 实现了 `bootstrap_django()` 主引导函数

* [x] `bootstrapper.py` 实现了 `_discover_settings_module()` 自动检测 settings module

* [x] `cli.py` 使用 click 库创建了 CLI 框架

* [x] `cli.py` 支持 `--settings` 和 `--project` 全局参数

* [x] `cli.py` 实现了 `er_export` 子命令委托

* [x] `cli.py` 实现了 `er_convert` 子命令委托

* [x] `cli.py` 实现了 `er_makemigrations` 子命令委托

* [x] `cli.py` 实现了 `er_showmigrations` 子命令委托

* [x] `__main__.py` 支持 `python -m x007007007.er_django` 运行

* [x] `pyproject.toml` 注册了 `er-django` console\_scripts entry point

* [x] 未安装 Django 时输出友好的错误信息

* [x] 已在 `INSTALLED_APPS` 时不重复添加

* [x] 现有 Django app 集成方式（management commands）不受影响，向后兼容

* [x] 测试覆盖了 bootstrapper 的核心逻辑

* [x] 测试覆盖了 CLI 子命令委托逻辑

* [x] 测试覆盖了 settings module 自动发现逻辑

