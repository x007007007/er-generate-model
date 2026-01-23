"""
测试CLI命令行接口
"""
import pytest
from click.testing import CliRunner
from pathlib import Path
from x007007007.er_migrate.cli import cli


class TestMakeMigrationsCommand:
    """测试makemigrations命令"""
    
    def test_makemigrations_basic(self, tmp_path):
        """CLI-001: 测试基本的makemigrations命令"""
        # 创建ER图文件
        er_file = tmp_path / "schema.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(er_file),
            '--migrations-dir', str(migrations_dir)
        ])
        
        # 验证命令成功
        assert result.exit_code == 0
        assert "Migrations for 'blog'" in result.output
        assert "0001_initial.yaml" in result.output
        
        # 验证文件已创建
        migration_file = migrations_dir / "blog" / "0001_initial.yaml"
        assert migration_file.exists()
    
    def test_makemigrations_no_changes(self, tmp_path):
        """测试无变更时的行为"""
        # 创建ER图文件
        er_file = tmp_path / "schema.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        
        # 第一次运行
        result1 = runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(er_file),
            '--migrations-dir', str(migrations_dir)
        ])
        assert result1.exit_code == 0
        
        # 第二次运行（无变更）
        result2 = runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(er_file),
            '--migrations-dir', str(migrations_dir)
        ])
        
        assert result2.exit_code == 0
        assert "No changes detected" in result2.output
    
    def test_makemigrations_missing_file(self, tmp_path):
        """测试ER文件不存在时的错误处理"""
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(tmp_path / "nonexistent.mmd"),
            '--migrations-dir', str(migrations_dir)
        ])
        
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "not found" in result.output.lower()
    
    def test_makemigrations_custom_name(self, tmp_path):
        """测试自定义迁移名称"""
        er_file = tmp_path / "schema.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(er_file),
            '--migrations-dir', str(migrations_dir),
            '--name', 'custom_migration'
        ])
        
        assert result.exit_code == 0
        assert "custom_migration" in result.output


class TestShowMigrationsCommand:
    """测试showmigrations命令"""
    
    def test_showmigrations_basic(self, tmp_path):
        """CLI-002: 测试showmigrations命令"""
        # 先创建一些迁移
        er_file = tmp_path / "schema.mmd"
        er_file.write_text("""
erDiagram
    User {
        uuid id PK
        string username
    }
""")
        
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        
        # 创建迁移
        runner.invoke(cli, [
            'makemigrations',
            '--namespace', 'blog',
            '--er-file', str(er_file),
            '--migrations-dir', str(migrations_dir)
        ])
        
        # 显示迁移
        result = runner.invoke(cli, [
            'showmigrations',
            '--namespace', 'blog',
            '--migrations-dir', str(migrations_dir)
        ])
        
        assert result.exit_code == 0
        assert "blog" in result.output
        assert "0001_initial" in result.output
    
    def test_showmigrations_empty(self, tmp_path):
        """测试空命名空间"""
        migrations_dir = tmp_path / ".migrations"
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'showmigrations',
            '--namespace', 'blog',
            '--migrations-dir', str(migrations_dir)
        ])
        
        assert result.exit_code == 0
        assert "No migrations found" in result.output or "blog" in result.output
    
    def test_showmigrations_all_namespaces(self, tmp_path):
        """测试显示所有命名空间"""
        # 创建多个命名空间的迁移
        migrations_dir = tmp_path / ".migrations"
        
        for namespace in ['blog', 'auth']:
            er_file = tmp_path / f"{namespace}.mmd"
            er_file.write_text(f"""
erDiagram
    {namespace.capitalize()} {{
        uuid id PK
    }}
""")
            
            runner = CliRunner()
            runner.invoke(cli, [
                'makemigrations',
                '--namespace', namespace,
                '--er-file', str(er_file),
                '--migrations-dir', str(migrations_dir)
            ])
        
        # 显示所有迁移
        result = runner.invoke(cli, [
            'showmigrations',
            '--migrations-dir', str(migrations_dir)
        ])
        
        assert result.exit_code == 0
        assert "blog" in result.output
        assert "auth" in result.output


class TestVersionCommand:
    """测试version命令"""
    
    def test_version(self):
        """测试--version选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "0." in result.output


class TestHelpCommand:
    """测试help命令"""
    
    def test_help(self):
        """测试--help选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "makemigrations" in result.output
        assert "showmigrations" in result.output
    
    def test_makemigrations_help(self):
        """测试makemigrations --help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['makemigrations', '--help'])
        
        assert result.exit_code == 0
        assert "namespace" in result.output.lower()
        assert "er-file" in result.output.lower()
