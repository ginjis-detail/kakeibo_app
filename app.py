from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DB初期化
def init_db():
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount INTEGER,
        category TEXT,
        type TEXT,
        memo TEXT
    )
    """)
    conn.commit()
    conn.close()

# トップページ（一覧）
@app.route("/")
def index():
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM records ORDER BY date DESC")
    records = cur.fetchall()
    conn.close()

    total = 0
    for r in records:
        amount = r[2]        # 金額
        category = r[4]      # 収入か支出か

        if category == "income":
            total += amount  # 収入ならプラス
        else:
            total -= amount  # 支出ならマイナス

    return render_template("index.html", records=records, total=total)

# 追加
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        date = request.form["date"]
        amount = int(request.form["amount"])
        category = request.form["category"]
        type_ = request.form["type"]
        memo = request.form["memo"]

        conn = sqlite3.connect("kakeibo.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO records (date, amount, category, type, memo)
        VALUES (?, ?, ?, ?, ?)
        """, (date, amount, category, type_, memo))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)