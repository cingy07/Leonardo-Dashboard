# utils/validation.py
"""
Data validation utilities.
These functions validate input data before processing.
"""

import re
from typing import Optional, Tuple
from app.core.exceptions import ValidationError

def validate_zip_code(zip_code: str) -> bool:
    """
    Validate US ZIP code format.
    
    Args:
        zip_code: ZIP code to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_zip_code('12345')
        True
        >>> validate_zip_code('1234')
        False
    """
    return bool(re.match(r'^\d{5}$', zip_code))

def validate_state_code(state: str) -> bool:
    """
    Validate US state code format.
    
    Args:
        state: Two-letter state code
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_state_code('CA')
        True
        >>> validate_state_code('CAL')
        False
    """
    state_codes = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC'  # Include DC for District of Columbia
    }
    return state.upper() in state_codes

def validate_district_format(district: str) -> Tuple[str, str]:
    """
    Validate and parse congressional district format.
    
    Args:
        district: District in format 'STATE-NN'
        
    Returns:
        Tuple of (state_code, district_number)
        
    Raises:
        ValidationError: If format is invalid
        
    Examples:
        >>> validate_district_format('CA-12')
        ('CA', '12')
    """
    match = re.match(r'^([A-Z]{2})-(\d{1,2})$', district.upper())
    if not match:
        raise ValidationError("Invalid district format")
        
    state, number = match.groups()
    if not validate_state_code(state):
        raise ValidationError("Invalid state code")
        
    return state, format_district_number(number)
