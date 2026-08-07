from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "travelinsurance123"

DATABASE = "travel_insurance.db"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
            (name, email, phone, password)
        )

        conn.commit()
        conn.close()

        print("User Saved Successfully")

        return render_template("login.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("travel_insurance.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        print(user)

        conn.close()

        if user:
            session["user"] = email
            return render_template("dashboard.html")
        else:
            return "Login Failed"

    return render_template("login.html")

@app.route("/apply_policy", methods=["GET", "POST"])
def apply_policy():

    if request.method == "POST":

        name = request.form.get("name")
        destination = request.form.get("destination")
        travel_date = request.form.get("travel_date")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO policies (name, destination, travel_date) VALUES (?, ?, ?)",
            (name, destination, travel_date)
        )

        conn.commit()
        conn.close()

        return render_template("dashboard.html")

    return render_template("apply_policy.html")
@app.route("/view_policies")
def view_policies():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM policies")
    policies = cursor.fetchall()

    conn.close()

    return render_template("view_policies.html", policies=policies)
@app.route("/claim")
def claim():
    return render_template("claim.html")
@app.route('/renewal', methods=['GET','POST'])
def renewal():

    if request.method == "POST":

        policy_id = request.form['policy_id']

        return "Policy Renewal Request Submitted Successfully"

    return render_template("renewal.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")
@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            return render_template("admin_dashboard.html")

        else:
            return "Invalid Admin Login"

    return render_template("admin_login.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")
@app.route('/users')
def users():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("users.html", users=users)
@app.route('/claims')
def claims():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM claims")
    claims = cursor.fetchall()

    conn.close()
    return render_template("claims.html", claims=claims)
if __name__ == "__main__":
    app.run(debug=True)