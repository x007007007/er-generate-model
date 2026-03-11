"""
ModelClassifier - 模型分类器

该模块负责在 Export 阶段识别模型是项目内模型还是第三方模型。
"""

import os
from pathlib import Path


class ModelClassifier:
    """
    分类模型为项目内或第三方
    
    该类用于判断 Django 模型是否属于项目内模型（位于项目 src/ 目录下）
    还是第三方模型（位于项目 src/ 目录外）。
    
    Attributes:
        project_root: 项目根目录的绝对路径
    """
    
    def __init__(self, project_root: str):
        """
        初始化分类器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = os.path.abspath(project_root)


    def classify(self, model_class: type) -> str:
        """
        分类模型为项目内或第三方

        该方法通过检查模型类的源文件路径来判断模型是否属于项目内模型。
        如果模型的源文件位于项目的 src/ 目录下，则分类为 "project"，
        否则分类为 "third-party"。

        Args:
            model_class: Django 模型类或任何 Python 类

        Returns:
            "project" 如果模型在项目 src/ 目录下
            "third-party" 如果模型在项目 src/ 目录外

        Raises:
            ValueError: 如果无法获取模型的源文件路径

        Examples:
            >>> classifier = ModelClassifier("/path/to/project")
            >>> classifier.classify(MyModel)
            'project'
        """
        import inspect

        try:
            # 使用 inspect.getfile() 获取源文件路径
            source_file = inspect.getfile(model_class)
        except (TypeError, OSError) as e:
            # 处理内置类型、动态生成的类等无法获取源文件的情况
            raise ValueError(
                f"Cannot determine source file for {model_class.__name__}: {e}"
            )

        # 转换为绝对路径
        source_file_abs = os.path.abspath(source_file)

        # 构建项目 src/ 目录的绝对路径
        src_dir = os.path.join(self.project_root, "src")
        src_dir_abs = os.path.abspath(src_dir)

        # 判断源文件是否在项目 src/ 目录下
        # 使用 Path.is_relative_to() 或者字符串前缀匹配
        try:
            # Python 3.9+ 支持 is_relative_to
            source_path = Path(source_file_abs)
            src_path = Path(src_dir_abs)
            if source_path.is_relative_to(src_path):
                return "project"
            else:
                return "third-party"
        except AttributeError:
            # Python 3.8 及以下版本的兼容处理
            # 使用字符串前缀匹配，确保路径分隔符正确
            if source_file_abs.startswith(src_dir_abs + os.sep):
                return "project"
            else:
                return "third-party"

    def get_namespace(self, model_class: type) -> str:
        """
        获取模型的命名空间
        
        该方法从模型类的 __module__ 属性提取命名空间。
        命名空间是 Python 模块的完整路径，例如 "myapp.models.user"。
        
        Args:
            model_class: Django 模型类或任何 Python 类
            
        Returns:
            模型的完整命名空间字符串
            
        Raises:
            ValueError: 如果无法获取模型的命名空间（__module__ 属性缺失、为 None 或为空）
            
        Examples:
            >>> classifier = ModelClassifier("/path/to/project")
            >>> classifier.get_namespace(MyModel)
            'myapp.models'
            
        Notes:
            - 处理边界情况：
              * 内置模块（如 __main__, __builtin__）：返回原始值
              * 动态生成的类：如果有 __module__ 属性则返回，否则抛出异常
              * None 或空 __module__：抛出 ValueError
        """
        # 检查 __module__ 属性是否存在
        if not hasattr(model_class, '__module__'):
            raise ValueError(
                f"Cannot determine namespace for {model_class.__name__}: "
                f"missing __module__ attribute"
            )
        
        # 获取 __module__ 属性
        namespace = model_class.__module__
        
        # 处理 None 或空字符串的情况
        if namespace is None:
            raise ValueError(
                f"Cannot determine namespace for {model_class.__name__}: "
                f"__module__ is None"
            )
        
        if not isinstance(namespace, str):
            raise ValueError(
                f"Cannot determine namespace for {model_class.__name__}: "
                f"__module__ is not a string (got {type(namespace).__name__})"
            )
        
        if not namespace.strip():
            raise ValueError(
                f"Cannot determine namespace for {model_class.__name__}: "
                f"__module__ is empty"
            )
        
        # 返回命名空间
        # 注意：对于内置模块（如 __main__, __builtin__）也返回原始值
        # 这些边界情况由调用者处理
        return namespace

