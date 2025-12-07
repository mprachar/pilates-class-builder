"""
Database module for Pilates Class Builder.

Uses SQLite to store saved classes and exercise data.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "pilates_classes.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Saved classes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration_minutes INTEGER NOT NULL,
            level TEXT NOT NULL,
            equipment TEXT NOT NULL,
            sections TEXT NOT NULL,
            total_exercises INTEGER NOT NULL,
            transitions INTEGER NOT NULL,
            max_transitions INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_class(class_data: dict, name: str, description: str = "") -> int:
    """
    Save a class to the database.

    Args:
        class_data: The generated class data dict
        name: User-provided name for the class
        description: Optional description

    Returns:
        The ID of the saved class
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO saved_classes (
            name, description, duration_minutes, level, equipment,
            sections, total_exercises, transitions, max_transitions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        description,
        class_data["duration_minutes"],
        class_data["level"],
        json.dumps(class_data["equipment"]),
        json.dumps(class_data["sections"]),
        class_data["total_exercises"],
        class_data["transitions"],
        class_data.get("max_transitions", 5),
    ))

    class_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return class_id


def update_class(class_id: int, class_data: dict, name: str = None, description: str = None) -> bool:
    """
    Update an existing saved class.

    Args:
        class_id: ID of the class to update
        class_data: Updated class data
        name: Optional new name
        description: Optional new description

    Returns:
        True if updated successfully
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build update query dynamically
    updates = [
        "sections = ?",
        "total_exercises = ?",
        "transitions = ?",
        "updated_at = CURRENT_TIMESTAMP",
    ]
    values = [
        json.dumps(class_data["sections"]),
        class_data["total_exercises"],
        class_data["transitions"],
    ]

    if name is not None:
        updates.append("name = ?")
        values.append(name)

    if description is not None:
        updates.append("description = ?")
        values.append(description)

    values.append(class_id)

    cursor.execute(f"""
        UPDATE saved_classes
        SET {", ".join(updates)}
        WHERE id = ?
    """, values)

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_class(class_id: int) -> dict:
    """
    Get a saved class by ID.

    Returns:
        Class data dict or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM saved_classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "duration_minutes": row["duration_minutes"],
        "level": row["level"],
        "level_name": row["level"],  # Will be filled by caller
        "equipment": json.loads(row["equipment"]),
        "sections": json.loads(row["sections"]),
        "total_exercises": row["total_exercises"],
        "transitions": row["transitions"],
        "max_transitions": row["max_transitions"],
        "equipment_flow": [],  # Reconstructed from sections
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_classes() -> list:
    """
    List all saved classes (summary only).

    Returns:
        List of class summaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description, duration_minutes, level,
               total_exercises, transitions, created_at, updated_at
        FROM saved_classes
        ORDER BY updated_at DESC
    """)

    classes = []
    for row in cursor.fetchall():
        classes.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "duration_minutes": row["duration_minutes"],
            "level": row["level"],
            "total_exercises": row["total_exercises"],
            "transitions": row["transitions"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })

    conn.close()
    return classes


def delete_class(class_id: int) -> bool:
    """
    Delete a saved class.

    Returns:
        True if deleted successfully
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM saved_classes WHERE id = ?", (class_id,))
    success = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return success


# Initialize database on module import
init_db()
