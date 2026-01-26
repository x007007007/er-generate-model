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

    def test_multiple_migrations_from_mmd_files(self, tmp_path):
        """测试从不同版本的mmd文件生成多个migration记录"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        parser = MermaidAntlrParser()
        
        # 版本1: 只有User表
        v1_mmd = """erDiagram
    User {
        uuid id PK
        string username
    }
"""
        v1_model = parser.parse(v1_mmd)
        migration1 = generator.generate("blog", v1_model)
        assert migration1 is not None
        assert migration1.name == "initial"
        fm.save_migration(migration1)
        
        files = fm.list_migration_files("blog")
        assert len(files) == 1
        assert files[0] == "0001_initial.yaml"
        
        # 版本2: 添加email列
        v2_mmd = """erDiagram
    User {
        uuid id PK
        string username
        string email
    }
"""
        v2_model = parser.parse(v2_mmd)
        migration2 = generator.generate("blog", v2_model)
        assert migration2 is not None
        assert migration2.name == "add_email"
        assert len(migration2.dependencies) == 1
        assert "0001_initial" in migration2.dependencies[0]
        fm.save_migration(migration2)
        
        files = fm.list_migration_files("blog")
        assert len(files) == 2
        assert files[1] == "0002_add_email.yaml"
        
        # 版本3: 添加Post表和关系
        v3_mmd = """erDiagram
    User ||--o{ Post : writes
    
    User {
        uuid id PK
        string username
        string email
    }
    
    Post {
        uuid id PK
        uuid author_id FK
        string title
    }
"""
        v3_model = parser.parse(v3_mmd)
        migration3 = generator.generate("blog", v3_model)
        assert migration3 is not None
        assert migration3.name == "create_post"
        assert len(migration3.dependencies) == 1
        assert "0002_add_email" in migration3.dependencies[0]
        fm.save_migration(migration3)
        
        files = fm.list_migration_files("blog")
        assert len(files) == 3
        assert files[2] == "0003_create_post.yaml"
        
        # 版本4: 修改列属性
        v4_mmd = """erDiagram
    User ||--o{ Post : writes
    
    User {
        uuid id PK
        string username UK
        string email
    }
    
    Post {
        uuid id PK
        uuid author_id FK
        string title
    }
"""
        v4_model = parser.parse(v4_mmd)
        migration4 = generator.generate("blog", v4_model)
        assert migration4 is not None
        # 应该检测到索引变更
        assert len(migration4.operations) > 0
        fm.save_migration(migration4)
        
        files = fm.list_migration_files("blog")
        assert len(files) == 4
        
        # 验证迁移链的完整性
        migrations = fm.load_namespace_migrations("blog")
        assert len(migrations) == 4
        assert migrations[0].dependencies == []
        assert migrations[1].dependencies == ["blog.0001_initial"]
        assert migrations[2].dependencies == ["blog.0002_add_email"]
        assert migrations[3].dependencies == ["blog.0003_create_post"]
        
        # 验证没有重复的外键
        # 第三个迁移应该有AddForeignKey
        fk_ops_3 = [op for op in migrations[2].operations if op.type == "AddForeignKey"]
        assert len(fk_ops_3) == 1
        
        # 第四个迁移不应该有AddForeignKey（因为外键已经存在）
        fk_ops_4 = [op for op in migrations[3].operations if op.type == "AddForeignKey"]
        assert len(fk_ops_4) == 0

    def test_no_duplicate_migrations_on_repeated_runs(self, tmp_path):
        """测试重复运行相同的mmd文件不会创建重复的migration"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.models import ERModel, Entity, Column, Relationship
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        
        # 使用ERModel直接构建，避免解析器问题
        def create_model():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string", unique=True),
                    Column(name="email", type="string")
                ]
            ))
            model.add_entity(Entity(
                name="Post",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="author_id", type="uuid", is_fk=True),
                    Column(name="title", type="string"),
                    Column(name="content", type="text")
                ]
            ))
            model.add_relationship(Relationship(
                left_entity="Post",
                right_entity="User",
                relation_type="many-to-one",
                left_column="author_id",
                right_column="id"
            ))
            return model
        
        # 第一次运行 - 应该生成初始migration
        model1 = create_model()
        migration1 = generator.generate("blog", model1)
        assert migration1 is not None
        assert migration1.name == "initial"
        fm.save_migration(migration1)
        
        files = fm.list_migration_files("blog")
        assert len(files) == 1
        assert files[0] == "0001_initial.yaml"
        
        # 第二次运行 - 相同的内容，应该返回None
        model2 = create_model()
        migration2 = generator.generate("blog", model2)
        assert migration2 is None, "第二次运行相同内容应该返回None"
        
        files = fm.list_migration_files("blog")
        assert len(files) == 1, "不应该创建新的migration文件"
        
        # 第三次运行 - 再次确认
        model3 = create_model()
        migration3 = generator.generate("blog", model3)
        assert migration3 is None, "第三次运行相同内容应该返回None"
        
        files = fm.list_migration_files("blog")
        assert len(files) == 1, "仍然只应该有一个migration文件"
        
        # 验证migration内容没有变化
        loaded_migration = fm.load_migration("blog", "0001_initial.yaml")
        assert loaded_migration.name == "initial"
        
        # 验证operations数量正确
        create_table_ops = [op for op in loaded_migration.operations if op.type == "CreateTable"]
        add_fk_ops = [op for op in loaded_migration.operations if op.type == "AddForeignKey"]
        assert len(create_table_ops) == 2  # User和Post
        assert len(add_fk_ops) == 1  # Post -> User的外键
    
    def test_repeated_runs_with_complex_model(self, tmp_path):
        """测试复杂模型的重复运行不会产生错误的migration"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        parser = MermaidAntlrParser()
        
        # 使用file_upload_models.mmd的简化版本
        mmd_content = """erDiagram
    User ||--o{ UploadedFile : uploads
    FileType ||--o{ UploadedFile : categorizes
    UploadedFile ||--o{ UploadedFile : parent
    User {
        uuid id PK
        string username UK
    }
    FileType {
        uuid id PK
        string name UK
    }
    UploadedFile {
        uuid id PK
        uuid user_id FK
        uuid file_type_id FK
        uuid parent_file_id FK
        string filename
    }
"""
        
        # 第一次运行
        model1 = parser.parse(mmd_content)
        migration1 = generator.generate("files", model1)
        assert migration1 is not None
        fm.save_migration(migration1)
        
        initial_ops_count = len(migration1.operations)
        initial_fk_count = len([op for op in migration1.operations if op.type == "AddForeignKey"])
        
        # 第二次运行 - 应该没有变化
        model2 = parser.parse(mmd_content)
        migration2 = generator.generate("files", model2)
        assert migration2 is None, "相同模型不应该生成新migration"
        
        # 第三次运行 - 再次确认
        model3 = parser.parse(mmd_content)
        migration3 = generator.generate("files", model3)
        assert migration3 is None, "相同模型不应该生成新migration"
        
        # 验证只有一个migration文件
        files = fm.list_migration_files("files")
        assert len(files) == 1
        
        # 验证migration内容没有重复
        loaded = fm.load_migration("files", files[0])
        assert len(loaded.operations) == initial_ops_count
        
        # 验证外键数量没有增加
        loaded_fk_count = len([op for op in loaded.operations if op.type == "AddForeignKey"])
        assert loaded_fk_count == initial_fk_count, f"外键数量应该保持{initial_fk_count}，但是是{loaded_fk_count}"
    
    def test_alternating_versions_no_duplicate_operations(self, tmp_path):
        """测试在两个版本之间来回切换不会产生重复操作"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.models import ERModel, Entity, Column
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        
        # 版本A
        def create_version_a():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string")
                ]
            ))
            return model
        
        # 版本B（添加email）
        def create_version_b():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string"),
                    Column(name="email", type="string")
                ]
            ))
            return model
        
        # 生成版本A的migration
        model_a1 = create_version_a()
        migration_a1 = generator.generate("test", model_a1)
        assert migration_a1 is not None
        fm.save_migration(migration_a1)
        
        # 生成版本B的migration
        model_b1 = create_version_b()
        migration_b1 = generator.generate("test", model_b1)
        assert migration_b1 is not None
        fm.save_migration(migration_b1)
        
        # 再次运行版本B - 不应该生成新migration
        model_b2 = create_version_b()
        migration_b2 = generator.generate("test", model_b2)
        assert migration_b2 is None, "重复运行版本B不应该生成新migration"
        
        # 再次运行版本B第三次 - 仍然不应该生成新migration
        model_b3 = create_version_b()
        migration_b3 = generator.generate("test", model_b3)
        assert migration_b3 is None, "第三次运行版本B不应该生成新migration"
        
        # 验证migration文件数量
        files = fm.list_migration_files("test")
        assert len(files) == 2  # 0001_initial, 0002_add_email
        
        # 验证第二个migration是AddColumn
        second_migration = fm.load_migration("test", files[-1])
        add_ops = [op for op in second_migration.operations if op.type == "AddColumn"]
        assert len(add_ops) == 1
        assert add_ops[0].column.name == "email"

    def test_migrations_only_generated_when_model_changes(self, tmp_path):
        """核心测试：只有当model变化时才生成migration，model不变时不生成"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.models import ERModel, Entity, Column, Relationship
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        
        # ========== 场景1: 初始模型 ==========
        def create_v1():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string")
                ]
            ))
            return model
        
        # 第一次运行 - 应该生成migration
        m1 = generator.generate("test", create_v1())
        assert m1 is not None, "初始模型应该生成migration"
        fm.save_migration(m1)
        assert len(fm.list_migration_files("test")) == 1
        
        # 重复运行相同模型 - 不应该生成migration
        m2 = generator.generate("test", create_v1())
        assert m2 is None, "相同模型不应该生成migration"
        assert len(fm.list_migration_files("test")) == 1
        
        m3 = generator.generate("test", create_v1())
        assert m3 is None, "再次运行相同模型不应该生成migration"
        assert len(fm.list_migration_files("test")) == 1
        
        # ========== 场景2: 添加列 ==========
        def create_v2():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string"),
                    Column(name="email", type="string")  # 新增
                ]
            ))
            return model
        
        # 模型变化 - 应该生成migration
        m4 = generator.generate("test", create_v2())
        assert m4 is not None, "添加列应该生成migration"
        fm.save_migration(m4)
        assert len(fm.list_migration_files("test")) == 2
        
        # 重复运行 - 不应该生成migration
        m5 = generator.generate("test", create_v2())
        assert m5 is None, "相同模型不应该生成migration"
        assert len(fm.list_migration_files("test")) == 2
        
        # ========== 场景3: 删除列 ==========
        def create_v3():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string")
                    # email被删除
                ]
            ))
            return model
        
        # 模型变化 - 应该生成migration
        m6 = generator.generate("test", create_v3())
        assert m6 is not None, "删除列应该生成migration"
        fm.save_migration(m6)
        assert len(fm.list_migration_files("test")) == 3
        
        # 重复运行 - 不应该生成migration
        m7 = generator.generate("test", create_v3())
        assert m7 is None, "相同模型不应该生成migration"
        assert len(fm.list_migration_files("test")) == 3
        
        # ========== 场景4: 添加新表和关系 ==========
        def create_v4():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string")
                ]
            ))
            model.add_entity(Entity(
                name="Post",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="author_id", type="uuid", is_fk=True),
                    Column(name="title", type="string")
                ]
            ))
            model.add_relationship(Relationship(
                left_entity="Post",
                right_entity="User",
                relation_type="many-to-one",
                left_column="author_id",
                right_column="id"
            ))
            return model
        
        # 模型变化 - 应该生成migration
        m8 = generator.generate("test", create_v4())
        assert m8 is not None, "添加表和关系应该生成migration"
        fm.save_migration(m8)
        assert len(fm.list_migration_files("test")) == 4
        
        # 重复运行多次 - 都不应该生成migration
        for i in range(5):
            m = generator.generate("test", create_v4())
            assert m is None, f"第{i+1}次重复运行不应该生成migration"
            assert len(fm.list_migration_files("test")) == 4
        
        # ========== 场景5: 修改列属性 ==========
        def create_v5():
            model = ERModel()
            model.add_entity(Entity(
                name="User",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="username", type="string", max_length=100)  # 添加长度限制
                ]
            ))
            model.add_entity(Entity(
                name="Post",
                columns=[
                    Column(name="id", type="uuid", is_pk=True),
                    Column(name="author_id", type="uuid", is_fk=True),
                    Column(name="title", type="string")
                ]
            ))
            model.add_relationship(Relationship(
                left_entity="Post",
                right_entity="User",
                relation_type="many-to-one",
                left_column="author_id",
                right_column="id"
            ))
            return model
        
        # 模型变化 - 应该生成migration
        m9 = generator.generate("test", create_v5())
        assert m9 is not None, "修改列属性应该生成migration"
        fm.save_migration(m9)
        assert len(fm.list_migration_files("test")) == 5
        
        # 重复运行 - 不应该生成migration
        m10 = generator.generate("test", create_v5())
        assert m10 is None, "相同模型不应该生成migration"
        assert len(fm.list_migration_files("test")) == 5
        
        # ========== 最终验证 ==========
        # 验证所有migration文件
        files = fm.list_migration_files("test")
        assert len(files) == 5, "应该有5个migration文件"
        
        # 验证依赖链
        migrations = fm.load_namespace_migrations("test")
        assert migrations[0].dependencies == []
        assert migrations[1].dependencies == ["test.0001_initial"]
        assert migrations[2].dependencies == ["test.0002_add_email"]
        assert migrations[3].dependencies == ["test.0003_auto_migration"]
        assert migrations[4].dependencies == ["test.0004_create_post"]
        
        print("\n✅ 核心行为验证通过：")
        print("  - 模型变化时生成migration ✓")
        print("  - 模型不变时不生成migration ✓")
        print("  - 依赖链正确 ✓")

    
    def test_blog_evolution_8_versions(self, tmp_path):
        """测试博客系统的完整演进（8个版本）"""
        from x007007007.er_migrate.generator import MigrationGenerator
        from x007007007.er_migrate.file_manager import FileManager
        from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
        
        migrations_dir = tmp_path / ".migrations"
        generator = MigrationGenerator(str(migrations_dir))
        fm = FileManager(str(migrations_dir))
        parser = MermaidAntlrParser()
        
        # 定义8个版本的ER图
        versions = [
            # v1: 只有User表
            """
            erDiagram
                User {
                    uuid id PK
                    string username UK
                    datetime created_at
                }
            """,
            # v2: 添加email
            """
            erDiagram
                User {
                    uuid id PK
                    string username UK
                    string email UK
                    datetime created_at
                }
            """,
            # v3: 添加Post表
            """
            erDiagram
                User ||--o{ Post : writes
                
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
            """,
            # v4: 添加Comment表
            """
            erDiagram
                User ||--o{ Post : writes
                User ||--o{ Comment : writes
                Post ||--o{ Comment : has
                
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
                    datetime updated_at
                }
                
                Comment {
                    uuid id PK
                    uuid author_id FK
                    uuid post_id FK
                    text content
                    datetime created_at
                }
            """,
            # v5: 添加更多字段
            """
            erDiagram
                User ||--o{ Post : writes
                User ||--o{ Comment : writes
                Post ||--o{ Comment : has
                
                User {
                    uuid id PK
                    string username UK
                    string email UK
                    string bio
                    datetime created_at
                }
                
                Post {
                    uuid id PK
                    uuid author_id FK
                    string title
                    text content
                    string status
                    datetime created_at
                    datetime updated_at
                    datetime published_at
                }
                
                Comment {
                    uuid id PK
                    uuid author_id FK
                    uuid post_id FK
                    text content
                    datetime created_at
                }
            """,
            # v6: 评论匿名化（删除author_id外键）
            """
            erDiagram
                User ||--o{ Post : writes
                Post ||--o{ Comment : has
                
                User {
                    uuid id PK
                    string username UK
                    string email UK
                    string bio
                    datetime created_at
                }
                
                Post {
                    uuid id PK
                    uuid author_id FK
                    string title
                    text content
                    string status
                    datetime created_at
                    datetime updated_at
                    datetime published_at
                }
                
                Comment {
                    uuid id PK
                    uuid post_id FK
                    string author_name
                    text content
                    datetime created_at
                }
            """,
            # v7: 重命名Post为Article
            """
            erDiagram
                User ||--o{ Article : writes
                Article ||--o{ Comment : has
                
                User {
                    uuid id PK
                    string username UK
                    string email UK
                    string bio
                    datetime created_at
                }
                
                Article {
                    uuid id PK
                    uuid author_id FK
                    string title
                    text content
                    string status
                    datetime created_at
                    datetime updated_at
                    datetime published_at
                }
                
                Comment {
                    uuid id PK
                    uuid article_id FK
                    string author_name
                    text content
                    datetime created_at
                }
            """,
            # v8: 删除Comment表
            """
            erDiagram
                User ||--o{ Article : writes
                
                User {
                    uuid id PK
                    string username UK
                    string email UK
                    string bio
                    datetime created_at
                }
                
                Article {
                    uuid id PK
                    uuid author_id FK
                    string title
                    text content
                    string status
                    datetime created_at
                    datetime updated_at
                    datetime published_at
                }
            """
        ]
        
        # 按顺序生成所有版本的migration
        for i, er_content in enumerate(versions, 1):
            er_model = parser.parse(er_content)
            migration = generator.generate("blog", er_model)
            
            if i == 1:
                # 第一个版本应该生成migration
                assert migration is not None, f"版本{i}应该生成migration"
            else:
                # 后续版本可能生成也可能不生成（取决于是否有变化）
                pass
            
            if migration:
                fm.save_migration(migration)
        
        # 验证生成了多个migration文件
        files = fm.list_migration_files("blog")
        assert len(files) >= 5, f"应该生成至少5个migration，实际生成了{len(files)}个"
        
        # 重复运行最后一个版本，不应该生成新migration
        final_model = parser.parse(versions[-1])
        migration = generator.generate("blog", final_model)
        assert migration is None, "重复运行最后一个版本不应该生成新migration"
        
        # 验证migration数量没有增加
        files_after = fm.list_migration_files("blog")
        assert len(files_after) == len(files), "重复运行不应该增加migration数量"
