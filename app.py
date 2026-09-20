from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "travel-insurance-secret-key-2026"

DATABASE = "travel_insurance.db"


# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            destination TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            policy_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            claim_amount REAL NOT NULL,
            reason TEXT,
            claim_date TEXT,
            status TEXT DEFAULT 'Submitted',
            FOREIGN KEY(policy_id) REFERENCES policies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS renewals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            renewal_date TEXT,
            status TEXT DEFAULT 'Renewed',
            FOREIGN KEY(policy_id) REFERENCES policies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Add missing columns if old database exists
    columns = [row["name"] for row in cur.execute(
        "PRAGMA table_info(policies)"
    ).fetchall()]

    if "policy_amount" not in columns:
        cur.execute(
            "ALTER TABLE policies ADD COLUMN policy_amount REAL DEFAULT 0"
        )

    if "status" not in columns:
        cur.execute(
            "ALTER TABLE policies ADD COLUMN status TEXT DEFAULT 'Active'"
        )

    conn.commit()
    conn.close()


# ================= DESIGN =================

CSS = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #fff0f6, #fff4df);
    color: #333;
}

.navbar {
    background: linear-gradient(90deg, #ff4f81, #ff8a3d);
    color: white;
    padding: 18px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar h2 {
    margin: 0;
}

.navbar a {
    color: white;
    text-decoration: none;
    margin-left: 18px;
    font-weight: bold;
}

.container {
    width: 90%;
    max-width: 1000px;
    margin: 35px auto;
}

.card {
    background: white;
    padding: 30px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    margin-bottom: 25px;
}

h1, h2, h3 {
    color: #e83e70;
}

input, select, textarea {
    width: 100%;
    padding: 13px;
    margin: 8px 0 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 15px;
}

button, .btn {
    background: linear-gradient(90deg, #ff4f81, #ff8a3d);
    color: white;
    border: none;
    padding: 12px 22px;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin: 5px;
    font-weight: bold;
}

button:hover, .btn:hover {
    opacity: 0.9;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th {
    background: #ff668d;
    color: white;
    padding: 12px;
}

td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

.success {
    background: #e9fff0;
    border: 2px solid #42b96b;
    color: #176b36;
    padding: 18px;
    border-radius: 12px;
    margin: 20px 0;
}

.error {
    background: #fff0f0;
    border: 2px solid #e05252;
    color: #9b2020;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
}

.detail-box {
    background: #fff7fa;
    border-left: 5px solid #ff4f81;
    padding: 18px;
    margin: 10px 0;
    border-radius: 8px;
}

.detail-box p {
    margin: 8px 0;
}

.center {
    text-align: center;
}
</style>
"""


def page(title, content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {CSS}
    </head>

    <body>

    <div class="navbar">
        <h2>Travel Insurance</h2>

        <div>
            <a href="/">Home</a>

            {('<a href="/dashboard">Dashboard</a>'
              '<a href="/logout">Logout</a>')
             if 'user' in session else ''}
        </div>
    </div>

    <div class="container">
        {content}
    </div>

    </body>
    </html>
    """


# ================= HOME =================

@app.route("/")
def home():

    content = """
    <div class="card center">

        <h1>Travel Insurance Policy Issuance Platform</h1>

        <p>
            Welcome to our Travel Insurance Management System.
        </p>

        <p>
            Apply for travel insurance, manage your policies,
            submit claims and renew policies easily.
        </p>

        <br>

        <a class="btn" href="/register">Get Started</a>

        <a class="btn" href="/login">Login</a>

        <a class="btn" href="/register">Register</a>

    </div>
    """

    return page("Travel Insurance", content)


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not phone or not password:

            message = """
            <div class="error">
                Please fill all the fields.
            </div>
            """

        else:

            conn = get_db()

            try:

                hashed_password = generate_password_hash(password)

                conn.execute("""
                    INSERT INTO users
                    (name, email, phone, password)
                    VALUES (?, ?, ?, ?)
                """, (
                    name,
                    email,
                    phone,
                    hashed_password
                ))

                conn.commit()
                conn.close()

                return redirect(url_for("login"))

            except sqlite3.IntegrityError:

                conn.close()

                message = """
                <div class="error">
                    Email already registered.
                </div>
                """

    content = f"""
    <div class="card">

        <h1>Register</h1>

        {message}

        <form method="POST">

            <label>Name</label>
            <input type="text" name="name" required>

            <label>Email</label>
            <input type="email" name="email" required>

            <label>Phone</label>
            <input type="text" name="phone" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit">
                Register
            </button>

        </form>

        <p>
            Already have an account?
            <a href="/login">Login here</a>
        </p>

    </div>
    """

    return page("Register", content)


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = email
            session["user_id"] = user["id"]

            return redirect(url_for("dashboard"))

        else:

            message = """
            <div class="error">
                Invalid email or password.
            </div>
            """

    content = f"""
    <div class="card">

        <h1>Login</h1>

        {message}

        <form method="POST">

            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit">
                Login
            </button>

        </form>

        <p>
            New user?
            <a href="/register">Create an account</a>
        </p>

    </div>
    """

    return page("Login", content)


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    user = conn.execute("""
        SELECT * FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()

    conn.close()

    content = f"""
    <div class="card center">

        <h1>Travel Insurance Dashboard</h1>

        <h3>
            Welcome, {user["name"]}!
        </h3>

        <p>
            Manage your travel insurance policies from here.
        </p>

        <br>

        <a class="btn" href="/apply_policy">
            Apply for New Policy
        </a>

        <a class="btn" href="/view_policies">
            View My Policies
        </a>

        <a class="btn" href="/claim">
            Claim Insurance
        </a>

        <a class="btn" href="/renewal">
            Policy Renewal
        </a>

    </div>
    """

    return page("Dashboard", content)


# ================= APPLY POLICY =================

@app.route("/apply_policy", methods=["GET", "POST"])
def apply_policy():

    if "user" not in session:
        return redirect(url_for("login"))

    message = ""
    policy_details = ""

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        destination = request.form.get("destination", "").strip()
        travel_date = request.form.get("travel_date", "").strip()
        policy_amount = request.form.get("policy_amount", "").strip()

        if not name or not destination or not travel_date or not policy_amount:

            message = """
            <div class="error">
                Please fill all fields.
            </div>
            """

        else:

            try:
                amount = float(policy_amount)

                if amount <= 0:
                    raise ValueError

                conn = get_db()

                cur = conn.execute("""
                    INSERT INTO policies
                    (
                        user_id,
                        name,
                        destination,
                        travel_date,
                        policy_amount,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session["user_id"],
                    name,
                    destination,
                    travel_date,
                    amount,
                    "Active"
                ))

                policy_id = cur.lastrowid

                conn.commit()
                conn.close()

                policy_details = f"""
                <div class="success">
                    <h2>Policy Applied Successfully!</h2>
                    <p>Your policy has been stored successfully.</p>
                </div>

                <div class="detail-box">
                    <p><b>Policy ID:</b> {policy_id}</p>
                    <p><b>Name:</b> {name}</p>
                    <p><b>Destination:</b> {destination}</p>
                    <p><b>Travel Date:</b> {travel_date}</p>
                    <p><b>Policy Amount:</b> ₹{amount:.2f}</p>
                    <p><b>Status:</b> Active</p>
                </div>

                <a class="btn" href="/view_policies">
                    View My Policies
                </a>
                """

            except ValueError:

                message = """
                <div class="error">
                    Please enter a valid policy amount.
                </div>
                """

    content = f"""
    <div class="card">

        <h1>Apply for New Policy</h1>

        {message}

        {policy_details}

        <form method="POST">

            <label>Name</label>
            <input
                type="text"
                name="name"
                required
            >

            <label>Destination</label>
            <input
                type="text"
                name="destination"
                required
            >

            <label>Travel Date</label>
            <input
                type="date"
                name="travel_date"
                required
            >

            <label>Policy Amount</label>
            <input
                type="number"
                name="policy_amount"
                min="1"
                step="0.01"
                required
            >

            <button type="submit">
                Apply Policy
            </button>

        </form>

        <br>

        <a class="btn" href="/dashboard">
            Back to Dashboard
        </a>

    </div>
    """

    return page("Apply Policy", content)
# ================= VIEW POLICIES =================

@app.route("/view_policies")
def view_policies():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    policies = conn.execute("""
        SELECT *
        FROM policies
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    rows = ""

    for policy in policies:

        rows += f"""
        <tr>
            <td>{policy["id"]}</td>
            <td>{policy["name"]}</td>
            <td>{policy["destination"]}</td>
            <td>{policy["travel_date"]}</td>
            <td>₹{float(policy["policy_amount"]):.2f}</td>
            <td>{policy["status"]}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="6">
                No policies found.
            </td>
        </tr>
        """

    content = f"""
    <div class="card">

        <h1>My Travel Policies</h1>

        <table>

            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Destination</th>
                <th>Travel Date</th>
                <th>Policy Amount</th>
                <th>Status</th>
            </tr>

            {rows}

        </table>

        <br>

        <a class="btn" href="/dashboard">
            Back to Dashboard
        </a>

    </div>
    """

    return page("My Policies", content)


# ================= CLAIM =================

@app.route("/claim", methods=["GET", "POST"])
def claim():

    if "user" not in session:
        return redirect(url_for("login"))

    message = ""
    claim_details = ""

    conn = get_db()

    policies = conn.execute("""
        SELECT *
        FROM policies
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    if request.method == "POST":

        policy_id = request.form.get("policy_id", "").strip()
        claim_amount = request.form.get("claim_amount", "").strip()
        reason = request.form.get("reason", "").strip()

        if not policy_id or not claim_amount or not reason:

            message = """
            <div class="error">
                Please fill all claim details.
            </div>
            """

        else:

            try:

                amount = float(claim_amount)

                if amount <= 0:
                    raise ValueError

                conn = get_db()

                policy = conn.execute("""
                    SELECT *
                    FROM policies
                    WHERE id = ?
                    AND user_id = ?
                """, (
                    policy_id,
                    session["user_id"]
                )).fetchone()

                if not policy:

                    conn.close()

                    message = """
                    <div class="error">
                        Invalid policy selected.
                    </div>
                    """

                elif amount > float(policy["policy_amount"]):

                    conn.close()

                    message = f"""
                    <div class="error">
                        Claim amount cannot be greater than
                        the policy amount of
                        ₹{float(policy["policy_amount"]):.2f}.
                    </div>
                    """

                else:

                    claim_date = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    cur = conn.execute("""
                        INSERT INTO claims
                        (
                            policy_id,
                            user_id,
                            claim_amount,
                            reason,
                            claim_date,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        policy["id"],
                        session["user_id"],
                        amount,
                        reason,
                        claim_date,
                        "Submitted"
                    ))

                    claim_id = cur.lastrowid

                    conn.commit()
                    conn.close()

                    claim_details = f"""
                    <div class="success">
                        <h2>Claim Successful!</h2>
                        <p>
                            Your insurance claim has been
                            submitted successfully.
                        </p>
                    </div>

                    <div class="detail-box">

                        <p>
                            <b>Claim ID:</b>
                            {claim_id}
                        </p>

                        <p>
                            <b>Policy ID:</b>
                            {policy["id"]}
                        </p>

                        <p>
                            <b>Policy Holder:</b>
                            {policy["name"]}
                        </p>

                        <p>
                            <b>Destination:</b>
                            {policy["destination"]}
                        </p>

                        <p>
                            <b>Travel Date:</b>
                            {policy["travel_date"]}
                        </p>

                        <p>
                            <b>Policy Amount:</b>
                            ₹{float(policy["policy_amount"]):.2f}
                        </p>

                        <p>
                            <b>Claim Amount:</b>
                            ₹{amount:.2f}
                        </p>

                        <p>
                            <b>Reason:</b>
                            {reason}
                        </p>

                        <p>
                            <b>Claim Date:</b>
                            {claim_date}
                        </p>

                        <p>
                            <b>Status:</b>
                            Submitted
                        </p>

                    </div>
                    """

            except ValueError:

                message = """
                <div class="error">
                    Please enter a valid claim amount.
                </div>
                """

    options = ""

    for policy in policies:

        options += f"""
        <option value="{policy["id"]}">
            Policy {policy["id"]} -
            {policy["destination"]} -
            ₹{float(policy["policy_amount"]):.2f}
        </option>
        """

    if not options:

        options = """
        <option value="">
            No policies available
        </option>
        """

    content = f"""
    <div class="card">

        <h1>Claim Insurance</h1>

        {message}

        {claim_details}

        <form method="POST">

            <label>Select Policy</label>

            <select name="policy_id" required>
                {options}
            </select>

            <label>Claim Amount</label>

            <input
                type="number"
                name="claim_amount"
                min="1"
                step="0.01"
                required
            >

            <label>Claim Reason</label>

            <textarea
                name="reason"
                rows="4"
                required
                placeholder="Enter claim reason"
            ></textarea>

            <button type="submit">
                Submit Claim
            </button>

        </form>

        <br>

        <a class="btn" href="/dashboard">
            Back to Dashboard
        </a>

    </div>
    """

    return page("Claim Insurance", content)


# ================= RENEWAL =================

@app.route("/renewal", methods=["GET", "POST"])
def renewal():

    if "user" not in session:
        return redirect(url_for("login"))

    message = ""
    renewal_details = ""

    conn = get_db()

    policies = conn.execute("""
        SELECT *
        FROM policies
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    if request.method == "POST":

        policy_id = request.form.get("policy_id", "").strip()
        renewal_date = request.form.get("renewal_date", "").strip()

        if not policy_id or not renewal_date:

            message = """
            <div class="error">
                Please select a policy and renewal date.
            </div>
            """

        else:

            conn = get_db()

            policy = conn.execute("""
                SELECT *
                FROM policies
                WHERE id = ?
                AND user_id = ?
            """, (
                policy_id,
                session["user_id"]
            )).fetchone()

            if not policy:

                conn.close()

                message = """
                <div class="error">
                    Invalid policy selected.
                </div>
                """

            else:

                cur = conn.execute("""
                    INSERT INTO renewals
                    (
                        policy_id,
                        user_id,
                        renewal_date,
                        status
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    policy["id"],
                    session["user_id"],
                    renewal_date,
                    "Renewed"
                ))

                renewal_id = cur.lastrowid

                conn.execute("""
                    UPDATE policies
                    SET status = ?
                    WHERE id = ?
                """, (
                    "Renewed",
                    policy["id"]
                ))

                conn.commit()
                conn.close()

                renewal_details = f"""
                <div class="success">

                    <h2>Policy Renewal Successful!</h2>

                    <p>
                        Your policy has been renewed successfully.
                    </p>

                </div>

                <div class="detail-box">

                    <p>
                        <b>Renewal ID:</b>
                        {renewal_id}
                    </p>

                    <p>
                        <b>Policy ID:</b>
                        {policy["id"]}
                    </p>

                    <p>
                        <b>Policy Holder:</b>
                        {policy["name"]}
                    </p>

                    <p>
                        <b>Destination:</b>
                        {policy["destination"]}
                    </p>

                    <p>
                        <b>Original Travel Date:</b>
                        {policy["travel_date"]}
                    </p>

                    <p>
                        <b>Policy Amount:</b>
                        ₹{float(policy["policy_amount"]):.2f}
                    </p>

                    <p>
                        <b>Renewal Date:</b>
                        {renewal_date}
                    </p>

                    <p>
                        <b>Renewal Status:</b>
                        Renewed
                    </p>

                </div>
                """

    options = ""

    for policy in policies:

        options += f"""
        <option value="{policy["id"]}">
            Policy {policy["id"]} -
            {policy["destination"]}
        </option>
        """

    if not options:

        options = """
        <option value="">
            No policies available
        </option>
        """

    content = f"""
    <div class="card">

        <h1>Policy Renewal</h1>

        {message}

        {renewal_details}

        <form method="POST">

            <label>Select Policy</label>

            <select name="policy_id" required>
                {options}
            </select>

            <label>Renewal Date</label>

            <input
                type="date"
                name="renewal_date"
                required
            >

            <button type="submit">
                Renew Policy
            </button>

        </form>

        <br>

        <a class="btn" href="/dashboard">
            Back to Dashboard
        </a>

    </div>
    """

    return page("Policy Renewal", content)


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ================= RUN =================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )