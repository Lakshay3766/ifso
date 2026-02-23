#!/usr/bin/env python3
"""
Authentication Manager Module
Handles user registration and login
"""

import sqlite3
import os
import hashlib
import binascii
from typing import Tuple, Optional
from datetime import datetime


class AuthManager:
    """Manages user authentication"""
    
    def __init__(self, base_db_path: str = 'data'):
        """
        Initialize auth manager
        
        Args:
            base_db_path: Base directory for database files
        """
        self.base_db_path = base_db_path
        if not os.path.exists(base_db_path):
            os.makedirs(base_db_path)
        
        self.users_db = os.path.join(base_db_path, 'users.db')
        self.create_users_table()
    
    def create_users_table(self):
        """Create users table if it doesn't exist"""
        conn = None
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            ''')
            
            conn.commit()
        except Exception as e:
            raise Exception(f"Error creating users table: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password with salt
        
        Args:
            password: Plain text password
            salt: Optional salt (hex string). If None, generates new salt.
            
        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = binascii.hexlify(os.urandom(16)).decode('utf-8')
            
        # Use PBKDF2 with SHA256
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        )
        return binascii.hexlify(pwd_hash).decode('utf-8'), salt
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message)
        """
        if not username or not password:
            return False, "Username and password are required"
            
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
            
        conn = None
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False, "Username already exists"
            
            # Hash password
            pwd_hash, salt = self._hash_password(password)
            
            # Insert user
            cursor.execute('''
            INSERT INTO users (username, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?)
            ''', (username, pwd_hash, salt, datetime.now()))
            
            conn.commit()
            return True, "Registration successful"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Login a user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message)
        """
        if not username or not password:
            return False, "Username and password are required"
            
        conn = None
        try:
            conn = sqlite3.connect(self.users_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT password_hash, salt FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Invalid username or password"
            
            stored_hash, salt = row
            
            # Verify password
            input_hash, _ = self._hash_password(password, salt)
            
            if input_hash == stored_hash:
                # Update last login
                cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', 
                             (datetime.now(), username))
                conn.commit()
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
                
        except Exception as e:
            return False, f"Login failed: {str(e)}"
        finally:
            if conn:
                conn.close()
