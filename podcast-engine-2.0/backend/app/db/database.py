import json
import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO)

DB_PATH = "data/database.sqlite"


def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed_items (
            id TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            audio_url TEXT,
            duration REAL,
            tags TEXT,
            knowledge_density TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logging.info("Database initialized.")


def add_feed_item(item_id, title, source, audio_url, duration, tags, density):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO feed_items (id, title, source, audio_url, duration, tags, knowledge_density)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (item_id, title, source, audio_url, duration, json.dumps(tags), density),
    )
    conn.commit()
    conn.close()
    logging.info(f"Added feed item: {title}")


def get_feed(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feed_items ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    feed = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item["tags"])
        feed.append(item)
    return feed


if __name__ == "__main__":
    init_db()
