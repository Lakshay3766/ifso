#!/usr/bin/env python3
"""
Validator Functions
Functions to validate phone numbers, IMEI, etc.
"""

import re
from typing import Tuple


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not phone:
        return False, "Phone number is empty"
    
    # Remove spaces and special characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check length (Indian phone numbers are 10 digits, with country code 12-13)
    if len(cleaned) < 10 or len(cleaned) > 13:
        return False, "Invalid phone number length"
    
    return True, "Valid phone number"


def validate_imei(imei: str) -> Tuple[bool, str]:
    """
    Validate IMEI number
    
    Args:
        imei: IMEI number string
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not imei:
        return False, "IMEI is empty"
    
    # Remove spaces and special characters
    cleaned = re.sub(r'[^\d]', '', imei)
    
    # IMEI should be 15 digits
    if len(cleaned) != 15:
        return False, "IMEI must be 15 digits"
    
    # Basic Luhn algorithm check (optional)
    try:
        digits = [int(d) for d in cleaned]
        checksum = 0
        for i, digit in enumerate(digits[:-1]):
            if i % 2 == 0:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        
        calculated_check = (10 - (checksum % 10)) % 10
        if calculated_check != digits[-1]:
            return False, "Invalid IMEI checksum"
    except:
        return False, "Invalid IMEI format"
    
    return True, "Valid IMEI"


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_str: Date string
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not date_str:
        return False, "Date is empty"
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False, "Date format should be YYYY-MM-DD"
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, "Valid date"
    except ValueError:
        return False, "Invalid date"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent SQL injection
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()
