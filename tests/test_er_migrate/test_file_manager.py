"""
测试文件管理器
"""
import pytest
from pathlib import Path
from x007007007.er_migrate.file_manager import FileManager
from x007007007.er_migrate.models import (
    Migration,
    CreateTable,
    ColumnDefinition,
)


class TestFileManager:
    """测试文件管理器"""
    
    def test_init_file_manager(self, tmp_path):
        """测试初始化文件管理器"""
        fm = FileManager(str(tmp_path))
        assert fm.migrations_dir == tmp_path
    
    def test_get_namespace_dir(self, tmp_path):
        """测试获取命名空间目录"""
        fm = FileManager(str(tmp_path))
        namespace_dir = fm.get_namespace_dir("blog")
        assert namespace_dir == tmp_path / "blog"
    
    def test_list_migration_files_empty(self, tmp_path):
        """测试列出空命名空间的迁移文件"""
        fm = FileManager(str(tmp_path))
        files = fm.list_migration_files("blog")
        assert files == []
    
    def test_save_migration(self, tmp_path):
        """测试保存迁移文件"""
        fm = FileManager(str(tmp_path))
        
        migration = Migration(
            name="initial",
            namespace="blog",
            operations=[
                CreateTable(
                    table_name="user",
                    columns=[
                        ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False)
                    ]
                )
            ]
        )
        
        file_path = fm.save_migration(migration)
        
        # 验证文件已创建
        assert file_path.exists()
        assert file_path.name == "0001_initial.yaml"
        assert file_path.parent.name == "blog"
    
    def test_save_multiple_migrations(self, tmp_path):
        """测试保存多个迁移文件"""
        fm = FileManager(str(tmp_path))
        
        # 保存第一个迁移
        migration1 = Migration(
            name="initial",
            namespace="blog",
            operations=[]
        )
        file1 = fm.save_migration(migration1)
        assert file1.name == "0001_initial.yaml"
        
        # 保存第二个迁移
        migration2 = Migration(
            name="add_posts",
            namespace="blog",
            operations=[]
        )
        file2 = fm.save_migration(migration2)
        assert file2.name == "0002_add_posts.yaml"
    
    def test_load_migration(self, tmp_path):
        """测试加载迁移文件"""
        fm = FileManager(str(tmp_path))
        
        # 先保存
        original = Migration(
            name="initial",
            namespace="blog",
            operations=[
                CreateTable(
                    table_name="user",
                    columns=[
                        ColumnDefinition(name="id", type="uuid", primary_key=True, nullable=False)
                    ]
                )
            ]
        )
        fm.save_migration(original)
        
        # 再加载
        loaded = fm.load_migration("blog", "0001_initial.yaml")
        
        assert loaded.name == "initial"
        assert loaded.namespace == "blog"
        assert len(loaded.operations) == 1
        assert isinstance(loaded.operations[0], CreateTable)
    
    def test_load_nonexistent_migration(self, tmp_path):
        """测试加载不存在的迁移文件"""
        fm = FileManager(str(tmp_path))
        
        with pytest.raises(FileNotFoundError):
            fm.load_migration("blog", "0001_initial.yaml")
    
    def test_list_migration_files(self, tmp_path):
        """测试列出迁移文件"""
        fm = FileManager(str(tmp_path))
        
        # 创建多个迁移
        for i, name in enumerate(["initial", "add_posts", "add_comments"], 1):
            migration = Migration(name=name, namespace="blog", operations=[])
            fm.save_migration(migration)
        
        # 列出文件
        files = fm.list_migration_files("blog")
        
        assert len(files) == 3
        assert files[0] == "0001_initial.yaml"
        assert files[1] == "0002_add_posts.yaml"
        assert files[2] == "0003_add_comments.yaml"
    
    def test_load_namespace_migrations(self, tmp_path):
        """测试加载命名空间下的所有迁移"""
        fm = FileManager(str(tmp_path))
        
        # 创建多个迁移
        for name in ["initial", "add_posts"]:
            migration = Migration(name=name, namespace="blog", operations=[])
            fm.save_migration(migration)
        
        # 加载所有迁移
        migrations = fm.load_namespace_migrations("blog")
        
        assert len(migrations) == 2
        assert migrations[0].name == "initial"
        assert migrations[1].name == "add_posts"
    
    def test_get_next_migration_number(self, tmp_path):
        """测试获取下一个迁移序号"""
        fm = FileManager(str(tmp_path))
        
        # 空命名空间
        assert fm.get_next_migration_number("blog") == 1
        
        # 创建一个迁移
        migration = Migration(name="initial", namespace="blog", operations=[])
        fm.save_migration(migration)
        
        assert fm.get_next_migration_number("blog") == 2
    
    def test_filename_generation_with_special_chars(self, tmp_path):
        """测试文件名生成 - 特殊字符处理"""
        fm = FileManager(str(tmp_path))
        
        migration = Migration(
            name="Add User's Email & Phone!",
            namespace="blog",
            operations=[]
        )
        
        file_path = fm.save_migration(migration)
        
        # 特殊字符应该被清理
        assert file_path.name == "0001_add_users_email_phone.yaml"
    
    def test_multiple_namespaces(self, tmp_path):
        """测试多个命名空间"""
        fm = FileManager(str(tmp_path))
        
        # 创建blog命名空间的迁移
        blog_migration = Migration(name="initial", namespace="blog", operations=[])
        fm.save_migration(blog_migration)
        
        # 创建auth命名空间的迁移
        auth_migration = Migration(name="initial", namespace="auth", operations=[])
        fm.save_migration(auth_migration)
        
        # 验证两个命名空间独立
        blog_files = fm.list_migration_files("blog")
        auth_files = fm.list_migration_files("auth")
        
        assert len(blog_files) == 1
        assert len(auth_files) == 1
        assert blog_files[0] == "0001_initial.yaml"
        assert auth_files[0] == "0001_initial.yaml"
