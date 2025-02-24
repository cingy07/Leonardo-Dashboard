"""
Functions for formatting and standardizing data presentation.
These utilities ensure consistent data formatting across the application.
"""

import re
from datetime import datetime
from typing import Optional

def format_district_number(district: str) -> str:
    """
    Format congressional district numbers consistently.
    Converts various district number formats to a standardized form.
    
    Args:
        district: District number in any format (e.g., '1', '01', 'District 1')
        
    Returns:
        Formatted district number (e.g., '01')
        
    Examples:
        >>> format_district_number('1')
        '01'
        >>> format_district_number('District 12')
        '12'
    """
    # Extract digits from district string
    digits = re.findall(r'\d+', str(district))
    if not digits:
        raise ValueError("Invalid district format")
        
    # Pad single digit districts with leading zero
    number = int(digits[0])
    return f"{number:02d}"

def format_party_name(party: str) -> str:
    """
    Standardize political party names.
    
    Args:
        party: Party name in any format
        
    Returns:
        Standardized party name
        
    Examples:
        >>> format_party_name('D')
        'Democratic'
        >>> format_party_name('Republican Party')
        'Republican'
    """
    party = party.lower().strip()
    
    party_mappings = {
        'd': 'Democratic',
        'dem': 'Democratic',
        'democratic': 'Democratic',
        'r': 'Republican',
        'rep': 'Republican',
        'republican': 'Republican',
        'i': 'Independent',
        'ind': 'Independent',
        'independent': 'Independent'
    }
    
    return party_mappings.get(party, party.title())

def format_date(date: Optional[datetime] = None, format_str: str = "%Y-%m-%d") -> str:
    """
    Format dates consistently throughout the application.
    
    Args:
        date: datetime object to format (defaults to current time)
        format_str: desired output format
        
    Returns:
        Formatted date string
        
    Examples:
        >>> format_date(datetime(2024, 2, 1))
        '2024-02-01'
    """
    if date is None:
        date = datetime.utcnow()
    return date.strftime(format_str)
