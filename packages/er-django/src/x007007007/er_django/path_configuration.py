"""Path configuration management for Django ER export."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PathConfiguration:
    """路径配置管理类
    
    管理扫描路径、输出路径和三方包输出路径的配置。
    提供配置继承规则和验证功能。
    
    Attributes:
        scan_path: 扫描Django模型的源代码目录路径
        output_path: 生成代码的输出目录路径
        third_party_output_path: 三方包代码的专用输出目录路径
        third_party_package_prefix: 三方包的包名前缀（可选）
    """
    
    scan_path: Path
    output_path: Path
    third_party_output_path: Path
    third_party_package_prefix: Optional[str] = None
    
    @classmethod
    def from_options(
        cls,
        scan_path: Optional[str] = None,
        output_path: Optional[str] = None,
        third_party_output_path: Optional[str] = None,
        third_party_package_prefix: Optional[str] = None,
        working_dir: Optional[Path] = None
    ) -> 'PathConfiguration':
        """从命令行选项创建配置对象，应用默认值和继承规则
        
        继承规则：
        1. scan_path默认为'src'
        2. output_path默认继承scan_path
        3. third_party_output_path默认为output_path/third
        4. third_party_package_prefix默认为third_party_output_path的最后一个目录名
        
        Args:
            scan_path: 扫描路径（可选，默认为'src'）
            output_path: 输出路径（可选，默认继承scan_path）
            third_party_output_path: 三方包输出路径（可选，默认为output_path/third）
            third_party_package_prefix: 三方包包名前缀（可选，默认为third_party_output_path的最后一个目录名）
            working_dir: 工作目录（可选，默认为当前工作目录）
            
        Returns:
            PathConfiguration实例
        """
        working_dir = working_dir or Path.cwd()
        
        # 应用默认值和继承规则
        resolved_scan_path = Path(scan_path) if scan_path else Path('src')
        resolved_output_path = Path(output_path) if output_path else resolved_scan_path
        
        # 解析相对路径
        if not resolved_scan_path.is_absolute():
            resolved_scan_path = working_dir / resolved_scan_path
        if not resolved_output_path.is_absolute():
            resolved_output_path = working_dir / resolved_output_path
            
        # 处理third_party_output_path
        if third_party_output_path:
            resolved_third_path = Path(third_party_output_path)
            # 如果是相对路径，相对于output_path解析
            if not resolved_third_path.is_absolute():
                resolved_third_path = resolved_output_path / resolved_third_path
        else:
            resolved_third_path = resolved_output_path / 'third'
        
        # 处理包名前缀
        if third_party_package_prefix is None:
            # 使用third_party_output_path的最后一个目录名
            third_party_package_prefix = resolved_third_path.name
        
        return cls(
            scan_path=resolved_scan_path,
            output_path=resolved_output_path,
            third_party_output_path=resolved_third_path,
            third_party_package_prefix=third_party_package_prefix
        )
    
    def validate(self) -> List[str]:
        """验证配置的有效性，返回错误列表
        
        验证规则：
        1. scan_path必须存在
        2. third_party_package_prefix必须是有效的Python标识符
        
        Returns:
            错误消息列表，如果配置有效则返回空列表
        """
        errors = []
        
        # 验证scan_path存在
        if not self.scan_path.exists():
            errors.append(f"Scan path does not exist: {self.scan_path}")
        
        # 验证包名前缀格式
        if self.third_party_package_prefix:
            if not self.third_party_package_prefix.isidentifier():
                errors.append(
                    f"Invalid package prefix: {self.third_party_package_prefix}. "
                    "Must be a valid Python identifier."
                )
        
        return errors
