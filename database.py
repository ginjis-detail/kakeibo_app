import sqlite3

def get_db():
    conn = sqlite3.connect("kakeibo.db")
    # データを数字だけでなく名前で扱えるように設定
    conn.row_factory = sqlite3.Row
    return conn

# DB初期化（起動時にテーブルがなければ作る）
def init_db():
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount INTEGER,
        category TEXT,
        type TEXT,
        memo TEXT,
        user_name TEXT
    )
    """)
    conn.commit()
    conn.close()