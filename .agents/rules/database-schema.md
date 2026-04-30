---
trigger: manual
---

// ==========================================================
// 1. TABEL MASTER (ENTITAS UTAMA & TEMPLATE)
// ==========================================================
Table users {
  id varchar(128) [primary key, note: 'Firebase UID']
  name varchar(255) [not null]
  email varchar(255) [unique, not null]
  phone varchar(20)
  role varchar(50) [not null, note: 'farmer atau buyer']
  address_city varchar(100)
  address_province varchar(100)
  address_detail text
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table commodities {
  id uuid [primary key, default: `gen_random_uuid()`]
  farmer_id varchar(128) [not null]
  name varchar(255) [not null]
  price_per_kg decimal(12,2) [not null]
  current_stock decimal(10,2) [not null]
  location varchar(255)
  updated_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table contract_templates {
  id uuid [primary key, default: `gen_random_uuid()`]
  name varchar(100) [not null, note: 'Contoh: Forward Contract, Spot Contract']
  description text
  base_text_prompt text [not null, note: 'Instruksi dasar legal untuk Gemini AI']
  required_fields jsonb [note: 'Definisi input form dinamis di frontend']
}

// ==========================================================
// 2. TABEL TRANSAKSIONAL (PRE-DEAL / NEGOSIASI)
// ==========================================================
Table negotiations {
  id uuid [primary key, default: `gen_random_uuid()`]
  template_id uuid [not null, note: 'Draft Kontrak yang dipilih sejak awal']
  farmer_id varchar(128) [not null]
  buyer_id varchar(128) [not null]
  commodity_id uuid [not null]
  current_price decimal(12,2) [not null]
  current_volume decimal(10,2) [not null]
  
  // Field Standarisasi Kontrak & Negosiasi (Terstruktur)
  quality_grade varchar(100) [note: 'Contoh: Grade A Premium']
  payment_method varchar(100) [note: 'Contoh: Transfer Bank, Escrow']
  payment_term varchar(100) [note: 'Contoh: DP 30%, CBD, Termin 14 Hari']
  shipping_point varchar(255) [note: 'Contoh: Loco Gudang Petani, Franko Pabrik']
  delivery_type varchar(100) [note: 'Contoh: Sekaligus (Full), Bertahap (Parsial)']
  
  proposed_by varchar(128) [not null]
  status varchar(50) [default: 'negotiating', note: 'negotiating, accepted, rejected']
  updated_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table negotiation_histories {
  id uuid [primary key, default: `gen_random_uuid()`]
  negotiation_id uuid [not null]
  price decimal(12,2) [not null]
  volume decimal(10,2) [not null]
  
  // Riwayat perubahan parameter saat tawar-menawar
  quality_grade varchar(100)
  payment_method varchar(100)
  payment_term varchar(100)
  shipping_point varchar(255)
  delivery_type varchar(100)
  
  proposed_by varchar(128) [not null]
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

// ==========================================================
// 3. TABEL BLOCKCHAIN LEDGER (POST-DEAL / KONTRAK)
// ==========================================================
Table contracts {
  hash_id varchar(64) [primary key, note: 'SHA-256 Hash Utama']
  negotiation_id uuid [unique, note: 'Asal usul kesepakatan']
  template_id uuid [not null, note: 'Referensi ke template standar']
  farmer_id varchar(128) [not null]
  buyer_id varchar(128) [not null]
  commodity_id uuid [not null]
  total_volume decimal(10,2) [not null]
  remaining_volume decimal(10,2) [not null]
  price_agreed decimal(12,2) [not null]
  
  // Parameter kesepakatan final yang dikunci dalam kontrak
  quality_grade varchar(100) [not null]
  payment_method varchar(100) [not null]
  payment_term varchar(100) [not null]
  shipping_point varchar(255) [not null]
  delivery_type varchar(100) [not null]
  
  status varchar(50) [default: 'pending', note: 'pending, partially_fulfilled, completed']
  mou_url text
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table fulfillments {
  hash_id varchar(64) [primary key, note: 'SHA-256 Hash Pengiriman']
  contract_hash_id varchar(64) [not null]
  delivery_volume decimal(10,2) [not null]
  status varchar(50) [default: 'in_transit', note: 'in_transit, received, rejected']
  buyer_notes text
  delivery_date timestamp [default: `CURRENT_TIMESTAMP`]
  received_at timestamp
}

// ==========================================================
// 4. TABEL EXTERNAL SCRAPING (TIME-SERIES HARGA PASAR)
// ==========================================================
Table market_prices {
  id varchar(100) [primary key, note: 'Contoh: cabe_rawit_merah']
  name varchar(255) [not null]
  unit varchar(50) [not null]
}

Table market_price_daily {
  id uuid [primary key, default: `gen_random_uuid()`]
  market_price_id varchar(100) [not null]
  date date [not null]
  current_price integer [not null]
  previous_price integer [not null]
  change_rp integer [not null]
  change_percentage decimal(5,2) [not null]
  trend varchar(20) [note: 'up, down, stable']
}

// ==========================================================
// DEFINISI RELASI (FOREIGN KEYS)
// ==========================================================

// Relasi Commodities
Ref: commodities.farmer_id > users.id [delete: cascade]

// Relasi Templates ke Negosiasi & Kontrak
Ref: negotiations.template_id > contract_templates.id [delete: restrict]
Ref: contracts.template_id > contract_templates.id [delete: restrict]

// Relasi Negotiations
Ref: negotiations.farmer_id > users.id [delete: restrict]
Ref: negotiations.buyer_id > users.id [delete: restrict]
Ref: negotiations.commodity_id > commodities.id [delete: restrict]
Ref: negotiations.proposed_by > users.id

// Relasi Negotiation Histories
Ref: negotiation_histories.negotiation_id > negotiations.id [delete: cascade]
Ref: negotiation_histories.proposed_by > users.id

// Relasi Contracts
Ref: contracts.negotiation_id - negotiations.id // One-to-One
Ref: contracts.farmer_id > users.id  [delete: restrict]
Ref: contracts.buyer_id > users.id [delete: restrict]
Ref: contracts.commodity_id > commodities.id [delete: restrict]

// Relasi Fulfillments (Parent-Child Ledger)
Ref: fulfillments.contract_hash_id > contracts.hash_id [delete: restrict]

// Relasi Market Prices Daily
Ref: market_price_daily.market_price_id > market_prices.id [delete: cascade] 

Ref: "commodities"."farmer_id" < "commodities"."id"