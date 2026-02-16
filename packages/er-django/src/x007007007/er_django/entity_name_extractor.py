"""Extract business entity names from Django model names using regex patterns."""

import re
from typing import Optional


class EntityNameExtractor:
    """Extract business entity names from Django model names using regex patterns.
    
    This class uses regular expressions to transform Django model class names
    into business entity names by removing common prefixes or suffixes.
    
    Examples:
        >>> extractor = EntityNameExtractor()  # Default: remove "Model" suffix
        >>> extractor.extract("AccountModel")
        'Account'
        
        >>> extractor = EntityNameExtractor(r"^Tbl(.+)$")  # Remove "Tbl" prefix
        >>> extractor.extract("TblUser")
        'User'
        
        >>> extractor = EntityNameExtractor(r"(.+)Entity$")  # Remove "Entity" suffix
        >>> extractor.extract("UserEntity")
        'User'
    """
    
    DEFAULT_PATTERN = r"(.+)Model$"  # Default: remove "Model" suffix
    
    def __init__(self, pattern: str = DEFAULT_PATTERN):
        """Initialize extractor with a regex pattern.
        
        Args:
            pattern: Regex pattern with one capture group for the business name.
                    The first capture group will be used as the extracted name.
                    
        Raises:
            ValueError: If pattern is invalid or has no capture groups.
            
        Examples:
            >>> EntityNameExtractor(r"(.+)Model$")  # Valid
            >>> EntityNameExtractor(r"^Tbl(.+)$")   # Valid
            >>> EntityNameExtractor(r"User")        # Invalid - no capture group
            Traceback (most recent call last):
                ...
            ValueError: Pattern 'User' must have at least one capture group...
        """
        try:
            self.compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        
        # Validate at least one capture group exists
        if self.compiled_pattern.groups < 1:
            raise ValueError(
                f"Pattern '{pattern}' must have at least one capture group. "
                f"Example: '(.+)Model$' or '^Tbl(.+)$'"
            )
        
        self.pattern = pattern
    
    def extract(self, model_name: str) -> str:
        """Extract business entity name from model name.
        
        Applies the regex pattern to the model name. If the pattern matches,
        returns the first capture group. If no match, returns the original name.
        
        Args:
            model_name: Django model class name (e.g., "AccountModel")
            
        Returns:
            Business entity name (e.g., "Account").
            If pattern doesn't match, returns original model_name.
            
        Examples:
            >>> extractor = EntityNameExtractor(r"(.+)Model$")
            >>> extractor.extract("AccountModel")
            'Account'
            >>> extractor.extract("User")  # No match - returns original
            'User'
        """
        match = self.compiled_pattern.match(model_name)
        if match:
            # Return the first capture group
            return match.group(1)
        else:
            # If no match, return original name
            return model_name
