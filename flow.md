# Flow & Plan — Role Admin + Approval + Penjadwalan + Pembayaran
**Project**: SkripsiEngineer
**Status dokumen**: ✅ SUDAH DIIMPLEMENTASI (Fase A–D selesai & teruji end-to-end).

> Tujuan: Menambah **role admin** (kamu) yang punya dashboard berbeda untuk **mengelola semua pengajuan**, **menyetujui/menolak**, **menetapkan jadwal & harga**, lalu klien **membayar** jika deal. Klien tetap pakai dashboard biasa untuk mengajukan & memantau.

---

## 1. Konsep Peran (Role)

| Role | Siapa | Akses |
|---|---|---|
| `user` (default) | Mahasiswa/klien | Ajukan bimbingan, pilih tanggal preferensi, lihat status, bayar |
| `admin` | **Kamu** | Lihat SEMUA pengajuan, setujui/tolak, set jadwal + harga, kelola user, ubah status |

**Cara menentukan admin (DIPUTUSKAN: otomatis via email):**
- Tambah kolom `role` di tabel `users` (default `'user'`).
- Set satu **`ADMIN_EMAIL`** di config `app.py` (default: email kamu). Saat email itu login/register, otomatis `role = 'admin'`.

Routing dibedakan di endpoint `/dashboard`:
```
if user.role == 'admin'  -> render dashboard_admin.html
else                     -> render dashboard.html (yang sekarang)
```

---

## 2. Perubahan Database

### 2.1 Tabel `users` — tambah 1 kolom
| Kolom | Tipe | Default | Keterangan |
|---|---|---|---|
| `role` | TEXT | `'user'` | `'user'` atau `'admin'` |

### 2.2 Tabel `requests` — tambah beberapa kolom
| Kolom | Tipe | Default | Keterangan |
|---|---|---|---|
| `preferred_date` | TEXT | NULL | Tanggal yang DIINGINKAN klien saat mengajukan |
| `scheduled_date` | TEXT | NULL | Jadwal FINAL yang ditetapkan admin |
| `price` | INTEGER | NULL | Harga final (penting untuk paket **Custom** hasil nego) |
| `admin_note` | TEXT | NULL | Catatan admin / alasan penolakan |

> Catatan: `CREATE TABLE IF NOT EXISTS` tidak mengubah tabel lama. Untuk DB yang sudah ada, kita pakai migrasi ringan (`ALTER TABLE ... ADD COLUMN`) atau cukup hapus `database.db` (data tes) supaya dibuat ulang. Akan ditangani di implementasi.

---

## 3. Status Pengajuan (State Machine)

Status diperluas dari yang sekarang. Alur lengkap (DIPUTUSKAN: ada konfirmasi admin setelah klien bayar):

```
                    [Tolak + alasan]
                  ┌────────────────────► Rejected (selesai, ditolak)
                  │
  Pending ────────┤
 (klien ajukan)   │  [Setujui: set jadwal + harga]
                  └───────────────────► Approved ──[klien Bayar]──► Confirming
                                        (tunggu bayar)              (tunggu konfirmasi admin)
                                                                          │ [admin konfirmasi bayar]
                                                                          ▼
                                                                        Paid ──[admin mulai]──► Ongoing ──[admin selesai]──► Completed
```

| Status (nilai di DB) | Tampilan | Arti | Siapa yang mengubah |
|---|---|---|---|
| `Pending` | Menunggu Review | Baru diajukan | otomatis saat klien submit |
| `Rejected` | Ditolak | Ditolak admin + alasan | Admin |
| `Approved` | Disetujui · Tunggu Bayar | Jadwal & harga ditetapkan | Admin |
| `Confirming` | Menunggu Konfirmasi | Klien sudah klik Bayar, menunggu verifikasi admin | Klien (Bayar) |
| `Paid` | Lunas | Pembayaran dikonfirmasi admin | Admin (konfirmasi) |
| `Ongoing` | Berjalan | Bimbingan/proyek berjalan | Admin |
| `Completed` | Selesai | Selesai | Admin |

> Nilai status disimpan tanpa spasi (mis. `Confirming`) agar aman dipakai sebagai CSS class (`status-confirming`); teks tampilan Indonesia diatur di template.

Progress bar dashboard klien: Pending 15% · Approved 35% · Confirming 55% · Paid 70% · Ongoing 85% · Completed 100% · Rejected (merah, 0%).

---

## 4. Alur Klien (User)

1. **Register / Login** seperti sekarang.
2. **Ajukan Bimbingan** (dashboard atau landing form) — sekarang ditambah field **"Tanggal yang diinginkan"** (`preferred_date`). Untuk paket **Custom**, deskripsikan scope (mau apa & sampai mana).
3. Status awal → **Pending**. Klien lihat: *"Menunggu persetujuan admin."*
4. Setelah admin proses:
   - **Disetujui** → klien melihat **jadwal final + harga**, muncul tombol **"Bayar Sekarang"**.
   - **Ditolak** → klien melihat alasan, bisa ajukan ulang.
5. **Bayar** (disimulasikan — klik tombol, tanpa payment gateway) → status jadi **Confirming**. Klien lihat: *"Pembayaran sedang diverifikasi admin."*
6. Admin **mengonfirmasi** pembayaran → status **Paid**. Klien lihat: *"Pembayaran lunas, bimbingan segera dimulai."*
7. Pantau progress sampai **Completed**.

