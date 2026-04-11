from flask import render_template, request, redirect
from database import get_db

def register_routes(app):#一覧表示
    @app.route("/")
    def index():
        target_user = request.args.get("user")
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()

        if target_user:
            cur.execute("SELECT * FROM records WHERE user_name = ? ORDER BY date DESC", (target_user,))
        else:
            cur.execute("SELECT * FROM records ORDER BY date DESC")
        records = cur.fetchall()
        conn.close()

        total = sum(r[2] if r[4] == "収入" else -r[2] for r in records)

        return render_template("index.html", 
                               records=records, 
                               total=total, 
                               users=users, 
                               current_user=target_user)

    @app.route("/add", methods=["GET", "POST"])#収支データ追加
    def add():
        conn = get_db()
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
        
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        conn.close()
        return render_template("add.html", users=users)

    @app.route("/user_setting", methods=["GET", "POST"])#家族（ユーザー）追加
    def user_setting():
        conn = get_db() 
        cur = conn.cursor()
        
        if request.method == "POST":
            new_user = request.form["new_user"]
            cur.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (new_user,))
            conn.commit()
        
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        conn.close()
        return render_template("user_setting.html", users=users)

    @app.route("/delete/<int:id>")#削除
    def delete(id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return redirect("/")

    @app.route("/edit/<int:id>", methods=["GET", "POST"])#編集
    def edit(id):
        conn = get_db()
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
    
    @app.route("/delete_user/<string:name>") # アカウント削除
    def delete_user(name):
        conn = get_db()
        cur = conn.cursor()
        #ユーザー削除
        cur.execute("DELETE FROM records WHERE user_name = ?", (name,))
        cur.execute("DELETE FROM users WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        return redirect("/")