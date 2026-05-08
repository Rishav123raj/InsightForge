import csv
import sqlite3
from pathlib import Path
from pypdf import PdfReader
from .config import get_settings

SCHEMA = {
    "movies": """CREATE TABLE IF NOT EXISTS movies(
        movie_id TEXT PRIMARY KEY,title TEXT,genre TEXT,release_date TEXT,budget REAL,studio TEXT)""",
    "viewers": """CREATE TABLE IF NOT EXISTS viewers(
        viewer_id TEXT PRIMARY KEY,age_segment TEXT,city TEXT,country TEXT,subscription_tier TEXT,email TEXT)""",
    "watch_activity": """CREATE TABLE IF NOT EXISTS watch_activity(
        activity_id TEXT PRIMARY KEY,viewer_id TEXT,movie_id TEXT,watch_date TEXT,minutes_watched REAL,completed INTEGER,device TEXT)""",
    "reviews": """CREATE TABLE IF NOT EXISTS reviews(
        review_id TEXT PRIMARY KEY,viewer_id TEXT,movie_id TEXT,review_date TEXT,rating REAL,sentiment TEXT,comment TEXT)""",
    "marketing_spend": """CREATE TABLE IF NOT EXISTS marketing_spend(
        spend_id TEXT PRIMARY KEY,movie_id TEXT,campaign TEXT,channel TEXT,spend_date TEXT,amount REAL,impressions INTEGER,clicks INTEGER)""",
    "regional_performance": """CREATE TABLE IF NOT EXISTS regional_performance(
        row_id TEXT PRIMARY KEY,movie_id TEXT,city TEXT,month TEXT,views INTEGER,completion_rate REAL,revenue REAL)""",
    "documents": """CREATE TABLE IF NOT EXISTS documents(
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,file_name TEXT,title TEXT,body TEXT,source_type TEXT)""",
}


def connect() -> sqlite3.Connection:
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> dict:
    settings = get_settings()
    with connect() as conn:
        for ddl in SCHEMA.values():
            conn.execute(ddl)
        conn.commit()
    return ingest_all(settings.csv_dir, settings.pdf_dir)


def ingest_all(csv_dir: Path, pdf_dir: Path) -> dict:
    counts = {"csv_rows": 0, "documents": 0}
    with connect() as conn:
        for path in sorted(csv_dir.glob("*.csv")):
            table = path.stem
            if table not in SCHEMA:
                continue
            conn.execute(f"DELETE FROM {table}")
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                if not rows:
                    continue
                columns = list(rows[0].keys())
                placeholders = ",".join(["?"] * len(columns))
                conn.executemany(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                    [[row[column] for column in columns] for row in rows],
                )
                counts["csv_rows"] += len(rows)
        conn.execute("DELETE FROM documents")
        for path in sorted(pdf_dir.glob("*.pdf")):
            text = extract_pdf_text(path)
            title = path.stem.replace("_", " ").title()
            conn.execute(
                "INSERT INTO documents(file_name,title,body,source_type) VALUES (?,?,?,?)",
                (path.name, title, text, "pdf"),
            )
            counts["documents"] += 1
        conn.commit()
    return counts


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

if __name__ == "__main__":
    print("Starting database initialization...")

    result = init_db()

    print("Database initialized successfully!")
    print("Ingestion Summary:", result)