"""
端到端测试 - 测试完整的工作流程
"""
import pytest
from pathlib import Path
from click.testing import CliRunner
from x007007007.er_migrate.cli import cli


class TestEndToEnd:
    """端到端测试"""
    
    def test_complete_workflow(self, tmp_path):
        """测试完整的工作流程：创建初始迁移 -> 修改ER图 -> 生成新迁移"""
        runner = CliRunner()
        migrations_dir = tmp_path / ".migrations"
        
        # 1. 创建初始ER图
        er_file_v1 = tmp_path / "schema_v1.mmd"
        er_file_v1.write_text("""
erDiagram
    User {
        uuid id PK
        string username UK
        datetime created_at
    }
""")
        
        # 2. 生成初始迁移
        result1 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(er_file_v1),
            '-d', str(migrations_dir)
        ])
        
        assert result1.exit_code == 0
        assert "0001_initial.yaml" in result1.output
        
        # 验证文件已创建
        migration1 = migrations_dir / "blog" / "0001_initial.yaml"
        assert migration1.exists()
        
        # 3. 显示迁移状态
        result2 = runner.invoke(cli, [
            'showmigrations',
            '-n', 'blog',
            '-d', str(migrations_dir)
        ])
        
        assert result2.exit_code == 0
        assert "blog" in result2.output
        assert "0001_initial" in result2.output
        
        # 4. 修改ER图（添加email列）
        er_file_v2 = tmp_path / "schema_v2.mmd"
        er_file_v2.write_text("""
erDiagram
    User {
        uuid id PK
        string username UK
        string email
        datetime created_at
    }
""")
        
        # 5. 生成第二个迁移
        result3 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(er_file_v2),
            '-d', str(migrations_dir)
        ])
        
        assert result3.exit_code == 0
        assert "0002" in result3.output
        
        # 验证第二个迁移文件已创建
        migration_files = list((migrations_dir / "blog").glob("*.yaml"))
        assert len(migration_files) == 2
        
        # 6. 再次显示迁移状态
        result4 = runner.invoke(cli, [
            'showmigrations',
            '-n', 'blog',
            '-d', str(migrations_dir)
        ])
        
        assert result4.exit_code == 0
        assert "0001_initial" in result4.output
        assert "0002" in result4.output
    
    def test_multiple_namespaces_workflow(self, tmp_path):
        """测试多命名空间工作流程"""
        runner = CliRunner()
        migrations_dir = tmp_path / ".migrations"
        
        # 创建auth命名空间的ER图
        auth_er = tmp_path / "auth.mmd"
        auth_er.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        # 创建blog命名空间的ER图
        blog_er = tmp_path / "blog.mmd"
        blog_er.write_text("""
erDiagram
    Post {
        uuid id PK
        string title
    }
""")
        
        # 生成auth迁移
        result1 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'auth',
            '-e', str(auth_er),
            '-d', str(migrations_dir)
        ])
        assert result1.exit_code == 0
        
        # 生成blog迁移
        result2 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(blog_er),
            '-d', str(migrations_dir)
        ])
        assert result2.exit_code == 0
        
        # 显示所有命名空间
        result3 = runner.invoke(cli, [
            'showmigrations',
            '-d', str(migrations_dir)
        ])
        
        assert result3.exit_code == 0
        assert "auth" in result3.output
        assert "blog" in result3.output
    
    def test_no_changes_workflow(self, tmp_path):
        """测试无变更的工作流程"""
        runner = CliRunner()
        migrations_dir = tmp_path / ".migrations"
        
        er_file = tmp_path / "schema.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        # 第一次生成迁移
        result1 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(er_file),
            '-d', str(migrations_dir)
        ])
        assert result1.exit_code == 0
        
        # 第二次生成（无变更）
        result2 = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(er_file),
            '-d', str(migrations_dir)
        ])
        
        assert result2.exit_code == 0
        assert "No changes detected" in result2.output
        
        # 验证只有一个迁移文件
        migration_files = list((migrations_dir / "blog").glob("*.yaml"))
        assert len(migration_files) == 1
    
    def test_complex_er_diagram(self, tmp_path):
        """测试复杂的ER图（包含关系和索引）"""
        runner = CliRunner()
        migrations_dir = tmp_path / ".migrations"
        
        er_file = tmp_path / "complex.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username UK
        string email UK
        datetime created_at
    }
    
    Post {
        uuid id PK
        uuid author_id FK
        string title
        text content
        datetime created_at
    }
    
    User ||--o{ Post : writes
""")
        
        # 生成迁移
        result = runner.invoke(cli, [
            'makemigrations',
            '-n', 'blog',
            '-e', str(er_file),
            '-d', str(migrations_dir)
        ])
        
        # 打印输出以便调试
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")
        
        assert result.exit_code == 0
        
        # 验证迁移文件内容
        migration_file = migrations_dir / "blog" / "0001_initial.yaml"
        assert migration_file.exists()
        
        content = migration_file.read_text()
        assert "User" in content or "user" in content
        assert "Post" in content or "post" in content
        assert "author_id" in content
