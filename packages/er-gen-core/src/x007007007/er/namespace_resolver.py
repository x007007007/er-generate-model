"""
命名空间解析器

该模块实现了 NamespaceResolver 类，负责将 Python 模块命名空间转换为对应的 TOML 文件路径。

核心功能：
- 接收命名空间字符串（如 kinkotech.common.models.base）
- 按优先级搜索对应的 TOML 文件（先 src/，后 src/third/）
- 返回文件路径和位置类型（project 或 third-party）
- 处理未找到的情况，返回详细错误信息
- 实现缓存机制以提高性能
"""

import os
from typing import Dict, List, Optional

from .namespace_models import NamespaceNotFoundError, ResolveResult


class NamespaceResolver:
    """解析命名空间到 TOML 文件路径
    
    NamespaceResolver 负责将 Python 模块命名空间映射到文件系统中的 TOML 文件。
    它支持多个搜索路径，并按优先级顺序搜索。
    
    Attributes:
        search_paths: 搜索路径列表，按优先级排序
        config: 可选的配置对象
        _cache: 内部缓存字典，存储已解析的命名空间结果
    
    Example:
        >>> resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
        >>> result = resolver.resolve("kinkotech.common.models.base")
        >>> print(result.file_path)
        src/kinkotech/common/models/base.toml
        >>> print(result.location_type)
        project
    """
    
    def __init__(self, search_paths: List[str], config: Optional[object] = None):
        """初始化命名空间解析器
        
        Args:
            search_paths: 搜索路径列表，按优先级排序。例如 ["src/", "src/third/"]
            config: 可选的配置对象，用于自定义解析行为
        
        Raises:
            ValueError: 如果 search_paths 为空
        """
        if not search_paths:
            raise ValueError("search_paths cannot be empty")
        
        self.search_paths = search_paths
        self.config = config
        self._cache: Dict[str, ResolveResult] = {}
    
    def _validate_namespace(self, namespace: str) -> None:
        """验证命名空间的安全性，防止路径遍历攻击
        
        该方法检查命名空间字符串是否包含可能导致路径遍历的字符或模式。
        
        Args:
            namespace: 要验证的命名空间字符串
        
        Raises:
            ValueError: 如果命名空间包含不安全的字符或模式
        
        Security:
            防止以下攻击模式：
            - 路径遍历：".."
            - 绝对路径：以 "/" 开头
            - Windows 路径：包含 "\\" 或 ":"
            - 空命名空间
        
        Example:
            >>> resolver._validate_namespace("myapp.models")  # OK
            >>> resolver._validate_namespace("../etc/passwd")  # Raises ValueError
            >>> resolver._validate_namespace("/etc/passwd")  # Raises ValueError
        """
        if not namespace:
            raise ValueError("Namespace cannot be empty")
        
        # 防止路径遍历攻击
        if ".." in namespace:
            raise ValueError(
                f"Invalid namespace '{namespace}': contains '..' which could lead to path traversal"
            )
        
        # 防止使用绝对路径
        if namespace.startswith("/"):
            raise ValueError(
                f"Invalid namespace '{namespace}': cannot start with '/' (absolute path)"
            )
        
        # 防止 Windows 风格的路径
        if "\\" in namespace:
            raise ValueError(
                f"Invalid namespace '{namespace}': contains '\\' (Windows path separator)"
            )
        
        # 防止 Windows 驱动器字母
        if ":" in namespace:
            raise ValueError(
                f"Invalid namespace '{namespace}': contains ':' (Windows drive letter)"
            )
        
        # 防止使用正斜杠（应该使用点号）
        if "/" in namespace:
            raise ValueError(
                f"Invalid namespace '{namespace}': contains '/' (use '.' for namespace separation)"
            )
    
    def _namespace_to_path(self, namespace: str) -> str:
        """将命名空间转换为相对文件路径
        
        该方法将 Python 模块命名空间转换为对应的 TOML 文件路径。
        转换规则：
        1. 将命名空间中的点号（.）替换为路径分隔符（/）
        2. 在路径末尾添加 .toml 扩展名
        
        Args:
            namespace: Python 模块命名空间，如 "kinkotech.common.models.base"
        
        Returns:
            相对文件路径，如 "kinkotech/common/models/base.toml"
        
        Raises:
            ValueError: 如果命名空间为空或包含不安全的字符
        
        Example:
            >>> resolver._namespace_to_path("myapp.models")
            'myapp/models.toml'
            >>> resolver._namespace_to_path("kinkotech.common.models.base")
            'kinkotech/common/models/base.toml'
            >>> resolver._namespace_to_path("django.contrib.auth.models")
            'django/contrib/auth/models.toml'
        
        Note:
            该方法假设命名空间已经通过 _validate_namespace 验证，
            因此可以安全地进行路径转换。
        """
        # 验证命名空间（防止路径遍历攻击）
        self._validate_namespace(namespace)
        
        # 将点号替换为路径分隔符
        relative_path = namespace.replace('.', os.sep)
        
        # 添加 .toml 扩展名
        toml_path = relative_path + '.toml'
        
        return toml_path
    
    def resolve(self, namespace: str) -> ResolveResult:
        """解析命名空间到文件路径
        
        该方法按优先级搜索命名空间对应的 TOML 文件，并返回解析结果。
        搜索顺序：按 search_paths 列表的顺序搜索，在第一个找到文件的路径停止。
        
        Args:
            namespace: Python 模块命名空间，如 "kinkotech.common.models.base"
        
        Returns:
            ResolveResult: 包含文件路径、位置类型和元数据的解析结果
        
        Raises:
            NamespaceNotFoundError: 当命名空间无法在任何搜索路径中解析时
        
        Example:
            >>> resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
            >>> result = resolver.resolve("myapp.models.user")
            >>> print(result.file_path)
            src/myapp/models/user.toml
            >>> print(result.location_type)
            project
            
            >>> result = resolver.resolve("django.contrib.auth.models")
            >>> print(result.file_path)
            src/third/django/contrib/auth/models.toml
            >>> print(result.location_type)
            third-party
        
        Note:
            - 该方法会自动使用缓存，避免重复的文件系统访问
            - 位置类型根据搜索路径自动确定：
              - 如果在 "src/" 中找到，location_type 为 "project"
              - 如果在 "src/third/" 中找到，location_type 为 "third-party"
              - 其他路径的 location_type 为 "unknown"
        """
        # 检查缓存
        if namespace in self._cache:
            return self._cache[namespace]
        
        # 步骤 1: 转换命名空间为相对路径
        relative_path = self._namespace_to_path(namespace)
        
        # 步骤 2: 按优先级搜索
        for search_path in self.search_paths:
            # 步骤 3: 构造完整路径
            full_path = os.path.join(search_path, relative_path)
            
            # 步骤 4: 检查文件是否存在
            if os.path.exists(full_path):
                # 步骤 5: 确定位置类型
                # 根据搜索路径判断位置类型
                # 规范化搜索路径以便比较（移除尾部分隔符）
                normalized_search_path = search_path.rstrip(os.sep)
                
                # 检查是否为标准的 src/ 路径（项目模型）
                if normalized_search_path.endswith("src") or normalized_search_path == "src":
                    location_type = "project"
                # 检查是否为 src/third/ 路径（第三方模型）
                elif normalized_search_path.endswith("src/third") or normalized_search_path.endswith("src\\third"):
                    location_type = "third-party"
                else:
                    # 对于其他自定义搜索路径，尝试智能判断
                    if "third" in search_path:
                        location_type = "third-party"
                    else:
                        location_type = "unknown"
                
                # 步骤 6: 创建解析结果
                result = ResolveResult(
                    namespace=namespace,
                    file_path=full_path,
                    location_type=location_type,
                    exists=True,
                    search_path=search_path,
                    metadata={}
                )
                
                # 缓存结果
                self._cache[namespace] = result
                
                return result
        
        # 步骤 7: 未找到，抛出异常
        raise NamespaceNotFoundError(namespace, self.search_paths)

    def resolve_batch(self, namespaces: List[str]) -> Dict[str, Optional[ResolveResult]]:
        """批量解析多个命名空间
        
        该方法批量解析多个命名空间，返回一个字典映射命名空间到解析结果。
        对于无法解析的命名空间，返回 None 而不是抛出异常，以便继续处理其他命名空间。
        
        Args:
            namespaces: 命名空间列表
        
        Returns:
            字典，键为命名空间，值为 ResolveResult 对象（如果解析成功）或 None（如果解析失败）
        
        Example:
            >>> resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
            >>> results = resolver.resolve_batch([
            ...     "myapp.models.user",
            ...     "django.contrib.auth.models",
            ...     "nonexistent.module"
            ... ])
            >>> print(results["myapp.models.user"].location_type)
            project
            >>> print(results["django.contrib.auth.models"].location_type)
            third-party
            >>> print(results["nonexistent.module"])
            None
        
        Note:
            - 该方法使用现有的 resolve() 方法，因此会自动利用缓存
            - 解析失败的命名空间不会中断整个批量处理
            - 建议在批量处理后检查 None 值，以识别解析失败的命名空间
        """
        results: Dict[str, Optional[ResolveResult]] = {}
        
        for namespace in namespaces:
            try:
                result = self.resolve(namespace)
                results[namespace] = result
            except NamespaceNotFoundError:
                # 对于无法解析的命名空间，返回 None 而不是抛出异常
                results[namespace] = None
        
        return results
    
    def clear_cache(self) -> None:
        """清除所有缓存的解析结果
        
        该方法清除内部缓存字典中的所有条目，强制后续的 resolve() 调用
        重新执行文件系统搜索。
        
        Example:
            >>> resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
            >>> result = resolver.resolve("myapp.models.user")  # 执行文件系统搜索
            >>> result = resolver.resolve("myapp.models.user")  # 使用缓存
            >>> resolver.clear_cache()
            >>> result = resolver.resolve("myapp.models.user")  # 重新执行文件系统搜索
        
        Note:
            在以下情况下应该调用此方法：
            - 文件系统结构发生变化（如添加或删除 TOML 文件）
            - 搜索路径配置发生变化
            - 需要强制刷新所有解析结果
        """
        self._cache.clear()
    
    def invalidate(self, namespace: str) -> None:
        """使特定命名空间的缓存失效
        
        该方法从缓存中移除指定命名空间的解析结果，强制下次 resolve() 调用
        重新执行文件系统搜索。
        
        Args:
            namespace: 要使缓存失效的命名空间
        
        Example:
            >>> resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
            >>> result = resolver.resolve("myapp.models.user")  # 执行文件系统搜索
            >>> result = resolver.resolve("myapp.models.user")  # 使用缓存
            >>> resolver.invalidate("myapp.models.user")
            >>> result = resolver.resolve("myapp.models.user")  # 重新执行文件系统搜索
        
        Note:
            在以下情况下应该调用此方法：
            - 特定 TOML 文件被修改或删除
            - 需要刷新特定命名空间的解析结果
            - 如果命名空间不在缓存中，该方法不会产生任何效果
        """
        if namespace in self._cache:
            del self._cache[namespace]
