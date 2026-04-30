---
trigger: manual
---

🛰️ Agent Rule: API Implementation & Routing
Kamu adalah AgriNode API Developer. Tugasmu adalah mengimplementasikan endpoint RESTful menggunakan FastAPI sesuai dengan daftar di bawah ini. Patuhi standar keamanan, skema Pydantic, dan logika database yang ketat.

🛠️ General API Standards
Prefix: Semua route harus diawali dengan /api/v1.

Auth: Gunakan dependency get_current_user (Firebase Auth) untuk semua endpoint kecuali GET /commodities.

Response: Gunakan Pydantic untuk standarisasi response. Gunakan status code yang tepat (201 untuk created, 204 untuk success no content, 400 untuk bad request).

Async: Semua handler wajib menggunakan async def.

📋 Endpoint Category Rules
1. Auth & Identity (/auth)
/Register: Sinkronisasi UID dari Firebase ke tabel users. Jika UID sudah ada, kembalikan profil yang ada.
/Register/petani : Register untuk mendaftarkan petani ke database
/Register/pembeli : Register untuk mendaftarkan pembeli ke database

/Login: Verifikasi token Firebase di header Authorization. Ambil data user dari PostgreSQL berdasarkan UID. Kembalikan 404 jika user terautentikasi di Firebase tapi belum ada di PostgreSQL.

2. Manajemen Katalog (/commodities)
/List: Implementasikan pagination dan filter berdasarkan location atau name.
/update/$id_katalog: Update katalog dari petani untuk komoditas yang di insert oleh petani tersebut
/Manual Insert: Pastikan farmer_id diambil dari current_user.id.

/Bulk Insert: * Gunakan pandas untuk parsing.

Jalankan dalam satu SQL Transaction.

Berikan feedback spesifik baris mana yang error jika validasi gagal.

3. Negosiasi Terstruktur (/negotiations)
/Start: User wajib mengirim commodity_id dan template_id. Inisialisasi parameter awal dari data komoditas.

/Counter: * Turn-Based Check: Cek field proposed_by. Pihak yang sama tidak boleh mengirim tawaran dua kali berturut-turut.

/History: Setiap tawaran baru WAJIB menyimpan state sebelumnya ke negotiation_histories.

/Status: Hanya owner (petani/pembeli) yang bisa melihat detail negosiasi.

4. Kontrak & AI Ledger (/contracts)
/Accept: 1. Ubah status negosiasi menjadi accepted.
2. Panggil Gemini Service untuk generate MoU.
3. Generate SHA-256 Hash dari data kontrak.
4. Simpan ke tabel contracts dan kembalikan hash_id.

/Listing: Berikan filter untuk memisahkan kontrak yang masih pending, partially_fulfilled, dan completed.

5. Logistik & Fulfillment (/fulfillments)
/Fulfill: Petani harus input delivery_volume. Cek apakah delivery_volume <= remaining_volume di kontrak.

/Confirm: * Gunakan SELECT ... FOR UPDATE pada baris kontrak di PostgreSQL untuk mencegah race condition.

/Update remaining_volume = remaining_volume - delivery_volume.

Jika nol, set status kontrak menjadi completed.

6. Insights & Worker (/dashboard & /cron)
/Summary: Cache data cuaca (jika memungkinkan) dan ambil tren harga 30 hari terakhir dengan satu query agregasi.

/Scrape Market: Endpoint ini harus dilindungi dengan X-Internal-Secret header agar tidak bisa ditembak publik.

🧪 Implementation Checklist (Internal)
[ ] Apakah skema Pydantic sudah memvalidasi range angka (misal: harga > 0)?

[ ] Apakah relasi database sudah menggunakan joinedload atau selectinload untuk efisiensi query?

[ ] Apakah error handling sudah menangkap IntegrityError dari SQLAlchemy?

[ ] Apakah file Excel di Bulk Insert langsung dihapus dari memori setelah diproses?