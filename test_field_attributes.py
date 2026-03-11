"""测试 Django 到 SQLAlchemy 转换中字段属性的保留情况"""
import django
from django.conf import settings

# 配置 Django
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
    USE_TZ=True,
)
django.setup()

from django.db import models
from x007007007.er_django.parser import DjangoModelParser
from x007007007.er.renderers.python.sqlalchemy.renderer import SQLAlchemyRenderer


class TestModel(models.Model):
    """测试模型，包含各种字段属性"""
    
    # 基本字段
    name = models.CharField(max_length=100, null=False, default='test')
    
    # 可空字段
    description = models.TextField(null=True, blank=True)
    
    # 带默认值的字段
    status = models.IntegerField(default=1)
    
    # 唯一字段
    email = models.EmailField(unique=True, max_length=255)
    
    # 带索引的字段
    code = models.CharField(max_length=50, db_index=True)
    
    # 带注释的字段
    created_at = models.DateTimeField(auto_now_add=True, help_text='创建时间')
    
    class Meta:
        app_label = 'test_app'


# 解析 Django 模型
parser = DjangoModelParser()
er_model = parser.parse([TestModel])

# 检查解析结果
entity = er_model.entities['TestModel']
print("=== 解析后的字段属性 ===")
for col in entity.columns:
    print(f"\n字段: {col.name}")
    print(f"  类型: {col.type}")
    print(f"  nullable: {col.nullable}")
    print(f"  default: {col.default}")
    print(f"  unique: {col.unique}")
    print(f"  indexed: {col.indexed}")
    print(f"  comment: {col.comment}")
    print(f"  max_length: {col.max_length}")

# 渲染为 SQLAlchemy
renderer = SQLAlchemyRenderer()
sqlalchemy_code = renderer.render(er_model)

print("\n\n=== 生成的 SQLAlchemy 代码 ===")
print(sqlalchemy_code)
