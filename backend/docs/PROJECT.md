## **1. Ringkasan Eksekutif**

AgriNode adalah platform B2B yang mendigitalkan transaksi pertanian dari hulu ke hilir dengan menggabungkan konsep **Draft-Based Negotiation**, **Blockchain-Style Ledger**, dan ekosistem **Agentic AI**. Backend dirancang untuk memfasilitasi tawar-menawar yang dinamis melalui form terstruktur dan *real-time chat*, di mana AI bertindak secara otonom sebagai asisten penasihat (*Co-Pilot*), analis pasar proaktif, konsultan agronomi, hingga asisten legal berbasis RAG (Retrieval-Augmented Generation) untuk operasional pasca-deal.

## **2. Arsitektur Teknis & Stack Teknologi**

- **Framework Backend Core:** Python FastAPI (mendukung asinkronus penuh).
- **Database Utama:** PostgreSQL (Relational Database) dikelola melalui SQLAlchemy (ORM) dan Alembic.
- **Komunikasi Real-Time:** WebSockets (untuk fitur Chat Negosiasi).
- **Identity & Access Management:** Firebase Authentication & JWT.
- **Penyimpanan Berkas:** Firebase Storage (Bukti bayar & MoU PDF).
- **Integrasi Agentic AI & RAG:** Google Gemini API (untuk generasi kontrak, fungsi agen proaktif, dan pemrosesan vektor dokumen hukum).
- **Automasi Data:** Background Tasks / Cron Job untuk *scraping* pasar harian dan *trigger* agen AI proaktif.

## **3. Spesifikasi Fitur Inti (Backend Logic & Agentic AI)**

### **3.1. Identitas, Manajemen Lahan, & Crop Prediction AI**

- **Manajemen Lahan (sawah):** Petani dapat mendaftarkan profil lahan mereka, mencakup luas tanah, lokasi, dan kondisi tanah.
- **🤖 Agentic AI 1: Agronomy Predictor (Prediksi Tanam):**
    - **Konsep:** Agen yang membantu petani merencanakan musim tanam.
    - **Cara Kerja:** Petani memasukkan nominal modal (budget) yang dimiliki saat ini. Agen akan melakukan *query* ke tabel sawah untuk mengambil data kondisi_tanah dan luas_sawah. Agen kemudian menganalisis kombinasi modal dan profil tanah tersebut untuk memberikan rekomendasi komoditas yang paling optimal untuk ditanam, lengkap dengan estimasi hasil panen.

### **3.2. Ruang Negosiasi Terpadu & Real-Time Chat**

- **Draft-Based Form:** Tawar-menawar 6 variabel utama (Harga, Volume, Grade, Payment Method, Term, Delivery) menggunakan *turn-based logic*.
- **Real-Time Chat:** Terintegrasi di dalam ruang negosiasi yang sama menggunakan koneksi WebSocket, memungkinkan petani dan pembeli bertukar konteks secara natural (tersimpan di tabel negotiation_chats).
- **🤖 Agentic AI 2: Negotiation Co-Pilot:**
    - **Konsep:** Asisten pembisik cerdas selama proses tawar-menawar.
    - **Cara Kerja:** Setiap kali ada tawaran baru atau pesan *chat* masuk, Agen membaca negotiation_histories, riwayat negotiation_chats, dan tren market_price_daily saat itu.
    - **Action:** Agen memberikan saran strategis (*pop-up insight*) kepada target user (misal: *"Tawaran ini Rp 2.000 di bawah pasar, namun dari chat, pembeli butuh cepat untuk ekspor. Saran: Terima harga ini dengan syarat mengubah Payment Term menjadi Cash Before Delivery"*).

### **3.3. Market Insights & Proactive Pricing**

- **Cron Job Scraping:** Ekstraksi data harga pangan ke tabel market_price_daily.
- **🤖 Agentic AI 3: Proactive Market Agent:**
    - **Konsep:** Agen yang bertindak sebagai manajer harga otomatis untuk melindungi margin petani.
    - **Cara Kerja:** Setelah *cron job* harga pasar selesai, Agen mengevaluasi seluruh data di tabel commodities. Jika harga jual petani terdeteksi tertinggal jauh di bawah harga pasar terkini, Agen mengirimkan notifikasi interaktif.
    - **Action:** *"Harga cabe rawit di pasar Jatim sedang naik 15%. Harga Anda (Rp 30.000) terlalu murah. Apakah Anda ingin saya update harganya menjadi Rp 35.000?"* Jika petani menyetujui, Agen mengeksekusi *function calling* untuk meng-update database.

### **3.4. Blockchain Ledger & Legal RAG Assistant**

- **Immutable Ledger:** Metadata kesepakatan final di-hash (SHA-256) untuk membuat entri yang terkunci di tabel contracts. MoU fisik (PDF) di-generate oleh Gemini.
- **🤖 Agentic AI 4: Legal RAG Assistant:**
    - **Konsep:** Menghidupkan dokumen pasca-deal agar bisa diajak interaksi untuk kebutuhan operasional logistik dan hukum.
    - **Cara Kerja:** Sistem mengimplementasikan arsitektur Retrieval-Augmented Generation. Pengguna dapat bertanya (*prompting*) seperti *"Berapa sisa volume yang belum dikirim ke PT ABC?"* atau *"Apakah saya kena denda jika telat 2 hari?"*
    - **Action:** Agen mengambil (*retrieve*) teks PDF dari mou_url di tabel contracts, menyilangkannya dengan status pengiriman *real-time* di tabel fulfillments, dan men-generate jawaban operasional/hukum yang akurat berdasarkan parameter final tersebut.

### **3.5. Smart Fulfillment & Manual Payment**

- **Pengiriman Parsial:** Menggunakan relasi Parent-Child Ledger antara kontrak dan pengiriman.
- **Konfirmasi Manual:** Pembayaran tagihan diunggah buktinya oleh pembeli, dan diverifikasi (verified_by) langsung oleh petani untuk mengubah status kontrak secara atomik.