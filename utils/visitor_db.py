"""SQLite helper for Duka demo visitors.

This module creates a `visitors.db` SQLite database automatically and
provides small helper functions to initialize the DB and save visitor
records.

Functions
- `init_visitor_db(db_path: str | Path = None) -> None`
- `save_visitor(name: str, contact: str, db_path: str | Path = None) -> int`
- `get_recent_visitors(limit: int = 20, db_path: str | Path = None) -> list[dict]`

The DB schema:
- id INTEGER PRIMARY KEY AUTOINCREMENT
- name TEXT NOT NULL
- contact TEXT
- timestamp TEXT (ISO-8601)

The implementation is minimal and uses context managers for safety.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

DB_FILENAME = "visitors.db"


def _resolve_db_path(db_path: str | Path | None) -> Path:
	if db_path:
		return Path(db_path)
	# default: place DB next to this module
	return Path(__file__).resolve().parent / DB_FILENAME


def init_visitor_db(db_path: str | Path | None = None) -> None:
	"""Create the visitors DB and table if they don't exist.

	Args:
		db_path: optional path to the SQLite file. Defaults to `visitors.db`
				 located next to this module.
	"""
	path = _resolve_db_path(db_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(path)
	try:
		with conn:
			conn.execute(
				"""
				CREATE TABLE IF NOT EXISTS visitors (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					name TEXT NOT NULL,
					contact TEXT,
					timestamp TEXT NOT NULL
				)
				"""
			)
	finally:
		conn.close()


def save_visitor(name: str, contact: str | None = None, db_path: str | Path | None = None) -> int:
	"""Save a visitor record and return the new row id.

	Args:
		name: visitor name
		contact: visitor contact information (phone/email)
		db_path: optional DB path

	Returns:
		int: inserted row id
	"""
	if not name:
		raise ValueError("name is required")

	path = _resolve_db_path(db_path)
	timestamp = datetime.utcnow().isoformat()
	conn = sqlite3.connect(path)
	try:
		with conn:
			cur = conn.execute(
				"INSERT INTO visitors (name, contact, timestamp) VALUES (?, ?, ?)",
				(name, contact, timestamp),
			)
			return cur.lastrowid
	finally:
		conn.close()


def get_recent_visitors(limit: int = 20, db_path: str | Path | None = None) -> List[Dict]:
	"""Return recent visitor rows as list of dicts ordered by newest first."""
	path = _resolve_db_path(db_path)
	conn = sqlite3.connect(path)
	try:
		conn.row_factory = sqlite3.Row
		cur = conn.execute(
			"SELECT id, name, contact, timestamp FROM visitors ORDER BY id DESC LIMIT ?",
			(limit,),
		)
		rows = cur.fetchall()
		return [dict(r) for r in rows]
	finally:
		conn.close()


__all__ = ["init_visitor_db", "save_visitor", "get_recent_visitors"]

