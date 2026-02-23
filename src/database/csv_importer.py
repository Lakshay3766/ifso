#!/usr/bin/env python3
"""
CSV Importer Module
Handles importing CDR data from CSV files
"""

import csv
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from .db_manager import DatabaseManager


class CSVImporter:
    """Handles CSV file imports for CDR data"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize CSV importer
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
    
    @staticmethod
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
            except ValueError:
                return None, None
        return None, None
    
    def import_csv(self, csv_file_path: str, progress_callback: Optional[Callable] = None) -> Tuple[bool, str, int]:
        """
        Import CSV file into database
        
        Args:
            csv_file_path: Path to CSV file
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (success, message, count)
        """
        try:
            file_size = os.path.getsize(csv_file_path)
            file_name = os.path.basename(csv_file_path)
            import_batch_id = self.db_manager.create_import_batch(file_name)

            def parse_datetime_str(date_value: str, time_value: str) -> Optional[str]:
                date_value = (date_value or "").strip().strip("'")
                time_value = (time_value or "").strip()
                if not date_value or not time_value:
                    return None
                try:
                    dt = datetime.strptime(f"{date_value} {time_value}", "%d/%m/%Y %H:%M:%S")
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    return None

            inserted = 0
            errors = 0
            batch: List[Dict[str, Any]] = []
            batch_size = 1000

            with open(csv_file_path, 'r', newline='', encoding='utf-8-sig', errors='replace') as csvfile:
                header_pos = None
                while True:
                    pos = csvfile.tell()
                    line = csvfile.readline()
                    if not line:
                        break
                    if 'Target No' in line:
                        header_pos = pos
                        break

                if header_pos is None:
                    return False, "Header line with 'Target No' not found in CSV file.", 0

                csvfile.seek(header_pos)
                reader = csv.DictReader(csvfile)

                for idx, row in enumerate(reader, start=1):
                    try:
                        cleaned_row = {
                            str(k).strip(): (v.strip() if isinstance(v, str) else v)
                            for k, v in row.items()
                            if k is not None
                        }

                        # Skip footer/junk rows (e.g. "This is System generated...")
                        target = (cleaned_row.get('Target No') or '').strip().strip("'")
                        if not target or not target[0].isdigit():
                            continue

                        dt_str = parse_datetime_str(
                            cleaned_row.get('Date', ''),
                            cleaned_row.get('Time', ''),
                        )

                        duration = None
                        dur_str = (cleaned_row.get('Dur(s)', '') or '').strip()
                        if dur_str:
                            try:
                                duration = int(float(dur_str))
                            except Exception:
                                duration = None

                        first_cgi_lat, first_cgi_long = self.parse_lat_long(cleaned_row.get('First CGI Lat/Long', ''))
                        last_cgi_lat, last_cgi_long = self.parse_lat_long(cleaned_row.get('Last CGI Lat/Long', ''))

                        record: Dict[str, Any] = {
                            'target_no': cleaned_row.get('Target No'),
                            'call_type': cleaned_row.get('Call Type'),
                            'toc': cleaned_row.get('TOC'),
                            'b_party_no': cleaned_row.get('B Party No'),
                            'lrn_no': cleaned_row.get('LRN No'),
                            'lrn_tsp_lsa': cleaned_row.get('LRN TSP-LSA'),
                            'datetime': dt_str,
                            'duration_seconds': duration,
                            'first_cgi_lat': first_cgi_lat,
                            'first_cgi_long': first_cgi_long,
                            'first_cgi': cleaned_row.get('First CGI'),
                            'last_cgi_lat': last_cgi_lat,
                            'last_cgi_long': last_cgi_long,
                            'last_cgi': cleaned_row.get('Last CGI'),
                            'smsc_no': cleaned_row.get('SMSC No'),
                            'service_type': cleaned_row.get('Service Type'),
                            'imei': cleaned_row.get('IMEI'),
                            'imsi': cleaned_row.get('IMSI'),
                            'call_fow_no': cleaned_row.get('Call Fow No'),
                            'roam_nw': cleaned_row.get('Roam Nw'),
                            'sw_msc_id': cleaned_row.get('SW & MSC ID'),
                            'in_tg': cleaned_row.get('IN TG'),
                            'out_tg': cleaned_row.get('OUT TG'),
                            'vowifi_first_ue_ip': cleaned_row.get('Vowifi First UE IP'),
                            'port1': cleaned_row.get('Port1'),
                            'vowifi_last_ue_ip': cleaned_row.get('Vowifi Last UE IP'),
                            'port2': cleaned_row.get('Port2'),
                            'import_batch_id': import_batch_id,
                        }

                        batch.append(record)
                        if len(batch) >= batch_size:
                            inserted += self.db_manager.insert_records(batch)
                            batch.clear()

                            if progress_callback and file_size > 0:
                                progress = int(min(100, (csvfile.tell() / file_size) * 100))
                                progress_callback(progress, inserted)

                    except Exception as e:
                        errors += 1
                        print(f"Error processing row {idx}: {str(e)}")
                        continue

                if batch:
                    inserted += self.db_manager.insert_records(batch)
                    batch.clear()

                if progress_callback:
                    progress_callback(100, inserted)

                self.db_manager.finalize_import_batch(import_batch_id, inserted)

                if inserted > 0:
                    msg = f"Successfully uploaded {inserted} records from {csv_file_path}"
                    if errors:
                        msg += f" (skipped {errors} bad rows)"
                    return True, msg, inserted

                return False, "No records were uploaded. Please check the CSV format.", 0

        except FileNotFoundError:
            return False, f"File not found: {csv_file_path}", 0
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}", 0
