from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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

# 一覧表示（トップページ）
@app.route("/")
def index():
    # 1. URLから「誰のデータを見たいか」を受け取る（例: /?user=父）
    target_user = request.args.get("user")
    
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    
    # 2. 登録されている家族（ユーザー）を全員連れてくる
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    # 3. 家計簿データを取得（特定の家族か、全員分か）
    if target_user:
        cur.execute("SELECT * FROM records WHERE user_name = ? ORDER BY date DESC", (target_user,))
    else:
        cur.execute("SELECT * FROM records ORDER BY date DESC")
    records = cur.fetchall()
    conn.close()

    total = sum(r[2] if r[4] == "収入" else -r[2] for r in records)

    # 5. すべての情報をHTMLに送る
    return render_template("index.html", 
                           records=records, 
                           total=total, 
                           users=users, 
                           current_user=target_user)

# データ追加（追加：家族リストを読み込み、名前も保存する）
@app.route("/add", methods=["GET", "POST"])
def add():
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()

    if request.method == "POST":
        date = request.form["date"]
        amount = int(request.form["amount"])
        category = request.form["category"]
        type_val = request.form["type"]
        memo = request.form["memo"]
        user_name = request.form["user_name"]

        cur.execute("""
        INSERT INTO records (date, amount, category, type, memo, user_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (date, amount, category, type_val, memo, user_name))
        conn.commit()
        conn.close()
        return redirect("/")
    
    #追加：登録されている家族を読み込んで選択肢にする
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template("add.html", users=users)

# 追加家族登録ページ
@app.route("/user_setting", methods=["GET", "POST"])
def user_setting():
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    
    if request.method == "POST":
        new_user = request.form["new_user"]
        # 重複しないように保存
        cur.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (new_user,))
        conn.commit()
    
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    conn.close()
    return render_template("user_setting.html", users=users)

# データ削除
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# データ編集
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("kakeibo.db")
    cur = conn.cursor()

    if request.method == "POST":
        date = request.form["date"]
        amount = int(request.form["amount"])
        category = request.form["category"]
        type_val = request.form["type"]
        memo = request.form["memo"]

        cur.execute("""
            UPDATE records 
            SET date=?, amount=?, category=?, type=?, memo=? 
            WHERE id=?
        """, (date, amount, category, type_val, memo, id))
        conn.commit()
        conn.close()
        return redirect("/")

    cur.execute("SELECT * FROM records WHERE id = ?", (id,))
    record = cur.fetchone()
    conn.close()
    return render_template("edit.html", record=record)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

#python app.py
