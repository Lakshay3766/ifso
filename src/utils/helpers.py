#!/usr/bin/env python3
"""
Utility Helper Functions
Common utility functions for data processing
"""

from datetime import datetime
from typing import Tuple, Optional


def parse_lat_long(lat_long_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse latitude/longitude string
    
    Args:
        lat_long_str: String in format "lat/long"
        
    Returns:
        Tuple of (latitude, longitude) or (None, None)
    """
    if lat_long_str and lat_long_str != '---':
        try:
            lat, long = lat_long_str.split('/')
            return float(lat), float(long)
        except (ValueError, AttributeError):
            return None, None
    return None, None


def format_datetime(dt: datetime) -> Tuple[str, str]:
    """
    Format datetime into date and time strings
    
    Args:
        dt: datetime object
        
    Returns:
        Tuple of (date_string, time_string)
    """
    if dt:
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    return "", ""


def parse_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Parse date and time strings into datetime object
    
    Args:
        date_str: Date string in DD/MM/YYYY format
        time_str: Time string in HH:MM:SS format
        
    Returns:
        datetime object or None
    """
    if date_str and time_str:
        try:
            date_str = date_str.strip("'")
            return datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
        except (ValueError, AttributeError):
            return None
    return None


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    if seconds is None:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate string to max length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if text and len(text) > max_length:
        return text[:max_length-3] + "..."
    return text or ""
