import os
import sqlite3

def initialize_database():
    db_dir = 'instance'
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")

    db_path = os.path.join(db_dir, 'database.db')
    schema_path = os.path.join('database', 'schema.sql')

    print(f"Initializing database: {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

if __name__ == '__main__':
    initialize_database()
