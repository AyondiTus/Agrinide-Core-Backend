---
trigger: manual
---

3. Spesifikasi Fitur Inti (Backend Logic)
3.1. Identitas & Manajemen Katalog
Auth Middleware: Validasi JWT pada setiap protected route.
Bulk Insert Excel: Fitur bagi petani untuk mengunggah banyak data komoditas sekaligus via file .xlsx. Backend melakukan validasi tipe data sebelum melakukan batch insert ke tabel commodities.
Single Insert: Input manual komoditas terikat pada farmer_id (UID).
3.2. Ruang Negosiasi Terstruktur (Draft-Based Negotiation)
Template Integration: Negosiasi wajib memilih template_id sejak awal. Struktur form tawar-menawar menyesuaikan kebutuhan template tersebut.
Multi-Parameter Tawar-Menawar: Mendukung perubahan pada Harga, Volume, Quality Grade, Payment Method, Payment Term, Shipping Point, dan Delivery Type.
Audit Trail: Setiap perubahan parameter disimpan ke negotiation_histories. Data bersifat terstruktur (kolom eksplisit, bukan JSONB).
Turn-Based Logic: Validasi agar pihak pengirim tawaran terakhir tidak bisa melakukan tawar-menawar berturut-turut.
3.3. AI Contract Generator & Blockchain-Style Ledger
Atomic Transition: Saat negosiasi accepted, data dikunci. Backend menggabungkan variabel negosiasi final dengan instruksi legal dari contract_templates.
Gemini Generator: Menghasilkan MoU formal berbasis data terstruktur.
Immutable Ledger: Metadata kontrak di-hash (SHA-256) dan disimpan di tabel contracts.
3.4. Smart Fulfillment (Manajemen Pengiriman)
Parent-Child Ledger: Melacak pengiriman parsial/bertahap.
Atomic Confirmation: Konfirmasi penerimaan oleh pembeli menggunakan transaksi database (SELECT ... FOR UPDATE) untuk sinkronisasi sisa volume kontrak secara real-time.
3.5. Market & Weather Insights
Daily Scraper: Ekstraksi otomatis data tabel harga pokok dari web pemerintah.
Time-Series Data: Menyimpan riwayat harga 30 hari terakhir untuk grafik dashboard.