#!/usr/bin/env python3
"""
Case Manager Module
Handles case creation, selection, and management
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional


class CaseManager:
    """Manages investigation cases"""
    
    def __init__(self, base_db_path: str = 'data'):
        """
        Initialize case manager
        
        Args:
            base_db_path: Base directory for database files
        """
        self.base_db_path = base_db_path
        if not os.path.exists(base_db_path):
            os.makedirs(base_db_path)
        
        self.cases_db = os.path.join(base_db_path, 'cases.db')
        self.create_cases_table()
    
    def create_cases_table(self):
        """Create cases table if it doesn't exist"""
        conn = None
        try:
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_name TEXT NOT NULL UNIQUE,
                case_number TEXT,
                description TEXT,
                investigating_officer TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                db_path TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                user_id TEXT
            )
            ''')
            
            # Check if user_id column exists (for migration)
            cursor.execute("PRAGMA table_info(cases)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute("ALTER TABLE cases ADD COLUMN user_id TEXT")
            
            conn.commit()
        except Exception as e:
            raise Exception(f"Error creating cases table: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def create_case(self, case_name: str, case_number: str = "", 
                   description: str = "", investigating_officer: str = "", 
                   user_id: str = None) -> Tuple[bool, str]:
        """
        Create a new case
        
        Args:
            case_name: Name of the case
            case_number: Official case number
            description: Case description
            investigating_officer: Officer name
            user_id: ID/Username of the creator
            
        Returns:
            Tuple of (success, message)
        """
        conn = None
        try:
            # Sanitize case name for filename
            safe_case_name = "".join(c for c in case_name if c.isalnum() or c in (' ', '_', '-')).strip()
            db_filename = f"case_{safe_case_name.replace(' ', '_')}.db"
            db_path = os.path.join(self.base_db_path, db_filename)
            
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO cases (case_name, case_number, description, investigating_officer, db_path, last_accessed, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (case_name, case_number, description, investigating_officer, db_path, datetime.now(), user_id))
            
            conn.commit()
            
            # Create the case database
            self._initialize_case_database(db_path)
            
            return True, f"Case '{case_name}' created successfully!"
        
        except sqlite3.IntegrityError:
            return False, f"Case '{case_name}' already exists!"
        except Exception as e:
            return False, f"Error creating case: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def _initialize_case_database(self, db_path: str):
        """Initialize a new case database with CDR tables"""
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS cdrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_no TEXT,
                call_type TEXT,
                toc TEXT,
                b_party_no TEXT,
                lrn_no TEXT,
                lrn_tsp_lsa TEXT,
                datetime TIMESTAMP,
                duration_seconds INTEGER,
                first_cgi_lat REAL,
                first_cgi_long REAL,
                first_cgi TEXT,
                last_cgi_lat REAL,
                last_cgi_long REAL,
                last_cgi TEXT,
                smsc_no TEXT,
                service_type TEXT,
                imei TEXT,
                imsi TEXT,
                call_fow_no TEXT,
                roam_nw TEXT,
                sw_msc_id TEXT,
                in_tg TEXT,
                out_tg TEXT,
                vowifi_first_ue_ip TEXT,
                port1 TEXT,
                vowifi_last_ue_ip TEXT,
                port2 TEXT,
                uploaded_file TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_target_no ON cdrs(target_no)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_b_party_no ON cdrs(b_party_no)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_imei ON cdrs(imei)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_datetime ON cdrs(datetime)')
            
            # Create uploads tracking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                records_count INTEGER,
                notes TEXT
            )
            ''')
            
            conn.commit()
        finally:
            if conn:
                conn.close()
    
    def get_all_cases(self, user_id: str = None) -> List[Tuple]:
        """
        Get all cases for a specific user
        
        Args:
            user_id: ID/Username of the user
            
        Returns:
            List of case tuples
        """
        conn = None
        try:
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            query = '''
            SELECT id, case_name, case_number, investigating_officer, created_date, last_accessed, status
            FROM cases
            '''
            params = []
            
            if user_id:
                query += ' WHERE user_id = ?'
                params.append(user_id)
            
            query += ' ORDER BY last_accessed DESC'
            
            cursor.execute(query, params)
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching cases: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_case_by_name(self, case_name: str) -> Optional[Tuple]:
        """
        Get case details by name
        
        Args:
            case_name: Name of the case
            
        Returns:
            Case tuple or None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, case_name, case_number, description, investigating_officer, 
                   created_date, last_accessed, db_path, status
            FROM cases
            WHERE case_name = ?
            ''', (case_name,))
            
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching case: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_case_db_path(self, case_name: str) -> Optional[str]:
        """
        Get database path for a case
        
        Args:
            case_name: Name of the case
            
        Returns:
            Database path or None
        """
        case = self.get_case_by_name(case_name)
        if case:
            return case[7]  # db_path is at index 7
        return None
    
    def update_last_accessed(self, case_name: str):
        """
        Update last accessed timestamp for a case
        
        Args:
            case_name: Name of the case
        """
        conn = None
        try:
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE cases
            SET last_accessed = ?
            WHERE case_name = ?
            ''', (datetime.now(), case_name))
            
            conn.commit()
        except Exception as e:
            print(f"Error updating last accessed: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_case(self, case_name: str) -> Tuple[bool, str]:
        """
        Delete a case
        
        Args:
            case_name: Name of the case to delete
            
        Returns:
            Tuple of (success, message)
        """
        conn = None
        try:
            case = self.get_case_by_name(case_name)
            if not case:
                return False, f"Case '{case_name}' not found!"
            
            db_path = case[7]
            
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cases WHERE case_name = ?', (case_name,))
            conn.commit()
            
            # Delete the database file
            if os.path.exists(db_path):
                os.remove(db_path)
            
            return True, f"Case '{case_name}' deleted successfully!"
        except Exception as e:
            return False, f"Error deleting case: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def update_case_status(self, case_name: str, status: str) -> Tuple[bool, str]:
        """
        Update case status
        
        Args:
            case_name: Name of the case
            status: New status (Active, Closed, Archived)
            
        Returns:
            Tuple of (success, message)
        """
        conn = None
        try:
            conn = sqlite3.connect(self.cases_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE cases
            SET status = ?
            WHERE case_name = ?
            ''', (status, case_name))
            
            conn.commit()
            
            return True, f"Case status updated to '{status}'"
        except Exception as e:
            return False, f"Error updating case status: {str(e)}"
        finally:
            if conn:
                conn.close()
    
    def get_case_statistics(self, case_name: str) -> dict:
        """
        Get statistics for a case
        
        Args:
            case_name: Name of the case
            
        Returns:
            Dictionary with statistics
        """
        db_path = self.get_case_db_path(case_name)
        if not db_path or not os.path.exists(db_path):
            return {}
        
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get total records
            cursor.execute('SELECT COUNT(*) FROM cdrs')
            total_records = cursor.fetchone()[0]
            
            # Get unique numbers
            cursor.execute('SELECT COUNT(DISTINCT target_no) FROM cdrs')
            unique_a_party = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT b_party_no) FROM cdrs')
            unique_b_party = cursor.fetchone()[0]
            
            # Get number of uploaded files
            cursor.execute('SELECT COUNT(*) FROM uploads')
            uploaded_files = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'unique_a_party': unique_a_party,
                'unique_b_party': unique_b_party,
                'uploaded_files': uploaded_files
            }
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}
        finally:
            if conn:
                conn.close()
