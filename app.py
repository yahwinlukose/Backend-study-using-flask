from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"   # needed for flash messages


# -------------------------
# DATABASE HELPER FUNCTION
# -------------------------
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# ROUTES
# -------------------------

# HOME → LOGIN PAGE
@app.route("/")
def login_page():
    return render_template("index.html")


# LOGIN HANDLER
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()

    if user:
        return f"<h1>Login Successful — Welcome, {username}!</h1>"
    else:
        flash("❌ Invalid username or password")
        return redirect(url_for("login_page"))


# SIGNUP PAGE
@app.route("/signup")
def signup_page():
    return render_template("signup.html")


# SIGNUP HANDLER
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()

    # check if user already exists
    existing = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing:
        conn.close()
        flash("⚠ Username already taken!")
        return redirect(url_for("signup_page"))

    # insert new user
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    conn.close()

    flash("✅ Account created successfully! Please login.")
    return redirect(url_for("login_page"))


# FORGOT PASSWORD PAGE
@app.route("/forgot")
def forgot_page():
    return render_template("forgot.html")


# FORGOT PASSWORD HANDLER (Basic)
@app.route("/reset", methods=["POST"])
def reset():
    username = request.form["username"]
    newpass = request.form["new_password"]

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user:
        conn.close()
        flash("❌ User not found!")
        return redirect(url_for("forgot_page"))

    # update password
    conn.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (newpass, username)
    )
    conn.commit()
    conn.close()

    flash("✅ Password updated successfully!")
    return redirect(url_for("login_page"))


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
