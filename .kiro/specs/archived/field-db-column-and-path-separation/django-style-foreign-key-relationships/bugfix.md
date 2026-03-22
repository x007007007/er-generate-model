# Bug修复需求文档

## 简介

SQLAlchemy生成器在从TOML规范生成模型时会产生错误的代码，特别是在处理以下场景时：包含指向同一实体的多个外键、外键同时也是主键的一对一关系、外部实体引用、错误的类继承、以及主键属性命名。这些问题导致生成的SQLAlchemy模型无法正常工作并引发运行时错误。Bug表现为六种不同的场景：重复的关系名称、一对一关系中错误的主键列命名、外部引用缺失ForeignKey约束、外部外键字段的错误类型、SQLAlchemy模型错误地继承Django模型类、以及主键Python属性名使用数据库列名而非安全的属性名。

## Bug分析

### 当前行为（缺陷）

1.1 当一个实体有多个外键指向同一个目标实体时（例如，SellItem通过SellItemBundleItem有两个指向自身的外键：`bundle_sell_item_id`和`component_sell_item_id`），生成器会创建重复的关系名称（例如，`sellitembundleitem_set`出现两次），而不是基于外键列的唯一名称

1.2 当存在外键同时也是主键的一对一关系时（例如，Voucher.entitlement_id同时作为外键和主键引用Entitlement.id），生成器错误地将Entitlement的主键列命名为`id_id`而不是保持为`id`，并且错误地添加了ForeignKey约束

1.3 当列引用TOML中未定义的外部实体时（例如，Order.visitor引用`kkt_rfc_login_visitor.id`），生成器会创建列但省略`ForeignKey()`约束

1.4 当列引用外部实体时，生成器使用错误的字段类型（例如，ID字段使用`String(255)`而不是`BigInteger`）

1.5 当TOML中的extends字段包含Django模型类路径时（例如，`kinkotech.common.infrastructure.models.base.KinkoTechModelBase`），生成器会在SQLAlchemy模型中直接导入并继承这些Django类，导致SQLAlchemy模型错误地继承Django ORM的类

1.6 当主键列名为`id`或其他名称时，生成器直接使用数据库列名作为Python属性名（例如，`id = Column(...)`），这可能与Python内置函数`id()`冲突，且不够清晰表达这是主键

### 期望行为（正确）

2.1 当一个实体有多个外键指向同一个目标实体时，生成器应该基于外键列名创建唯一的关系名称（例如，`bundle_items`和`component_items`而不是重复的`sellitembundleitem_set`）

2.2 当存在外键同时也是主键的一对一关系时，生成器应该正确识别这是反向关系，不在"one"侧（Entitlement）创建外键列，只创建relationship定义

2.3 当列引用TOML中未定义的外部实体时，生成器应该包含带有正确外部表引用的`ForeignKey()`约束（例如，`Column(BigInteger, ForeignKey('kkt_rfc_login_visitor.id'))`）

2.4 当列引用外部实体时，生成器应该使用与被引用列类型匹配的正确字段类型（例如，ID字段使用`BigInteger`）

2.5 当TOML中的extends字段包含Django模型类路径时，生成器应该忽略这些Django特定的类，只继承SQLAlchemy的Base类（或者如果有SQLAlchemy版本的mixin类，则继承那些类）

2.6 当主键列名为`id`时，生成器应该使用`pk`作为Python属性名，同时在Column定义中指定数据库列名为`id`（例如，`pk = Column('id', BigInteger, primary_key=True)`），以避免与Python内置函数`id()`的潜在冲突并更清晰地表达这是主键

### 不变行为（回归预防）

3.1 当实体有单个外键指向另一个实体时，生成器应该继续使用Django风格的`_set`后缀创建正确的关系名称

3.2 当外键不同时是主键时，生成器应该继续通过在逻辑字段名后附加`_id`来正确命名列

3.3 当列引用同一TOML文件中定义的实体时，生成器应该继续创建带有正确表引用的`ForeignKey()`约束

3.4 当生成没有外键关系的列时，生成器应该继续基于TOML类型规范使用正确的字段类型

3.5 当生成关系的back_populates时，生成器应该继续使用TOML中的正确逻辑字段名

3.6 当生成带有继承（extends字段）的模型时，如果extends中包含的是SQLAlchemy兼容的类，生成器应该继续在类定义中正确包含这些父类引用

3.7 当TOML中的extends字段为空或只包含内部模板时，生成器应该继续正确处理继承关系

3.8 当主键列名不是`id`时（例如，`user_id`、`order_id`等），生成器应该继续使用原始列名作为Python属性名
