"""
Tests for column comments in Mermaid ER diagrams
"""
import pytest
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser


def test_column_comment_english():
    """Test parsing column with English comment"""
    content = '''erDiagram
    User {
        string username "User name"
        int age "User age"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 2
    
    username_col = user.columns[0]
    assert username_col.name == 'username'
    assert username_col.type == 'string'
    assert username_col.comment == 'User name'
    
    age_col = user.columns[1]
    assert age_col.name == 'age'
    assert age_col.type == 'int'
    assert age_col.comment == 'User age'


def test_column_comment_chinese():
    """Test parsing column with Chinese comment"""
    content = '''erDiagram
    User {
        string username "用户名"
        int age "年龄"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 2
    
    username_col = user.columns[0]
    assert username_col.name == 'username'
    assert username_col.comment == '用户名'
    
    age_col = user.columns[1]
    assert age_col.name == 'age'
    assert age_col.comment == '年龄'


def test_column_comment_with_pk_modifier():
    """Test parsing column with PK modifier and comment"""
    content = '''erDiagram
    User {
        uuid id PK "主键-唯一标识符"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 1
    
    id_col = user.columns[0]
    assert id_col.name == 'id'
    assert id_col.type == 'uuid'
    assert id_col.is_pk is True
    assert id_col.comment == '主键-唯一标识符'


def test_column_comment_with_uk_modifier():
    """Test parsing column with UK modifier and comment"""
    content = '''erDiagram
    User {
        string username UK "用户名-唯一"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 1
    
    username_col = user.columns[0]
    assert username_col.name == 'username'
    assert username_col.type == 'string'
    assert username_col.unique is True
    assert username_col.comment == '用户名-唯一'


def test_column_comment_with_fk_modifier():
    """Test parsing column with FK modifier and comment"""
    content = '''erDiagram
    Post {
        uuid author_id FK "作者ID-外键"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'Post' in model.entities
    post = model.entities['Post']
    assert len(post.columns) == 1
    
    author_id_col = post.columns[0]
    assert author_id_col.name == 'author_id'
    assert author_id_col.type == 'uuid'
    assert author_id_col.is_fk is True
    assert author_id_col.comment == '作者ID-外键'


def test_column_comment_with_multiple_modifiers():
    """Test parsing column with multiple modifiers and comment"""
    content = '''erDiagram
    User {
        uuid id PK UK "主键-唯一"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 1
    
    id_col = user.columns[0]
    assert id_col.name == 'id'
    assert id_col.type == 'uuid'
    assert id_col.is_pk is True
    assert id_col.unique is True
    assert id_col.comment == '主键-唯一'


def test_column_mixed_with_and_without_comments():
    """Test parsing columns with and without comments"""
    content = '''erDiagram
    User {
        uuid id PK "主键"
        string username
        int age "年龄"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 3
    
    assert user.columns[0].comment == '主键'
    assert user.columns[1].comment is None
    assert user.columns[2].comment == '年龄'


def test_column_comment_with_special_characters():
    """Test parsing column comment with special characters"""
    content = '''erDiagram
    User {
        string email "邮箱地址-格式:user@example.com"
        decimal price "价格(元)-范围:0.00-9999.99"
    }
    '''
    parser = MermaidAntlrParser()
    model = parser.parse(content)
    
    assert 'User' in model.entities
    user = model.entities['User']
    assert len(user.columns) == 2
    
    email_col = user.columns[0]
    assert email_col.comment == '邮箱地址-格式:user@example.com'
    
    price_col = user.columns[1]
    assert price_col.comment == '价格(元)-范围:0.00-9999.99'