---

## 5. Alur Admin (Kamu)

Login dengan akun admin → masuk **Dashboard Admin** yang isinya:

### 5.1 Ringkasan (kartu statistik)
Total pengajuan · Pending (perlu aksi) · Approved (tunggu bayar) · Ongoing · Total pemasukan (dari yang Paid/Completed).

### 5.2 Tabel "Kelola Pengajuan" (inti)
Menampilkan **semua pengajuan dari semua user**, kolom: Nama klien · Bidang · Paket · Deskripsi · Tanggal diminta · Status. Aksi per baris:
- **Setujui** → form kecil: isi **jadwal final** (`scheduled_date`) + **harga** (`price`, untuk Custom diisi hasil nego) + catatan opsional → status **Approved**.
- **Tolak** → isi alasan → status **Rejected**.
- **Konfirmasi Pembayaran** → saat status **Confirming**, admin verifikasi → status **Paid**.
- **Ubah status** → tandai **Ongoing** / **Completed**.

### 5.3 Manajemen User
List semua user: nama, email, jurusan, no. WA, jumlah pengajuan. (Opsional: hapus user.)

### 5.4 (Opsional) Konfigurasi Jadwal
Atur slot/hari tersedia agar saat menyetujui tinggal pilih. *Versi awal cukup input tanggal manual; slot bisa menyusul.*

---

## 6. Endpoint API Baru

**Proteksi:** decorator `@admin_required` (cek `session role == 'admin'`, kalau bukan → 403).

### Admin
- `GET  /api/admin/requests` — semua pengajuan + data klien
- `POST /api/admin/requests/<id>/approve` — body `{ scheduled_date, price, note }` → Approved
- `POST /api/admin/requests/<id>/reject` — body `{ note }` → Rejected
- `POST /api/admin/requests/<id>/status` — body `{ status }` → Paid/Ongoing/Completed
- `GET  /api/admin/users` — daftar semua user

### User (tambahan / modifikasi)
- `POST /api/requests` — tambah field `preferred_date`
- `POST /api/requests/<id>/pay` — simulasi bayar → status **Confirming** (hanya pemilik request)
- Konfirmasi pembayaran oleh admin memakai `POST /api/admin/requests/<id>/status` dengan `{ status: "Paid" }`

---

## 7. Perubahan Halaman / Template

| File | Perubahan |
|---|---|
| `app.py` | `ADMIN_EMAIL` + `admin_required`, routing dashboard per-role, endpoint admin & pay |
| `db.py` | Kolom baru, helper: `get_all_requests`, `get_all_users`, `update_request_status`, `approve_request`, `set_user_role` |
| `templates/dashboard_admin.html` | **BARU** — dashboard admin (statistik, tabel pengajuan, manajemen user) |
| `templates/dashboard.html` | Tambah field tanggal, tampilkan jadwal+harga+tombol Bayar, status baru |
| `static/css/style.css` | Style tabel admin + badge status baru (Rejected, Paid) — mengikuti desain yang ada, **tidak mengubah tampilan lama** |
| `static/js/...` | Handler AJAX aksi admin (approve/reject/status) & tombol bayar |

---

## 8. Rencana Implementasi (Checklist Bertahap)

### Fase A — Fondasi Role
- [ ] Tambah kolom `role` + migrasi/seed admin via `ADMIN_EMAIL`
- [ ] `admin_required` + routing `/dashboard` per-role
- [ ] Halaman `dashboard_admin.html` kerangka + statistik

### Fase B — Kelola Pengajuan (inti)
- [ ] Kolom baru di `requests` + helper DB
- [ ] Tabel "Kelola Pengajuan" + aksi Setujui (jadwal+harga) / Tolak
- [ ] Endpoint approve / reject / status + AJAX

### Fase C — Sisi Klien
- [ ] Field "Tanggal diinginkan" saat mengajukan
- [ ] Tampilkan jadwal + harga + tombol **Bayar** saat Approved
- [ ] Endpoint `/pay` (simulasi) → Paid, progress bar status baru

### Fase D — Manajemen User & Polish
- [ ] Tabel manajemen user
- [ ] (Opsional) konfigurasi slot jadwal
- [ ] Uji end-to-end: klien ajukan → admin setujui+jadwal+harga → klien bayar → ongoing → completed

---

## 9. Keputusan (SUDAH DIPUTUSKAN)

1. ✅ **Penentuan admin** → otomatis lewat `ADMIN_EMAIL` (email kamu).
2. ✅ **Pembayaran** → **disimulasikan** (klik tombol "Bayar", tanpa payment gateway sungguhan).
3. ✅ **Konfirmasi pembayaran** → klien Bayar → **Confirming** → **admin konfirmasi** → **Paid**.
4. ✅ **Penjadwalan** → admin **ketik tanggal manual** saat menyetujui (sistem slot menyusul kalau perlu).
5. ✅ **Harga** → Basic/Pro/Premium otomatis dari paket (admin bisa override); **Custom wajib diisi admin** (nego).

---

*Rencana sudah final. Tinggal eksekusi mengikuti checklist Fase A–D.*
