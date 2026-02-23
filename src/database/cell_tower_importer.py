#!/usr/bin/env python3
"""
Cell Tower CSV Importer
Handles importing cell tower location data from CSV files.
Supports flexible column mapping for different CSV formats.
"""

import csv
import os
from typing import Any, Callable, Dict, List, Optional, Tuple
from .db_manager import DatabaseManager


# Common column name aliases → internal field name
_COLUMN_MAP = {
    # CGI / Cell ID
    "cgi": "cgi", "cell_id": "cgi", "cellid": "cgi", "cell id": "cgi",
    "cell_global_identity": "cgi", "ci": "cgi",
    # Latitude
    "latitude": "latitude", "lat": "latitude",
    # Longitude
    "longitude": "longitude", "long": "longitude", "lon": "longitude", "lng": "longitude",
    # Address
    "address": "address", "site_address": "address", "location": "address",
    "site address": "address", "site_location": "address",
    # Tower name
    "tower_name": "tower_name", "site_name": "tower_name", "tower name": "tower_name",
    "site name": "tower_name", "name": "tower_name", "site_id": "tower_name",
    "site id": "tower_name",
    # Operator
    "operator": "operator", "tsp": "operator", "provider": "operator",
    "network": "operator",
    # City
    "city": "city", "district": "city", "town": "city",
    # State
    "state": "state", "circle": "state", "region": "state", "lsa": "state",
    # Azimuth
    "azimuth": "azimuth", "az": "azimuth", "bearing": "azimuth",
}


class CellTowerImporter:
    """Handles CSV imports for cell tower location data."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def _normalize_header(header: str) -> str:
        return header.strip().lower().replace("-", "_")

    def _map_columns(self, csv_headers: List[str]) -> Dict[str, str]:
        """Map CSV column names to internal field names."""
        mapping: Dict[str, str] = {}
        for h in csv_headers:
            norm = self._normalize_header(h)
            if norm in _COLUMN_MAP:
                mapping[h] = _COLUMN_MAP[norm]
        return mapping

    def import_csv(
        self,
        csv_file_path: str,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[bool, str, int]:
        """
        Import a cell tower CSV file.

        Returns:
            Tuple of (success, message, count)
        """
        try:
            file_size = os.path.getsize(csv_file_path)
            file_name = os.path.basename(csv_file_path)
            batch_id = self.db_manager.create_cell_tower_import_batch(file_name)

            inserted = 0
            errors = 0
            batch: List[Dict[str, Any]] = []
            batch_size = 1000

            with open(csv_file_path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return False, "Could not read CSV headers.", 0

                col_map = self._map_columns(list(reader.fieldnames))
                if "cgi" not in col_map.values():
                    return False, "No CGI / Cell ID column found in CSV. Expected a column named CGI, Cell ID, or similar.", 0

                for idx, row in enumerate(reader, start=1):
                    try:
                        record: Dict[str, Any] = {"import_batch_id": batch_id}
                        for csv_col, field in col_map.items():
                            val = (row.get(csv_col) or "").strip().strip("'\"")
                            if field in ("latitude", "longitude"):
                                try:
                                    record[field] = float(val) if val else None
                                except ValueError:
                                    record[field] = None
                            else:
                                record[field] = val if val else None

                        if not record.get("cgi"):
                            continue

                        batch.append(record)
                        if len(batch) >= batch_size:
                            inserted += self.db_manager.insert_cell_towers(batch)
                            batch.clear()
                            if progress_callback and file_size > 0:
                                progress = int(min(100, (f.tell() / file_size) * 100))
                                progress_callback(progress, inserted)
                    except Exception as e:
                        errors += 1
                        print(f"Cell tower row {idx} error: {e}")
                        continue

                if batch:
                    inserted += self.db_manager.insert_cell_towers(batch)
                    batch.clear()

                if progress_callback:
                    progress_callback(100, inserted)

                self.db_manager.finalize_cell_tower_import(batch_id, inserted)

                if inserted > 0:
                    msg = f"Successfully imported {inserted} cell towers from {file_name}"
                    if errors:
                        msg += f" (skipped {errors} bad rows)"
                    return True, msg, inserted

                return False, "No cell towers were imported. Check that the CSV has a CGI column.", 0

        except FileNotFoundError:
            return False, f"File not found: {csv_file_path}", 0
        except Exception as e:
            return False, f"Error importing cell towers: {str(e)}", 0
