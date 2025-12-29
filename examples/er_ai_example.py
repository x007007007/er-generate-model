"""
ER AI 使用示例。

这个示例展示了如何使用 ER AI SDK 生成 TOML 格式的 ER 配置。
"""
import os
from x007007007.er_ai import generate_er_model, ERModeler

def example_basic_usage():
    """基本使用示例。"""
    print("=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)
    
    # 注意：需要设置 DEEPSEEK_API_KEY 环境变量
    # 或者在代码中直接传递 api_key 参数
    
    requirement = """
    设计一个简单的博客系统，包含：
    - 用户实体：用户名、邮箱、密码
    - 文章实体：标题、内容、发布时间
    - 用户和文章是一对多关系
    """
    
    try:
        # 使用 SDK 接口
        toml_config = generate_er_model(
            requirement,
            api_key=os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取
        )
        
        print("\n生成的 TOML 配置：")
        print(toml_config)
        
        # 保存到文件
        with open("blog_er.toml", "w", encoding="utf-8") as f:
            f.write(toml_config)
        print("\n配置已保存到 blog_er.toml")
        
    except ValueError as e:
        print(f"错误: {e}")
        print("提示: 请设置 DEEPSEEK_API_KEY 环境变量")


def example_advanced_usage():
    """高级使用示例。"""
    print("\n" + "=" * 60)
    print("示例 2: 高级使用")
    print("=" * 60)
    
    requirement = """
    设计一个电商系统，包含：
    - 用户：用户名、邮箱、手机号、注册时间
    - 商品：名称、价格、库存、描述
    - 订单：订单号、总金额、下单时间、状态
    - 订单项：商品ID、数量、单价
    - 关系：用户和订单是一对多，订单和订单项是一对多，商品和订单项是一对多
    """
    
    try:
        # 使用 ERModeler 类进行更精细的控制
        modeler = ERModeler(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"  # 可选，默认就是这个
        )
        
        toml_config = modeler.generate_toml(requirement)
        
        print("\n生成的 TOML 配置：")
        print(toml_config)
        
        # 验证生成的配置
        from x007007007.er.parser.toml_parser import TomlERParser
        parser = TomlERParser()
        model = parser.parse(toml_config)
        
        print(f"\n验证结果：")
        print(f"- 实体数量: {len(model.entities)}")
        print(f"- 关系数量: {len(model.relationships)}")
        print(f"- 模板数量: {len(model.templates)}")
        
        # 列出所有实体
        print("\n实体列表：")
        for entity_name in model.entities:
            entity = model.entities[entity_name]
            print(f"  - {entity_name}: {len(entity.columns)} 个字段")
        
    except ValueError as e:
        print(f"错误: {e}")
        print("提示: 请设置 DEEPSEEK_API_KEY 环境变量")


def example_integration_with_code_generation():
    """与代码生成集成的示例。"""
    print("\n" + "=" * 60)
    print("示例 3: 与代码生成集成")
    print("=" * 60)
    
    requirement = "设计一个内容管理系统，包含用户、文章、分类、评论等实体"
    
    try:
        # 1. 生成 TOML 配置
        toml_config = generate_er_model(
            requirement,
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        
        # 2. 保存 TOML 配置
        with open("cms_er.toml", "w", encoding="utf-8") as f:
            f.write(toml_config)
        print("✓ TOML 配置已生成: cms_er.toml")
        
        # 3. 生成 Django 代码
        from x007007007.er.parser.toml_parser import TomlERParser
        from x007007007.er.renderers import DjangoRenderer
        
        parser = TomlERParser()
        model = parser.parse(toml_config)
        
        renderer = DjangoRenderer(app_label="cms")
        django_code = renderer.render(model)
        
        with open("cms_models.py", "w", encoding="utf-8") as f:
            f.write(django_code)
        print("✓ Django 模型代码已生成: cms_models.py")
        
        # 4. 生成 SQLAlchemy 代码
        from x007007007.er.renderers import SQLAlchemyRenderer
        
        renderer = SQLAlchemyRenderer()
        sqlalchemy_code = renderer.render(model)
        
        with open("cms_sqlalchemy.py", "w", encoding="utf-8") as f:
            f.write(sqlalchemy_code)
        print("✓ SQLAlchemy 模型代码已生成: cms_sqlalchemy.py")
        
        print("\n完整的工作流程：")
        print("  需求描述 → AI 生成 TOML → 生成代码")
        
    except ValueError as e:
        print(f"错误: {e}")
        print("提示: 请设置 DEEPSEEK_API_KEY 环境变量")


if __name__ == "__main__":
    print("\nER AI 使用示例\n")
    print("注意: 运行这些示例需要设置 DEEPSEEK_API_KEY 环境变量\n")
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  警告: 未设置 DEEPSEEK_API_KEY 环境变量")
        print("   示例将无法正常运行，但可以查看代码了解使用方法\n")
    
    # 运行示例（如果设置了 API 密钥）
    if os.getenv("DEEPSEEK_API_KEY"):
        example_basic_usage()
        # example_advanced_usage()  # 取消注释以运行
        # example_integration_with_code_generation()  # 取消注释以运行
    else:
        print("请设置 DEEPSEEK_API_KEY 环境变量后重新运行示例")
        print("\n示例代码已展示，可以参考代码了解使用方法")

