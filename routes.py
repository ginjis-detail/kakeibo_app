from flask import render_template, request, redirect
from database import get_db

def register_routes(app):#一覧表示
    @app.route("/")
    def index():
        target_user = request.args.get("user")
        target_cat = request.args.get("cat")
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()

        query = "SELECT * FROM records WHERE 1=1"
        params = []
        
        if target_user:
            query += " AND user_name = ?"
            params.append(target_user)
            
        if target_cat:
            query += " AND category = ?"
            params.append(target_cat)

        query += " ORDER BY date DESC"
        
        cur.execute(query, params)
        records = cur.fetchall()
        
        conn.close()

        total = sum(int(r[2]) if r[4] == "収入" else -int(r[2]) for r in records)

        return render_template("index.html", 
                               records=records, 
                               total=total, 
                               users=users, 
                               categories=categories,
                               current_user=target_user,
                               current_cat=target_cat)

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

        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()

        conn.close()
        return render_template("edit.html", record=record, categories=categories)
    
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
    
    @app.route("/category_setting", methods=["GET", "POST"])#カテゴリ追加・表示
    def category_setting():
        conn = get_db()
        cur = conn.cursor()
        
        if request.method == "POST":
            new_category = request.form["new_category"]
            if new_category:
                cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (new_category,))
                conn.commit()
        
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        conn.close()
        return render_template("category_setting.html", categories=categories)
    
    @app.route("/add", methods=["GET", "POST"])#データの一覧表示と絞り込み
    def add():
        conn = get_db()
        cur = conn.cursor()

        if request.method == "POST":
            user_name = request.form["user_name"]
            date = request.form["date"]
            amount = int(request.form["amount"])
            category = request.form["category"]
            type_val = request.form["type"]
            memo = request.form["memo"]
            cur.execute("""
                INSERT INTO records (user_name, date, amount, category, type, memo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_name, date, amount, category, type_val, memo))
            conn.commit()
            conn.close()
            return redirect("/") 

        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        if not users:
            conn.close()
            # 直接リダイレクト
            return redirect("/user_setting")
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        conn.close()
        return render_template("add.html", users=users, categories=categories)
    
    @app.route("/delete_category/<string:name>")#カテゴリ削除
    def delete_category(name):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        return redirect("/category_setting")