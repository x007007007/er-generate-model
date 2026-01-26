# ER Migrations Examples

本目录包含了使用ER迁移系统的示例。

## 多版本Migration示例

### 场景：博客系统的演进

我们提供了8个版本的ER图，展示了博客系统从简单到复杂，再到重构的完整演进过程：

#### 版本1 (blog_v1.mmd) - 初始版本
只有User表：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v1.mmd
```

**变更**：
- 创建User表（id, username, created_at）

---

#### 版本2 (blog_v2.mmd) - 添加邮箱
添加email字段：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v2.mmd
```

**变更**：
- User表添加email列（带唯一索引）

---

#### 版本3 (blog_v3.mmd) - 添加文章功能
添加Post表和关系：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v3.mmd
```

**变更**：
- 创建Post表（id, author_id, title, content, created_at）
- 添加User到Post的一对多关系（外键）

---

#### 版本4 (blog_v4.mmd) - 添加评论功能
添加Comment表和更多字段：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v4.mmd
```

**变更**：
- 创建Comment表（id, author_id, post_id, content, created_at）
- Post表添加updated_at列
- 添加User到Comment的一对多关系
- 添加Post到Comment的一对多关系

---

#### 版本5 (blog_v5.mmd) - 增强功能
添加更多业务字段：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v5.mmd
```

**变更**：
- User表添加bio列
- Post表添加status列（草稿/已发布）
- Post表添加published_at列

---

#### 版本6 (blog_v6.mmd) - 评论匿名化
允许匿名评论：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v6.mmd
```

**变更**：
- Comment表删除author_id外键（允许匿名）
- Comment表添加author_name列（存储匿名用户名）
- 删除User到Comment的关系

---

#### 版本7 (blog_v7.mmd) - 重命名Post为Article
重构表名：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v7.mmd
```

**变更**：
- Post表重命名为Article
- Comment表的post_id重命名为article_id
- 更新所有相关的外键关系

---

#### 版本8 (blog_v8.mmd) - 删除评论功能
简化系统：
```bash
uv run er-migrate makemigrations -n blog -e examples/blog_v8.mmd
```

**变更**：
- 删除Comment表
- 只保留User和Article表

---

### 完整演进流程

```bash
# 按顺序执行所有版本
uv run er-migrate makemigrations -n blog -e examples/blog_v1.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v2.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v3.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v4.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v5.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v6.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v7.mmd
uv run er-migrate makemigrations -n blog -e examples/blog_v8.mmd

# 查看所有迁移
uv run er-migrate showmigrations -n blog
```

预期输出：
```
blog:
  [X] 0001_initial
  [X] 0002_auto_migration
  [X] 0003_create_post
  [X] 0004_create_comment
  [X] 0005_auto_migration
  [X] 0006_auto_migration
  [X] 0007_rename_post_to_article
  [X] 0008_drop_comment
```

### 演进总结

| 版本 | 主要变更 | 操作类型 |
|------|---------|---------|
| v1 | 创建User表 | CreateTable |
| v2 | 添加email列 | AddColumn, AddIndex |
| v3 | 创建Post表 | CreateTable, AddForeignKey |
| v4 | 创建Comment表 | CreateTable, AddColumn, AddForeignKey |
| v5 | 添加业务字段 | AddColumn |
| v6 | 评论匿名化 | RemoveForeignKey, AddColumn, RemoveColumn |
| v7 | 重命名表 | RenameTable, AlterColumn |
| v8 | 删除评论功能 | DropTable |

## 完整示例：文件上传系统

`file_upload_models.mmd` 包含了一个完整的文件上传和处理系统的ER图，展示了：
- 多个实体之间的关系
- 一对一、一对多关系
- 自引用关系（parent_file_id）
- 外键约束

生成migration：
```bash
uv run er-migrate makemigrations -n file_system -e examples/file_upload_models.mmd
```

## 数据类型完整示例

`all_data_types.mmd` 展示了系统支持的所有数据类型：

### 字符串类型
- `string` / `varchar` - 可变长度字符串
- `char` - 固定长度字符串
- `text` - 大文本内容

### 数值类型
- `int` / `integer` - 标准整数
- `bigint` - 64位大整数
- `smallint` - 16位小整数
- `tinyint` - 8位微整数
- `float` / `real` - 单精度浮点数
- `double` - 双精度浮点数
- `decimal` / `numeric` - 固定精度小数

### 布尔类型
- `boolean` / `bool` - 真/假值

### 日期时间类型
- `date` - 日期（年月日）
- `time` - 时间（时分秒）
- `datetime` - 日期时间
- `timestamp` - Unix时间戳

### 特殊类型
- `uuid` - 通用唯一标识符
- `json` / `jsonb` - JSON对象

生成migration：
```bash
uv run er-migrate makemigrations -n showcase -e examples/all_data_types.mmd
```

### Blog示例中的数据类型覆盖

8个版本的blog示例逐步引入了不同的数据类型：

| 版本 | 新增数据类型 |
|------|-------------|
| v1 | uuid, string, datetime |
| v2 | （无新增） |
| v3 | int, boolean, text |
| v4 | float, smallint |
| v5 | date, time, decimal, json |
| v6 | （无新增） |
| v7 | bigint, varchar, char, double |
| v8 | timestamp, real, numeric |

通过这8个版本，覆盖了**所有主要数据类型**。

## 工作流程

1. **创建初始ER图** - 定义你的数据模型
2. **生成初始migration** - `er-migrate makemigrations -n <namespace> -e <er_file>`
3. **修改ER图** - 添加/修改/删除表或列
4. **生成新migration** - 再次运行makemigrations命令
5. **查看migration历史** - `er-migrate showmigrations -n <namespace>`

## 注意事项

- 每次运行makemigrations时，系统会：
  1. 从已有的migration重建当前状态
  2. 与新的ER图进行对比
  3. 生成差异操作
  4. 如果没有变化，不会生成新的migration

- Migration文件按顺序编号（0001, 0002, 0003...）
- 每个migration都记录了它依赖的前一个migration
- YAML文件的字段顺序是固定的，便于版本控制
- 重复运行相同的ER图不会产生新的migration

## 测试场景覆盖

这些示例覆盖了以下测试场景：

### 表操作
- ✅ CreateTable - v1, v3, v4
- ✅ DropTable - v8
- ✅ RenameTable - v7

### 列操作
- ✅ AddColumn - v2, v4, v5, v6
- ✅ RemoveColumn - v6
- ✅ AlterColumn - v5（修改列属性）

### 关系操作
- ✅ AddForeignKey - v3, v4
- ✅ RemoveForeignKey - v6

### 复杂场景
- ✅ 添加表和关系 - v3, v4
- ✅ 删除关系但保留表 - v6
- ✅ 重命名表并更新关系 - v7
- ✅ 删除有关系的表 - v8
- ✅ 重复运行不产生新migration - 所有版本
