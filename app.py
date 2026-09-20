from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "travelinsurance123"

DATABASE = "travel_insurance.db"


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================
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

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect(url_for("dashboard"))

        return """
        <h2 style="text-align:center;margin-top:100px;color:red;">
            Login Failed
        </h2>
        <p style="text-align:center;">
            <a href="/login">Try Again</a>
        </p>
        """

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =========================
# APPLY POLICY
# =========================
@app.route("/apply_policy", methods=["GET", "POST"])
def apply_policy():

    if request.method == "POST":

        name = request.form.get("name")
        destination = request.form.get("destination")
        travel_date = request.form.get("travel_date")
        days = int(request.form.get("days"))

        premium = days * 100

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO policies
            (name, destination, travel_date)
            VALUES (?, ?, ?)
            """,
            (name, destination, travel_date)
        )

        conn.commit()
        conn.close()

        return f"""
<!DOCTYPE html>
<html>
<head>

    <title>Travel Sync - Policy Success</title>

    <style>

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}

        body {{
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;

            background:
            linear-gradient(
                135deg,
                #00c6ff,
                #0072ff,
                #7b2ff7
            );
        }}

        .box {{
            width: 450px;
            padding: 45px;

            text-align: center;

            background: white;

            border-radius: 25px;

            box-shadow:
            0 15px 40px
            rgba(0,0,0,0.3);
        }}

        .icon {{
            font-size: 60px;
            margin-bottom: 15px;
        }}

        h2 {{
            color: #16a085;
            margin-bottom: 25px;
        }}

        p {{
            color: #444;
            font-size: 17px;
            margin: 12px;
        }}

        .back {{
            display: inline-block;

            margin-top: 25px;

            padding: 13px 28px;

            background:
            linear-gradient(
                90deg,
                #0072ff,
                #7b2ff7
            );

            color: white;

            text-decoration: none;

            border-radius: 25px;

            font-weight: bold;
        }}

    </style>

</head>

<body>

<div class="box">

    <div class="icon">✅✈️</div>

    <h2>Policy Applied Successfully!</h2>

    <p><b>Name:</b> {name}</p>

    <p><b>Destination:</b> {destination}</p>

    <p><b>Travel Date:</b> {travel_date}</p>

    <p><b>Duration:</b> {days} Days</p>

    <p><b>Premium Amount:</b> ₹{premium}</p>

    <a class="back" href="/dashboard">
        ← Back to Dashboard
    </a>

</div>

</body>
</html>
"""

    return render_template("apply_policy.html")


# =========================
# VIEW POLICIES
# =========================
@app.route("/view_policies")
def view_policies():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM policies")

    policies = cursor.fetchall()

    conn.close()

    return render_template(
        "view_policies.html",
        policies=policies
    )


# =========================
# CLAIM
# =========================
@app.route("/claim", methods=["GET", "POST"])
def claim():

    if request.method == "POST":

        policy_id = request.form.get("policy_id")
        claim_reason = request.form.get("claim_reason")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO claims
            (policy_id, claim_reason)
            VALUES (?, ?)
            """,
            (policy_id, claim_reason)
        )

        conn.commit()
        conn.close()

        return render_template("claim.html")

    return render_template("claim.html")


# =========================
# RENEWAL
# =========================
@app.route("/renewal", methods=["GET", "POST"])
def renewal():

    if request.method == "POST":

        policy_id = request.form.get("policy_id")

        return f"""
<!DOCTYPE html>
<html>

<head>

    <title>Travel Sync - Renewal Success</title>

    <style>

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}

        body {{
            min-height: 100vh;

            display: flex;
            justify-content: center;
            align-items: center;

            background:
            linear-gradient(
                135deg,
                #00b09b,
                #96c93d,
                #00c6ff
            );
        }}

        .box {{
            width: 450px;

            padding: 45px;

            text-align: center;

            background:
            rgba(255,255,255,0.97);

            border-radius: 25px;

            box-shadow:
            0 15px 40px
            rgba(0,0,0,0.3);
        }}

        .icon {{
            font-size: 65px;

            margin-bottom: 18px;
        }}

        h2 {{
            color: #159957;

            margin-bottom: 20px;
        }}

        p {{
            color: #555;

            font-size: 17px;

            line-height: 1.6;

            margin-bottom: 15px;
        }}

        .policy {{
            font-weight: bold;

            color: #159957;

            margin-bottom: 25px;
        }}

        .back {{
            display: inline-block;

            padding: 13px 28px;

            background:
            linear-gradient(
                90deg,
                #00b09b,
                #96c93d
            );

            color: white;

            text-decoration: none;

            border-radius: 25px;

            font-weight: bold;
        }}

        .back:hover {{
            transform: scale(1.05);
        }}

    </style>

</head>

<body>

<div class="box">

    <div class="icon">🔄✅</div>

    <h2>
        Policy Renewal Request Submitted!
    </h2>

    <p>
        Your policy renewal request has been
        submitted successfully.
    </p>

    <p class="policy">
        Policy ID: {policy_id}
    </p>

    <a class="back" href="/dashboard">
        ← Back to Dashboard
    </a>

</div>

</body>

</html>
"""

    return render_template("renewal.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))


# =========================
# ADMIN LOGIN
# =========================
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            return redirect(
                url_for("admin_dashboard")
            )

        return """
        <h2 style="text-align:center;margin-top:100px;color:red;">
            Invalid Admin Login
        </h2>

        <p style="text-align:center;">
            <a href="/admin_login">Try Again</a>
        </p>
        """

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin_dashboard")
def admin_dashboard():

    return render_template(
        "admin_dashboard.html"
    )


# =========================
# USERS
# =========================
@app.route("/users")
def users():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "users.html",
        users=users
    )


# =========================
# CLAIMS
# =========================
@app.route("/claims")
def claims():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM claims")

    claims = cursor.fetchall()

    conn.close()

    return render_template(
        "claims.html",
        claims=claims
    )


# =========================
# RUN APPLICATION
# =========================
if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False
    )