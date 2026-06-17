<div align="center">

# 🎓 SkripsiEngineer

### Platform Bimbingan Skripsi Teknik & Teknologi

Aplikasi web untuk menghubungkan mahasiswa teknik dengan mentor — dari pengajuan bimbingan, persetujuan jadwal & harga, pembayaran, hingga selesai.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success)

</div>

---

## ✨ Fitur Utama

### 🌐 Landing Page
- Desain modern bersih (light theme) dengan aksen biru, animasi scroll & counter
- Bidang bimbingan (Elektro, IT, Data Science, Sipil, Mesin, Kimia, dll.)
- Paket harga **Basic / Pro / Premium** + paket **Custom** (proyek end-to-end, harga nego)
- Form pengajuan kelas langsung dari landing page

### 👩‍🎓 Dashboard Klien
- Ajukan bimbingan: pilih bidang, paket, deskripsi, & tanggal yang diinginkan
- Pantau status tiap pengajuan dengan **progress bar** bertahap
- Lihat **jadwal final**, **harga**, dan catatan dari admin
- **Pembayaran** dengan modal transfer bank (kartu rekening BRI) + notifikasi toast

### 🛠️ Dashboard Admin
- Ringkasan statistik: total pengajuan, perlu direview, menunggu konfirmasi, total pemasukan
- **Kelola semua pengajuan**: Setujui (tetapkan jadwal + harga), Tolak (dengan alasan), ubah status
- Tombol **Detail** untuk melihat info lengkap & deskripsi pengajuan
- **Manajemen user**: daftar semua pengguna + role + jumlah pengajuan
- Konfirmasi pembayaran sebelum bimbingan dimulai

---

## 🔄 Alur Pengajuan (Status)

```
Pending ──┬──► Rejected            (admin tolak + alasan)
          │
          └──► Approved ──► Confirming ──► Paid ──► Ongoing ──► Completed
            (admin set       (klien      (admin     (admin       (admin
             jadwal+harga)    bayar)      konfirmasi) mulai)      selesai)
```

| Status | Arti |
|---|---|
| `Pending` | Baru diajukan, menunggu review admin |
| `Approved` | Disetujui — jadwal & harga ditetapkan, menunggu pembayaran |
| `Confirming` | Klien sudah bayar, menunggu konfirmasi admin |
| `Paid` | Pembayaran dikonfirmasi (lunas) |
| `Ongoing` | Bimbingan/proyek berjalan |
| `Completed` | Selesai |
| `Rejected` | Ditolak admin |

---

## 🧰 Tech Stack

| Lapisan | Teknologi |
|---|---|
| Backend | Python **Flask** |
| Database | **SQLite3** (tanpa setup tambahan) |
| Auth | Flask session + Werkzeug `pbkdf2:sha256` |
| Frontend | HTML, CSS murni (custom), JavaScript vanilla |
| Ikon & Font | Lucide Icons, Google Fonts (Outfit & Inter) |

---

## 📁 Struktur Proyek

```text
bimbel_skripsi_web/
├── app.py                      # Routes & API (auth, dashboard, admin, payment)
├── db.py                       # Koneksi SQLite, skema, migrasi, & helper query
├── requirements.txt
├── database.db                 # Dibuat otomatis saat run (jangan di-commit)
│
├── static/
│   ├── css/style.css           # Seluruh styling (light theme)
│   ├── js/main.js              # Interaksi landing page
│   └── images/hero_study.jpg
│
├── templates/
│   ├── base.html               # Navbar, footer, layout dasar
│   ├── index.html              # Landing page
│   ├── login.html / register.html
│   ├── dashboard.html          # Dashboard klien
│   └── dashboard_admin.html    # Dashboard admin
│
└── docs: design.md · plan.md · flow.md
```

---

## 🚀 Cara Menjalankan

### 1. Prasyarat
- Python **3.9+**

### 2. Install dependency
```bash
# (opsional tapi disarankan) buat virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Jalankan server
```bash
python3 app.py
```
Buka **http://127.0.0.1:5001** di browser. Database `database.db` dibuat otomatis pada run pertama.

---

## 🔑 Membuat Akun Admin

Akun yang mendaftar dengan email **`ADMIN_EMAIL`** otomatis menjadi admin.

1. Buka aplikasi → **Daftar**
2. Gunakan email admin (default sudah diset di `app.py`)
3. Setelah login, kamu langsung masuk **Dashboard Admin**

User lain yang mendaftar akan menjadi klien biasa.

---

## ⚙️ Konfigurasi (Environment Variables)

Semua opsional — ada nilai default.

| Variabel | Default | Fungsi |
|---|---|---|
| `SECRET_KEY` | `skripsiengineer-dev-secret-key` | Kunci sesi Flask (ganti di produksi) |
| `ADMIN_EMAIL` | email admin di `app.py` | Email yang otomatis jadi admin |
| `DATABASE_PATH` | `./database.db` | Lokasi file database |
| `PORT` | `5001` | Port server |

Contoh:
```bash
ADMIN_EMAIL="admin@email.com" PORT=8000 python3 app.py
```

---

## 🔌 Ringkasan API

| Method | Endpoint | Akses | Fungsi |
|---|---|---|---|
| `POST` | `/api/requests` | Klien | Ajukan bimbingan |
| `GET` | `/api/requests` | Klien | Daftar pengajuan sendiri |
| `POST` | `/api/requests/<id>/pay` | Klien | Bayar (→ menunggu konfirmasi) |
| `GET` | `/api/admin/requests` | Admin | Semua pengajuan |
| `POST` | `/api/admin/requests/<id>/approve` | Admin | Setujui + jadwal & harga |
| `POST` | `/api/admin/requests/<id>/reject` | Admin | Tolak + alasan |
| `POST` | `/api/admin/requests/<id>/status` | Admin | Ubah status (Paid/Ongoing/Completed) |
| `GET` | `/api/admin/users` | Admin | Daftar semua user |

---

## 🗄️ Skema Database

**users** — `id`, `username`, `email`, `password_hash`, `phone`, `major`, `role`, `created_at`
**requests** — `id`, `user_id`, `field`, `package`, `description`, `status`, `preferred_date`, `scheduled_date`, `price`, `admin_note`, `created_at`

---

## 📝 Catatan

- Pembayaran **disimulasikan** (tanpa payment gateway) — cocok untuk demo/skripsi.
- Untuk mereset data, hentikan server lalu hapus `database.db` (tabel dibuat ulang otomatis).
- Tambahkan `database.db` ke `.gitignore` agar data lokal tidak ikut ter-commit.

---

<div align="center">
Dibuat dengan ❤️ untuk membantu mahasiswa teknik menyelesaikan skripsi.
</div>
