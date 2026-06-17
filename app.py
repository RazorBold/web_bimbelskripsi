"""SkripsiEngineer - Flask application.

Page routes (landing, auth, dashboards) and JSON APIs for bimbingan requests,
plus admin management (approve/reject/schedule/status) and a simulated payment.
"""
import os
import re
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skripsiengineer-dev-secret-key")

# The account using this email is automatically treated as admin.
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "muhammad.syaiful250198@gmail.com").lower()

db.init_db()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 6
# pbkdf2 is available on every Python build; scrypt (Werkzeug's default) needs
# OpenSSL scrypt support, which is missing on some interpreters (e.g. py3.9).
PASSWORD_HASH_METHOD = "pbkdf2:sha256"

PACKAGE_PRICES = {"Basic": 149000, "Pro": 249000, "Premium": 349000, "Custom": None}
# Statuses an admin may set directly via the status endpoint.
ADMIN_SETTABLE_STATUSES = {"Paid", "Ongoing", "Completed"}


# ---------------------------------------------------------------------------
# Helpers & decorators
# ---------------------------------------------------------------------------
def current_user():
    uid = session.get("user_id")
    return db.get_user_by_id(uid) if uid else None


def role_for(email):
    return "admin" if email.lower() == ADMIN_EMAIL else "user"


def start_session(user):
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan masuk terlebih dahulu.", "info")
            return redirect(url_for("login"))
        # Guard against stale sessions (user no longer exists in the DB).
        if current_user() is None:
            session.clear()
            flash("Sesi tidak valid, silakan masuk kembali.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session or current_user() is None:
            session.clear()
            return jsonify(status="error", message="Unauthorized"), 401
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """JSON-API guard: only admins may proceed."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify(status="error", message="Unauthorized"), 401
        if session.get("role") != "admin":
            return jsonify(status="error", message="Akses khusus admin"), 403
        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Harap isi semua kolom.", "danger")
            return render_template("login.html")

        user = db.get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            # Keep the designated admin account in the admin role.
            desired = role_for(email)
            if user["role"] != desired:
                db.set_user_role(user["id"], desired)
                user = db.get_user_by_id(user["id"])
            start_session(user)
            return redirect(url_for("dashboard"))

        flash("Email atau password salah.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        phone = (request.form.get("phone") or "").strip()
        major = (request.form.get("major") or "").strip()

        if not all([username, email, password, phone, major]):
            flash("Harap isi semua kolom.", "danger")
            return render_template("register.html")
        if not EMAIL_RE.match(email):
            flash("Format email tidak valid.", "danger")
            return render_template("register.html")
        if len(password) < MIN_PASSWORD_LEN:
            flash(f"Password minimal {MIN_PASSWORD_LEN} karakter.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password, method=PASSWORD_HASH_METHOD)
        user_id = db.create_user(
            username, email, password_hash, phone, major, role=role_for(email)
        )

        if user_id:
            start_session(db.get_user_by_id(user_id))
            flash("Pendaftaran berhasil! Selamat datang.", "success")
            return redirect(url_for("dashboard"))

        flash("Email atau Username sudah terdaftar.", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user["role"] == "admin":
        all_requests = db.get_all_requests()
        paid_statuses = {"Paid", "Ongoing", "Completed"}
        stats = {
            "total": len(all_requests),
            "pending": sum(1 for r in all_requests if r["status"] == "Pending"),
            "confirming": sum(1 for r in all_requests if r["status"] == "Confirming"),
            "ongoing": sum(1 for r in all_requests if r["status"] == "Ongoing"),
            "revenue": sum(
                (r["price"] or 0) for r in all_requests if r["status"] in paid_statuses
            ),
        }
        return render_template(
            "dashboard_admin.html",
            user=user,
            requests=all_requests,
            users=db.get_all_users(),
            stats=stats,
        )
    return render_template(
        "dashboard.html", user=user, requests=db.get_requests_by_user(user["id"])
    )


# ---------------------------------------------------------------------------
# User JSON API
# ---------------------------------------------------------------------------
@app.route("/api/requests", methods=["POST"])
@api_login_required
def submit_request():
    data = request.get_json(silent=True) or {}
    field = (data.get("field") or "").strip()
    package = (data.get("package") or "").strip()
    description = (data.get("description") or "").strip()
    preferred_date = (data.get("preferred_date") or "").strip() or None

    if not all([field, package, description]):
        return jsonify(status="error", message="Data tidak lengkap."), 400

    req_id = db.create_request(
        session["user_id"], field, package, description, preferred_date
    )
    return jsonify(
        status="success",
        message="Permintaan bimbingan berhasil diajukan!",
        request_id=req_id,
    )


@app.route("/api/requests", methods=["GET"])
@api_login_required
def get_requests():
    return jsonify(status="success", requests=db.get_requests_by_user(session["user_id"]))


@app.route("/api/requests/<int:req_id>/pay", methods=["POST"])
@api_login_required
def pay_request(req_id):
    req = db.get_request_by_id(req_id)
    if req is None or req["user_id"] != session["user_id"]:
        return jsonify(status="error", message="Pengajuan tidak ditemukan."), 404
    if req["status"] != "Approved":
        return jsonify(status="error", message="Pengajuan belum bisa dibayar."), 400

    db.update_request_status(req_id, "Confirming")
    return jsonify(status="success", message="Pembayaran dikirim, menunggu konfirmasi admin.")


# ---------------------------------------------------------------------------
# Admin JSON API
# ---------------------------------------------------------------------------
@app.route("/api/admin/requests", methods=["GET"])
@admin_required
def admin_list_requests():
    return jsonify(status="success", requests=db.get_all_requests())


@app.route("/api/admin/requests/<int:req_id>/approve", methods=["POST"])
@admin_required
def admin_approve(req_id):
    if db.get_request_by_id(req_id) is None:
        return jsonify(status="error", message="Pengajuan tidak ditemukan."), 404

    data = request.get_json(silent=True) or {}
    scheduled_date = (data.get("scheduled_date") or "").strip()
    note = (data.get("note") or "").strip() or None
    raw_price = data.get("price")

    if not scheduled_date:
        return jsonify(status="error", message="Jadwal wajib diisi."), 400
    try:
        price = int(raw_price)
        if price <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(status="error", message="Harga harus berupa angka."), 400

    db.approve_request(req_id, scheduled_date, price, note)
    return jsonify(status="success", message="Pengajuan disetujui.")


@app.route("/api/admin/requests/<int:req_id>/reject", methods=["POST"])
@admin_required
def admin_reject(req_id):
    if db.get_request_by_id(req_id) is None:
        return jsonify(status="error", message="Pengajuan tidak ditemukan."), 404

    data = request.get_json(silent=True) or {}
    note = (data.get("note") or "").strip() or None
    db.reject_request(req_id, note)
    return jsonify(status="success", message="Pengajuan ditolak.")


@app.route("/api/admin/requests/<int:req_id>/status", methods=["POST"])
@admin_required
def admin_set_status(req_id):
    if db.get_request_by_id(req_id) is None:
        return jsonify(status="error", message="Pengajuan tidak ditemukan."), 404

    data = request.get_json(silent=True) or {}
    new_status = (data.get("status") or "").strip()
    if new_status not in ADMIN_SETTABLE_STATUSES:
        return jsonify(status="error", message="Status tidak valid."), 400

    db.update_request_status(req_id, new_status)
    return jsonify(status="success", message=f"Status diubah ke {new_status}.")


@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_list_users():
    return jsonify(status="success", users=db.get_all_users())


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
