"""Tests for Python renderer utilities."""
import pytest
from x007007007.er.renderers.python.utils import to_snake_case


class TestToSnakeCase:
    """Tests for to_snake_case helper function - Task 14.1."""
    
    def test_simple_camel_case(self):
        """Test simple CamelCase conversion."""
        assert to_snake_case("User") == "user"
        assert to_snake_case("Post") == "post"
    
    def test_multi_word_camel_case(self):
        """Test multi-word CamelCase conversion."""
        assert to_snake_case("UserProfile") == "user_profile"
        assert to_snake_case("BlogPost") == "blog_post"
        assert to_snake_case("UserAccount") == "user_account"
    
    def test_complex_camel_case(self):
        """Test complex CamelCase conversion."""
        assert to_snake_case("ConversationSessionModel") == "conversation_session_model"
        assert to_snake_case("FileTypeModel") == "file_type_model"
    
    def test_acronyms(self):
        """Test handling of acronyms - Requirement 5.2."""
        assert to_snake_case("HTTPResponse") == "http_response"
        assert to_snake_case("HTTPRequest") == "http_request"
        assert to_snake_case("XMLParser") == "xml_parser"
        assert to_snake_case("APIClient") == "api_client"
    
    def test_already_snake_case(self):
        """Test strings already in snake_case."""
        assert to_snake_case("user_profile") == "user_profile"
        assert to_snake_case("blog_post") == "blog_post"
    
    def test_single_letter(self):
        """Test single letter names."""
        assert to_snake_case("A") == "a"
        assert to_snake_case("X") == "x"
    
    def test_with_numbers(self):
        """Test names with numbers - Requirement 5.2."""
        assert to_snake_case("User2") == "user2"
        assert to_snake_case("Model3D") == "model3_d"
        assert to_snake_case("Version2API") == "version2_api"
    
    def test_special_characters_in_name(self):
        """Test that special characters are handled (though not typical in class names)."""
        # These are edge cases - typically class names don't have special chars
        # The function preserves existing underscores
        assert to_snake_case("User_Profile") == "user__profile"  # Underscore is preserved
        assert to_snake_case("User__Profile") == "user___profile"  # Double underscore preserved
    
    def test_consecutive_uppercase(self):
        """Test consecutive uppercase letters."""
        assert to_snake_case("HTTPSConnection") == "https_connection"
        assert to_snake_case("XMLHTTPRequest") == "xmlhttp_request"
    
    def test_empty_string(self):
        """Test empty string."""
        assert to_snake_case("") == ""
    
    def test_lowercase_only(self):
        """Test lowercase only strings."""
        assert to_snake_case("user") == "user"
        assert to_snake_case("post") == "post"
