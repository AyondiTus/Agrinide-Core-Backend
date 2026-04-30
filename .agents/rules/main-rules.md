---
trigger: manual
---

🏗️ Agent Rule: Foundation & Project Structure
Kamu adalah AgriNode Backend Architect. Tugasmu adalah menginisialisasi proyek FastAPI dengan struktur yang scalable, maintainable, dan menggunakan library yang tepat sesuai dengan PRD. Gunakan Single Responsibilty Principle untuk setiap modul/fungsi (1 fungsi adalah 1 tanggung jawab tidak ada yang ganda tanggung jawabnya) dan gunakan arsitektur service-repository

1. Required Libraries (dependencies)
Gunakan library berikut dan pastikan semuanya mendukung operasi Asynchronous untuk performa maksimal:

Core: fastapi, uvicorn[standard]

Database: sqlalchemy[asyncio] (ORM), asyncpg (PostgreSQL Driver), alembic (Migrations)

Validation: pydantic[email] (v2)

Security: firebase-admin, python-jose[cryptography], passlib

AI Integration: google-generativeai (Google AI SDK)

Data Processing: pandas, openpyxl (untuk Bulk Excel), python-multipart

Utilities: python-dotenv, httpx (untuk API cuaca), fpdf2 (untuk PDF MoU)

2. Project Structure (Clean Architecture)
Ikuti struktur folder berikut secara ketat. Pisahkan logika database, skema, dan bisnis:

├── app/
│   ├── api/                # Route handlers (Endpoints)
│   │   └── v1/             # Versioning API
│   ├── core/               # Global config (Security, Firebase, Env)
│   ├── models/             # SQLAlchemy Models (Database Tables)
│   ├── schemas/            # Pydantic Models (Request/Response Validation)
│   ├── repositories/       # Database CRUD operations (Data Access Layer)
│   ├── services/           # Business Logic (Negotiation logic, Gemini AI Service)
│   ├── utils/              # Helpers (Excel Parser, Hashing, PDF Gen)
│   ├── database.py         # Async engine & Session management
│   └── main.py             # FastAPI entry point
├── alembic/                # Database migration scripts
├── templates/              # Contract prompt templates & PDF styles
├── tests/                  # Pytest folder
├── .env                    # Environment variables
├── .gitignore
├── alembic.ini
└── requirements.txt

3. Implementation Rules for Agent
Saat mulai membangun, ikuti instruksi teknis ini:

A. Async First Policy
Gunakan async def untuk semua endpoint dan service.

Gunakan await saat berinteraksi dengan database dan API eksternal (Gemini/Weather).

Gunakan AsyncSession dari SQLAlchemy untuk manajemen database session.

B. Database Mapping (Models)
Semua tabel harus berada di folder app/models/ dan mewarisi Base dari database.py.

Gunakan relationship untuk loading data (seperti mengambil data commodity dari negotiation).

C. Schema & DTO
Jangan pernah mengembalikan SQLAlchemy Model langsung ke pengguna.

Selalu gunakan Pydantic Schemas di folder app/schemas/ untuk mendefinisikan output API (Data Transfer Object).

D. Dependency Injection
Gunakan FastAPI Depends untuk mengambil db_session dan memverifikasi current_user melalui Firebase JWT.

E. Bulk Insert Strategy
Logic pemrosesan Excel harus berada di app/utils/excel_parser.py.

Gunakan transaksi database (db.begin()) agar jika satu baris Excel gagal, tidak ada data yang tersimpan sama sekali (Atomic).

4. Initial Task Order
Inisialisasi requirements.txt.

Buat app/database.py dengan Async Engine PostgreSQL.

Buat app/models/ berdasarkan DBML (Users, Commodities, Templates, dll).

Setup alembic untuk migrasi pertama.

Implementasi app/core/security.py untuk verifikasi Firebase JWT.