#!/usr/bin/env python3
"""
Database Manager Module
Handles all SQLite database operations for CDR records
"""

import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple


class DatabaseManager:
    """Manages all database operations for CDR records"""

    _INSERT_COLUMNS: Tuple[str, ...] = (
        "target_no",
        "call_type",
        "toc",
        "b_party_no",
        "lrn_no",
        "lrn_tsp_lsa",
        "datetime",
        "duration_seconds",
        "first_cgi_lat",
        "first_cgi_long",
        "first_cgi",
        "last_cgi_lat",
        "last_cgi_long",
        "last_cgi",
        "smsc_no",
        "service_type",
        "imei",
        "imsi",
        "call_fow_no",
        "roam_nw",
        "sw_msc_id",
        "in_tg",
        "out_tg",
        "vowifi_first_ue_ip",
        "port1",
        "vowifi_last_ue_ip",
        "port2",
        "import_batch_id",
    )
    _SAFE_DISTINCT_COLUMNS = {
        "call_type",
        "service_type",
        "toc",
        "roam_nw",
        "first_cgi",
        "last_cgi",
    }
    
    def __init__(self, db_path: str = 'cdr_database.db'):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.create_tables()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        except sqlite3.DatabaseError:
            pass
        return conn
    
    def create_tables(self):
        """Create CDR table if it doesn't exist"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
            
                cursor.execute(
                    '''
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
                        import_batch_id INTEGER
                    )
                    '''
                )

                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS imports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT NOT NULL,
                        imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        record_count INTEGER DEFAULT 0
                    )
                    '''
                )

                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS cell_towers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cgi TEXT,
                        latitude REAL,
                        longitude REAL,
                        address TEXT,
                        tower_name TEXT,
                        operator TEXT,
                        city TEXT,
                        state TEXT,
                        azimuth TEXT,
                        import_batch_id INTEGER
                    )
                    '''
                )

                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS cell_tower_imports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT NOT NULL,
                        imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        record_count INTEGER DEFAULT 0
                    )
                    '''
                )

                # ── CDR Groups ──
                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS cdr_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    '''
                )

                cursor.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS group_imports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER NOT NULL,
                        import_batch_id INTEGER NOT NULL,
                        FOREIGN KEY (group_id) REFERENCES cdr_groups(id) ON DELETE CASCADE,
                        FOREIGN KEY (import_batch_id) REFERENCES imports(id) ON DELETE CASCADE,
                        UNIQUE(group_id, import_batch_id)
                    )
                    '''
                )

                # Ensure legacy databases have import_batch_id column
                cursor.execute("PRAGMA table_info(cdrs)")
                existing_cols = {row[1] for row in cursor.fetchall()}
                if "import_batch_id" not in existing_cols:
                    cursor.execute("ALTER TABLE cdrs ADD COLUMN import_batch_id INTEGER")

                # Add group_id to imports for legacy DBs
                cursor.execute("PRAGMA table_info(imports)")
                import_cols = {row[1] for row in cursor.fetchall()}
                if "group_id" not in import_cols:
                    cursor.execute("ALTER TABLE imports ADD COLUMN group_id INTEGER")

                # Create indexes for better search performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_target_no ON cdrs(target_no)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_b_party_no ON cdrs(b_party_no)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_imei ON cdrs(imei)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_imsi ON cdrs(imsi)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_type ON cdrs(call_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_type ON cdrs(service_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_datetime ON cdrs(datetime)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_first_cgi ON cdrs(first_cgi)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_cgi ON cdrs(last_cgi)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_import_batch ON cdrs(import_batch_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_imports_file_name ON imports(file_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cell_tower_cgi ON cell_towers(cgi)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cell_tower_import ON cell_towers(import_batch_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_imports_group ON group_imports(group_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_imports_batch ON group_imports(import_batch_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_imports_group ON imports(group_id)')
        except Exception as e:
            raise Exception(f"Error creating tables: {str(e)}")
    
    def insert_record(self, record: Dict[str, Any]) -> bool:
        """
        Insert a single CDR record
        
        Args:
            record: Dictionary containing CDR data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            inserted = self.insert_records([record])
            if inserted != 1:
                return False
            return True
        except Exception as e:
            print(f"Error inserting record: {str(e)}")
            return False

    def insert_records(self, records: Sequence[Dict[str, Any]]) -> int:
        if not records:
            return 0

        placeholders = ", ".join(["?"] * len(self._INSERT_COLUMNS))
        columns = ", ".join(self._INSERT_COLUMNS)
        insert_sql = f"INSERT INTO cdrs ({columns}) VALUES ({placeholders})"

        rows = []
        for record in records:
            rows.append(tuple(record.get(col) for col in self._INSERT_COLUMNS))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.executemany(insert_sql, rows)
            return len(rows)
        except Exception as e:
            print(f"Error inserting records: {str(e)}")
            return 0

    def create_import_batch(self, file_name: str) -> int:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO imports (file_name, imported_at, record_count) VALUES (?, CURRENT_TIMESTAMP, 0)",
                    (file_name,),
                )
                return int(cursor.lastrowid)
        except Exception as e:
            raise Exception(f"Error creating import batch: {str(e)}")

    def finalize_import_batch(self, batch_id: int, record_count: int) -> None:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE imports SET record_count = ? WHERE id = ?",
                    (int(record_count), int(batch_id)),
                )
        except Exception as e:
            raise Exception(f"Error finalizing import batch: {str(e)}")

    def get_import_batches(self) -> List[sqlite3.Row]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, file_name, imported_at, record_count FROM imports ORDER BY imported_at DESC, id DESC"
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting import batches: {str(e)}")
            return []

    def get_record_details(self, record_id: int) -> Optional[Dict[str, Any]]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cdrs WHERE id = ?", (record_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return dict(row)
        except Exception as e:
            print(f"Error getting record details: {str(e)}")
            return None

    def get_distinct_values(self, column: str, limit: int = 200) -> List[str]:
        if column not in self._SAFE_DISTINCT_COLUMNS:
            return []
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT DISTINCT {column} FROM cdrs WHERE {column} IS NOT NULL AND TRIM({column}) != '' LIMIT ?",
                    (limit,),
                )
                return [str(r[0]) for r in cursor.fetchall() if r[0] is not None]
        except Exception as e:
            print(f"Error getting distinct values: {str(e)}")
            return []

    def count_records_advanced(self, filters: Dict[str, Any]) -> int:
        query, params = self._build_advanced_where(filters, count_only=True)
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except Exception as e:
            print(f"Error counting records: {str(e)}")
            return 0

    def search_records_advanced(
        self,
        filters: Dict[str, Any],
        limit: int = 500,
        offset: int = 0,
    ) -> List[Tuple]:
        query, params = self._build_advanced_where(filters, count_only=False)
        query += " ORDER BY datetime DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([int(limit), int(offset)])
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error searching records: {str(e)}")
            return []

    def _build_advanced_where(self, filters: Dict[str, Any], count_only: bool) -> Tuple[str, List[Any]]:
        if count_only:
            select = "SELECT COUNT(*)"
        else:
            select = (
                "SELECT id, target_no, b_party_no, datetime, duration_seconds, call_type, "
                "service_type, imei, imsi, first_cgi, last_cgi"
            )

        query = f"{select} FROM cdrs WHERE 1=1"
        params: List[Any] = []

        if filters.get("a_party"):
            query += " AND target_no LIKE ?"
            params.append(f"%{filters['a_party']}%")

        if filters.get("b_party"):
            query += " AND b_party_no LIKE ?"
            params.append(f"%{filters['b_party']}%")

        if filters.get("imei"):
            query += " AND imei LIKE ?"
            params.append(f"%{filters['imei']}%")

        if filters.get("imsi"):
            query += " AND imsi LIKE ?"
            params.append(f"%{filters['imsi']}%")

        if filters.get("call_type"):
            query += " AND call_type = ?"
            params.append(filters["call_type"])

        if filters.get("service_type"):
            query += " AND service_type = ?"
            params.append(filters["service_type"])

        if filters.get("cgi"):
            query += " AND (first_cgi LIKE ? OR last_cgi LIKE ?)"
            params.extend([f"%{filters['cgi']}%", f"%{filters['cgi']}%"])

        if filters.get("duration_min") is not None:
            query += " AND duration_seconds >= ?"
            params.append(int(filters["duration_min"]))

        if filters.get("duration_max") is not None:
            query += " AND duration_seconds <= ?"
            params.append(int(filters["duration_max"]))

        date_from = filters.get("date_from")
        if date_from:
            query += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")

        date_to = filters.get("date_to")
        if date_to:
            query += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        time_from = filters.get("time_from")
        if time_from:
            query += " AND TIME(datetime) >= ?"
            params.append(time_from)

        time_to = filters.get("time_to")
        if time_to:
            query += " AND TIME(datetime) <= ?"
            params.append(time_to)

        return query, params
    
    def search_records(self, filters: Dict[str, str]) -> List[Tuple]:
        """
        Search CDR records with filters
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of matching records
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
            
                query = "SELECT id, target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa, datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi, last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type, imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg, vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2 FROM cdrs WHERE 1=1"
                params = []
            
                if filters.get('a_party'):
                    query += " AND target_no LIKE ?"
                    params.append(f"%{filters['a_party']}%")
            
                if filters.get('b_party'):
                    query += " AND b_party_no LIKE ?"
                    params.append(f"%{filters['b_party']}%")
            
                if filters.get('date'):
                    query += " AND DATE(datetime) = ?"
                    params.append(filters['date'])
            
                if filters.get('imei'):
                    query += " AND imei LIKE ?"
                    params.append(f"%{filters['imei']}%")
            
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error searching records: {str(e)}")
            return []
    
    def get_all_records(self, limit: int = 1000) -> List[Tuple]:
        """
        Get all records with optional limit
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa, datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi, last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type, imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg, vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2 FROM cdrs ORDER BY datetime DESC, id DESC LIMIT ?",
                    (int(limit),),
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching records: {str(e)}")
            return []
    
    def get_group_statistics(self, group_by: str, limit: int = 50) -> List[Tuple]:
        """
        Get grouped statistics
        
        Args:
            group_by: Field to group by (target_no, imei, call_type, service_type)
            limit: Maximum number of groups to return
            
        Returns:
            List of (value, count) tuples
        """
        allowed = {
            "target_no",
            "b_party_no",
            "imei",
            "imsi",
            "call_type",
            "service_type",
            "toc",
            "roam_nw",
            "sw_msc_id",
            "first_cgi",
            "last_cgi",
        }

        if group_by not in allowed:
            return []

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                query = f"""
                SELECT {group_by} AS value, COUNT(*) AS cnt
                FROM cdrs
                WHERE {group_by} IS NOT NULL AND TRIM({group_by}) != ''
                GROUP BY {group_by}
                ORDER BY cnt DESC
                LIMIT ?
                """
                cursor.execute(query, (int(limit),))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting group statistics: {str(e)}")
            return []
    
    def get_analytics(self, analytics_type: str) -> Any:
        """
        Get various analytics
        
        Args:
            analytics_type: Type of analytics (max_duration, max_imei, total_records, call_stats)
            
        Returns:
            Analytics data based on type
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
            
                if analytics_type == "max_duration":
                    cursor.execute("SELECT target_no, b_party_no, duration_seconds FROM cdrs WHERE duration_seconds IS NOT NULL ORDER BY duration_seconds DESC LIMIT 10")
                    return cursor.fetchall()
            
                elif analytics_type == "max_imei":
                    cursor.execute("SELECT imei, COUNT(*) FROM cdrs WHERE imei IS NOT NULL GROUP BY imei ORDER BY COUNT(*) DESC LIMIT 10")
                    return cursor.fetchall()
            
                elif analytics_type == "total_records":
                    cursor.execute("SELECT COUNT(*) FROM cdrs")
                    total = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(DISTINCT target_no) FROM cdrs")
                    unique_a = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(DISTINCT b_party_no) FROM cdrs")
                    unique_b = cursor.fetchone()[0]
                    return {'total': total, 'unique_a': unique_a, 'unique_b': unique_b}
            
                elif analytics_type == "call_stats":
                    cursor.execute("SELECT call_type, COUNT(*) FROM cdrs WHERE call_type IS NOT NULL GROUP BY call_type")
                    return cursor.fetchall()
            
                return None
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
            return None

    def get_summary_stats(self) -> Dict[str, Any]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM cdrs")
                total = int(cursor.fetchone()[0])

                cursor.execute("SELECT COUNT(DISTINCT target_no) FROM cdrs WHERE target_no IS NOT NULL AND TRIM(target_no) != ''")
                unique_a = int(cursor.fetchone()[0])

                cursor.execute("SELECT COUNT(DISTINCT b_party_no) FROM cdrs WHERE b_party_no IS NOT NULL AND TRIM(b_party_no) != ''")
                unique_b = int(cursor.fetchone()[0])

                cursor.execute("SELECT COUNT(DISTINCT imei) FROM cdrs WHERE imei IS NOT NULL AND TRIM(imei) != ''")
                unique_imei = int(cursor.fetchone()[0])

                cursor.execute("SELECT COUNT(DISTINCT imsi) FROM cdrs WHERE imsi IS NOT NULL AND TRIM(imsi) != ''")
                unique_imsi = int(cursor.fetchone()[0])

                cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM cdrs WHERE datetime IS NOT NULL AND TRIM(datetime) != ''")
                dt_min, dt_max = cursor.fetchone()

                return {
                    "total_records": total,
                    "unique_a_party": unique_a,
                    "unique_b_party": unique_b,
                    "unique_imei": unique_imei,
                    "unique_imsi": unique_imsi,
                    "min_datetime": dt_min,
                    "max_datetime": dt_max,
                }
        except Exception as e:
            print(f"Error getting summary stats: {str(e)}")
            return {}

    def get_top_duration_records(
        self,
        limit: int = 50,
        number: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Tuple]:
        where = "duration_seconds IS NOT NULL"
        params: List[Any] = []

        number = (number or "").strip()
        if number:
            where += " AND (target_no = ? OR b_party_no = ?)"
            params.extend([number, number])

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT id,
               datetime,
               target_no,
               b_party_no,
               duration_seconds,
               call_type,
               service_type,
               imei,
               imsi
        FROM cdrs
        WHERE {where}
        ORDER BY duration_seconds DESC, datetime DESC, id DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting top durations: {str(e)}")
            return []

    def get_top_imeis(
        self,
        limit: int = 50,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Tuple]:
        where = "imei IS NOT NULL AND TRIM(imei) != ''"
        params: List[Any] = []

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT imei,
               COUNT(*) AS calls,
               MIN(datetime) AS first_dt,
               MAX(datetime) AS last_dt
        FROM cdrs
        WHERE {where}
        GROUP BY imei
        ORDER BY calls DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting top IMEIs: {str(e)}")
            return []

    def get_distribution(
        self,
        column: str,
        limit: int = 200,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Tuple]:
        if column not in self._SAFE_DISTINCT_COLUMNS:
            return []

        where = f"{column} IS NOT NULL AND TRIM({column}) != ''"
        params: List[Any] = []

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT {column} AS value, COUNT(*) AS cnt
        FROM cdrs
        WHERE {where}
        GROUP BY {column}
        ORDER BY cnt DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting distribution for {column}: {str(e)}")
            return []

    def get_top_contacts(
        self,
        number: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
    ) -> List[Tuple]:
        number = (number or "").strip()
        if not number:
            return []

        out_where = "target_no = ? AND b_party_no IS NOT NULL AND TRIM(b_party_no) != ''"
        in_where = "b_party_no = ? AND target_no IS NOT NULL AND TRIM(target_no) != ''"
        out_params: List[Any] = [number]
        in_params: List[Any] = [number]

        if date_from:
            out_where += " AND datetime >= ?"
            in_where += " AND datetime >= ?"
            out_params.append(f"{date_from} 00:00:00")
            in_params.append(f"{date_from} 00:00:00")
        if date_to:
            out_where += " AND datetime <= ?"
            in_where += " AND datetime <= ?"
            out_params.append(f"{date_to} 23:59:59")
            in_params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT contact_no,
               COUNT(*) AS calls,
               SUM(COALESCE(duration_seconds, 0)) AS total_duration,
               MIN(datetime) AS first_dt,
               MAX(datetime) AS last_dt
        FROM (
            SELECT b_party_no AS contact_no, duration_seconds, datetime
            FROM cdrs
            WHERE {out_where}
            UNION ALL
            SELECT target_no AS contact_no, duration_seconds, datetime
            FROM cdrs
            WHERE {in_where}
        )
        WHERE contact_no IS NOT NULL AND TRIM(contact_no) != '' AND contact_no != ?
        GROUP BY contact_no
        ORDER BY calls DESC, total_duration DESC
        LIMIT ?
        """
        params = out_params + in_params + [number, int(limit)]

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting top contacts: {str(e)}")
            return []

    def get_contact_stats(
        self,
        number: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 5000,
    ) -> Dict[str, Dict[str, Any]]:
        rows = self.get_top_contacts(number=number, date_from=date_from, date_to=date_to, limit=limit)
        stats: Dict[str, Dict[str, Any]] = {}
        for contact_no, calls, total_duration, first_dt, last_dt in rows:
            stats[str(contact_no)] = {
                "calls": int(calls or 0),
                "total_duration": int(total_duration or 0),
                "first_dt": first_dt,
                "last_dt": last_dt,
            }
        return stats

    def get_mutual_contacts_two_numbers(
        self,
        number_a: str,
        number_b: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Tuple]:
        a_stats = self.get_contact_stats(number_a, date_from=date_from, date_to=date_to)
        b_stats = self.get_contact_stats(number_b, date_from=date_from, date_to=date_to)
        common = set(a_stats.keys()) & set(b_stats.keys())
        if not common:
            return []

        rows: List[Tuple] = []
        for contact in common:
            a_calls = a_stats[contact]["calls"]
            b_calls = b_stats[contact]["calls"]
            total_calls = a_calls + b_calls
            total_duration = int(a_stats[contact]["total_duration"]) + int(b_stats[contact]["total_duration"])
            rows.append((contact, a_calls, b_calls, total_calls, total_duration))

        rows.sort(key=lambda r: (r[3], r[4]), reverse=True)
        return rows[: int(limit)]

    def get_direct_link_summary(
        self,
        number_a: str,
        number_b: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        number_a = (number_a or "").strip()
        number_b = (number_b or "").strip()
        if not number_a or not number_b:
            return {}

        def add_date_filters(where: str, params: List[Any]) -> Tuple[str, List[Any]]:
            if date_from:
                where += " AND datetime >= ?"
                params.append(f"{date_from} 00:00:00")
            if date_to:
                where += " AND datetime <= ?"
                params.append(f"{date_to} 23:59:59")
            return where, params

        out_where, out_params = add_date_filters("target_no = ? AND b_party_no = ?", [number_a, number_b])
        in_where, in_params = add_date_filters("target_no = ? AND b_party_no = ?", [number_b, number_a])
        all_where, all_params = add_date_filters(
            "((target_no = ? AND b_party_no = ?) OR (target_no = ? AND b_party_no = ?))",
            [number_a, number_b, number_b, number_a],
        )

        sql = "SELECT COUNT(*) AS calls, SUM(COALESCE(duration_seconds, 0)) AS total_duration, MIN(datetime) AS first_dt, MAX(datetime) AS last_dt FROM cdrs WHERE "

        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                cursor.execute(sql + out_where, out_params)
                out_calls, out_dur, out_first, out_last = cursor.fetchone()

                cursor.execute(sql + in_where, in_params)
                in_calls, in_dur, in_first, in_last = cursor.fetchone()

                cursor.execute(sql + all_where, all_params)
                total_calls, total_dur, first_dt, last_dt = cursor.fetchone()

                return {
                    "number_a": number_a,
                    "number_b": number_b,
                    "a_to_b_calls": int(out_calls or 0),
                    "a_to_b_duration": int(out_dur or 0),
                    "b_to_a_calls": int(in_calls or 0),
                    "b_to_a_duration": int(in_dur or 0),
                    "total_calls": int(total_calls or 0),
                    "total_duration": int(total_dur or 0),
                    "first_dt": first_dt,
                    "last_dt": last_dt,
                    "a_to_b_first_dt": out_first,
                    "a_to_b_last_dt": out_last,
                    "b_to_a_first_dt": in_first,
                    "b_to_a_last_dt": in_last,
                }
        except Exception as e:
            print(f"Error getting direct link summary: {str(e)}")
            return {}

    def get_calls_between_numbers(
        self,
        number_a: str,
        number_b: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 500,
    ) -> List[Tuple]:
        number_a = (number_a or "").strip()
        number_b = (number_b or "").strip()
        if not number_a or not number_b:
            return []

        where = "((target_no = ? AND b_party_no = ?) OR (target_no = ? AND b_party_no = ?))"
        params: List[Any] = [number_a, number_b, number_b, number_a]

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT id,
               datetime,
               target_no,
               b_party_no,
               duration_seconds,
               call_type,
               service_type,
               imei,
               imsi,
               first_cgi,
               last_cgi
        FROM cdrs
        WHERE {where}
        ORDER BY datetime DESC, id DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting calls between numbers: {str(e)}")
            return []

    def get_call_type_distribution_for_pair(
        self,
        number_a: str,
        number_b: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Tuple]:
        number_a = (number_a or "").strip()
        number_b = (number_b or "").strip()
        if not number_a or not number_b:
            return []

        where = "((target_no = ? AND b_party_no = ?) OR (target_no = ? AND b_party_no = ?))"
        params: List[Any] = [number_a, number_b, number_b, number_a]

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT COALESCE(NULLIF(TRIM(call_type), ''), 'N/A') AS call_type,
               COUNT(*) AS cnt
        FROM cdrs
        WHERE {where}
        GROUP BY call_type
        ORDER BY cnt DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting call type distribution for pair: {str(e)}")
            return []

    def get_number_timeline(
        self,
        number: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        group_by: str = "day",
        limit: int = 400,
    ) -> List[Tuple]:
        number = (number or "").strip()
        if not number:
            return []

        if group_by == "hour":
            period_expr = "strftime('%Y-%m-%d %H:00', datetime)"
        else:
            period_expr = "strftime('%Y-%m-%d', datetime)"

        where = "(target_no = ? OR b_party_no = ?)"
        params: List[Any] = [number, number]
        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT {period_expr} AS period,
               COUNT(*) AS calls,
               SUM(COALESCE(duration_seconds, 0)) AS total_duration
        FROM cdrs
        WHERE {where}
        GROUP BY period
        ORDER BY period ASC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting timeline: {str(e)}")
            return []

    def get_numbers_by_imei(self, imei: str, limit: int = 200) -> List[Tuple]:
        imei = (imei or "").strip()
        if not imei:
            return []
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT target_no,
                           COUNT(*) AS calls,
                           MIN(datetime) AS first_dt,
                           MAX(datetime) AS last_dt
                    FROM cdrs
                    WHERE imei LIKE ? AND target_no IS NOT NULL AND TRIM(target_no) != ''
                    GROUP BY target_no
                    ORDER BY calls DESC
                    LIMIT ?
                    """,
                    (f"%{imei}%", int(limit)),
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting numbers by IMEI: {str(e)}")
            return []

    def get_imeis_by_number(self, number: str, limit: int = 200) -> List[Tuple]:
        number = (number or "").strip()
        if not number:
            return []
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT imei,
                           COUNT(*) AS calls,
                           MIN(datetime) AS first_dt,
                           MAX(datetime) AS last_dt
                    FROM cdrs
                    WHERE target_no = ? AND imei IS NOT NULL AND TRIM(imei) != ''
                    GROUP BY imei
                    ORDER BY calls DESC
                    LIMIT ?
                    """,
                    (number, int(limit)),
                )
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting IMEIs by number: {str(e)}")
            return []

    def get_top_cgi(
        self,
        cgi_field: str,
        number: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Tuple]:
        if cgi_field not in {"first_cgi", "last_cgi"}:
            return []

        where = f"{cgi_field} IS NOT NULL AND TRIM({cgi_field}) != ''"
        params: List[Any] = []

        number = (number or "").strip()
        if number:
            where += " AND (target_no = ? OR b_party_no = ?)"
            params.extend([number, number])

        if date_from:
            where += " AND datetime >= ?"
            params.append(f"{date_from} 00:00:00")
        if date_to:
            where += " AND datetime <= ?"
            params.append(f"{date_to} 23:59:59")

        sql = f"""
        SELECT {cgi_field} AS cgi, COUNT(*) AS cnt
        FROM cdrs
        WHERE {where}
        GROUP BY {cgi_field}
        ORDER BY cnt DESC
        LIMIT ?
        """
        params.append(int(limit))

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting top CGI: {str(e)}")
            return []

    def get_numbers_on_cgi(
        self,
        cgi_value: str,
        limit: int = 200,
    ) -> List[Tuple]:
        cgi_value = (cgi_value or "").strip()
        if not cgi_value:
            return []

        sql = """
        SELECT target_no, COUNT(*) AS cnt
        FROM cdrs
        WHERE target_no IS NOT NULL
          AND TRIM(target_no) != ''
          AND (first_cgi LIKE ? OR last_cgi LIKE ?)
        GROUP BY target_no
        ORDER BY cnt DESC
        LIMIT ?
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (f"%{cgi_value}%", f"%{cgi_value}%", int(limit)))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting numbers on CGI: {str(e)}")
            return []
    
    def clear_all_records(self) -> bool:
        """
        Clear all records from database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cdrs")
            return True
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            return False
    
    def export_to_list(self) -> Tuple[List[str], List[Tuple]]:
        """
        Export all records as list
        
        Returns:
            Tuple of (column_names, rows)
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cdrs")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                return columns, rows
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return [], []

    # ── Cell Tower Methods ──────────────────────────────────────────

    def create_cell_tower_import_batch(self, file_name: str) -> int:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO cell_tower_imports (file_name) VALUES (?)",
                    (file_name,),
                )
                return cursor.lastrowid or 0
        except Exception:
            return 0

    def finalize_cell_tower_import(self, batch_id: int, count: int):
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE cell_tower_imports SET record_count = ? WHERE id = ?",
                    (count, batch_id),
                )
        except Exception:
            pass

    def insert_cell_towers(self, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cols = ("cgi", "latitude", "longitude", "address", "tower_name",
                        "operator", "city", "state", "azimuth", "import_batch_id")
                placeholders = ",".join("?" for _ in cols)
                col_str = ",".join(cols)
                rows = [
                    tuple(r.get(c) for c in cols) for r in records
                ]
                cursor.executemany(
                    f"INSERT INTO cell_towers ({col_str}) VALUES ({placeholders})",
                    rows,
                )
                return len(rows)
        except Exception as e:
            print(f"Error inserting cell towers: {e}")
            return 0

    def lookup_towers_by_cgis(self, cgi_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """Look up cell towers for a list of CGI codes. Returns {cgi: row_dict}."""
        if not cgi_list:
            return {}
        result: Dict[str, Dict[str, Any]] = {}
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in cgi_list)
                cursor.execute(
                    f"SELECT cgi, latitude, longitude, address, tower_name, operator, city, state, azimuth FROM cell_towers WHERE cgi IN ({placeholders})",
                    cgi_list,
                )
                for row in cursor.fetchall():
                    result[row[0]] = {
                        "latitude": row[1], "longitude": row[2],
                        "address": row[3], "tower_name": row[4],
                        "operator": row[5], "city": row[6],
                        "state": row[7], "azimuth": row[8],
                    }
        except Exception as e:
            print(f"Error looking up towers: {e}")
        return result

    def get_cell_tower_count(self) -> int:
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT COUNT(*) FROM cell_towers").fetchone()
                return row[0] if row else 0
        except Exception:
            return 0

    def get_cell_tower_imports(self) -> List[Tuple]:
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT id, file_name, imported_at, record_count FROM cell_tower_imports ORDER BY id DESC"
                ).fetchall()
        except Exception:
            return []

    def clear_cell_towers(self):
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM cell_towers")
                conn.execute("DELETE FROM cell_tower_imports")
        except Exception as e:
            print(f"Error clearing cell towers: {e}")

    # ── Group Management ────────────────────────────────────────────

    def create_group(self, name: str) -> int:
        """Create a new CDR group. Returns the group ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO cdr_groups (name) VALUES (?)", (name.strip(),)
            )
            return cursor.lastrowid

    def get_all_groups(self) -> List[Tuple]:
        """Return all groups: [(id, name, created_at), ...]"""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT id, name, created_at FROM cdr_groups ORDER BY name"
                ).fetchall()
        except Exception:
            return []

    def delete_group(self, group_id: int):
        """Delete a group (does NOT delete the CDR files themselves)."""
        with self._connect() as conn:
            conn.execute("DELETE FROM group_imports WHERE group_id = ?", (group_id,))
            conn.execute("UPDATE imports SET group_id = NULL WHERE group_id = ?", (group_id,))
            conn.execute("DELETE FROM cdr_groups WHERE id = ?", (group_id,))

    def rename_group(self, group_id: int, new_name: str):
        """Rename a group."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE cdr_groups SET name = ? WHERE id = ?",
                (new_name.strip(), group_id),
            )

    def assign_import_to_group(self, import_batch_id: int, group_id: int):
        """Assign an import batch to a group."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO group_imports (group_id, import_batch_id) VALUES (?, ?)",
                (group_id, import_batch_id),
            )
            conn.execute(
                "UPDATE imports SET group_id = ? WHERE id = ?",
                (group_id, import_batch_id),
            )

    def remove_import_from_group(self, import_batch_id: int, group_id: int):
        """Remove an import batch from a group."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM group_imports WHERE group_id = ? AND import_batch_id = ?",
                (group_id, import_batch_id),
            )
            conn.execute(
                "UPDATE imports SET group_id = NULL WHERE id = ? AND group_id = ?",
                (import_batch_id, group_id),
            )

    def get_group_imports(self, group_id: int) -> List[Tuple]:
        """Get all import batches assigned to a group."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    """
                    SELECT i.id, i.file_name, i.imported_at, i.record_count
                    FROM imports i
                    INNER JOIN group_imports gi ON gi.import_batch_id = i.id
                    WHERE gi.group_id = ?
                    ORDER BY i.file_name
                    """,
                    (group_id,),
                ).fetchall()
        except Exception:
            return []

    def get_unassigned_imports(self) -> List[Tuple]:
        """Get import batches not assigned to any group."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    """
                    SELECT i.id, i.file_name, i.imported_at, i.record_count
                    FROM imports i
                    WHERE NOT EXISTS (
                        SELECT 1 FROM group_imports gi WHERE gi.import_batch_id = i.id
                    )
                    ORDER BY i.file_name
                    """
                ).fetchall()
        except Exception:
            return []

    def get_group_cdr_count(self, group_id: int) -> int:
        """Get total CDR record count for a group."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT COUNT(*) FROM cdrs c
                    INNER JOIN group_imports gi ON gi.import_batch_id = c.import_batch_id
                    WHERE gi.group_id = ?
                    """,
                    (group_id,),
                ).fetchone()
                return row[0] if row else 0
        except Exception:
            return 0

    def get_group_batch_ids(self, group_id: int) -> List[int]:
        """Get list of import_batch_ids for a group."""
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT import_batch_id FROM group_imports WHERE group_id = ?",
                    (group_id,),
                ).fetchall()
                return [r[0] for r in rows]
        except Exception:
            return []
