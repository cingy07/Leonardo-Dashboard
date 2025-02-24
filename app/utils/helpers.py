"""
General helper functions used throughout the application.
These utilities provide common functionality needed by multiple components.
"""

import uuid
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

def generate_request_id() -> str:
    """
    Generate a unique request identifier.
    
    Returns:
        Unique request ID string
        
    Example:
        >>> generate_request_id()
        'req_1234567890abcdef'
    """
    return f"req_{uuid.uuid4().hex[:16]}"

def parse_committee_data(file_path: Path) -> Dict[str, List[str]]:
    """
    Parse committee membership data from JSON file.
    
    Args:
        file_path: Path to committee data file
        
    Returns:
        Dictionary mapping committees to member lists
        
    Example:
        >>> parse_committee_data(Path('committees.json'))
        {'Committee1': ['Member1', 'Member2'], ...}
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Invalid committee data format")
            
        # Ensure all values are lists
        return {
            committee: (
                members if isinstance(members, list)
                else [members] if members
                else []
            )
            for committee, members in data.items()
        }
        
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in committee data file")
    except Exception as e:
        raise ValueError(f"Error reading committee data: {str(e)}")

def merge_representative_data(
    civic_data: Dict[str, Any],
    committee_data: List[str]
) -> Dict[str, Any]:
    """
    Merge data from different sources into a single representative record.
    
    Args:
        civic_data: Data from Google Civic API
        committee_data: List of committee assignments
        
    Returns:
        Combined representative data
        
    Example:
        >>> merge_representative_data(
        ...     {"name": "John Doe", "party": "Democratic"},
        ...     ["Committee1", "Committee2"]
        ... )
        {
            "name": "John Doe",
            "party": "Democratic",
            "committees": ["Committee1", "Committee2"]
        }
    """
    return {
        "name": civic_data.get("name"),
        "party": format_party_name(civic_data.get("party", "")),
        "district": civic_data.get("district"),
        "state": civic_data.get("state"),
        "committees": committee_data,
        "photo_url": civic_data.get("photo_url"),
        "contact": {
            "phone": civic_data.get("phones", [None])[0],
            "email": civic_data.get("emails", [None])[0],
            "website": civic_data.get("urls", [None])[0]
        },
        "social_media": {
            channel["type"]: channel["id"]
            for channel in civic_data.get("channels", [])
        },
        "last_updated": format_date(datetime.utcnow())
    }