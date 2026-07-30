# AIOS Architecture v1.0

## Vision

AIOS membantu menjalankan bisnis dengan lebih sedikit pekerjaan manual dan lebih banyak proses yang berjalan otomatis.

AIOS menggunakan satu antarmuka utama dengan banyak kemampuan di belakangnya.

Primary interface:

- Telegram

Future interfaces:

- Web
- Mobile
- API
- Voice
- WhatsApp jika diperlukan

## Core Principle

Satu antarmuka, banyak kemampuan.

Pengguna tidak diminta memilih agent. AIOS menentukan mode atau specialist yang sesuai. Jika permintaan ambigu, AIOS meminta klarifikasi berdasarkan maksud pekerjaan, bukan meminta pengguna memilih agent.

## Official Pipeline

Telegram
↓
Telegram Adapter
↓
Universal Ingestion
↓
Request Context
↓
Asset Pipeline
↓
Document Manifest
↓
PostgreSQL Registry
↓
AIOS Event Engine
↓
AIOS Core
↓
AIOS Brain
↓
Specialist Router
↓
Specialists
↓
PostgreSQL / Storage / External Services

## AIOS Brain

AIOS Brain terdiri dari:

- Chief of Staff
- Advisor
- Decision Engine
- Specialist Router
- AIOS Memory
- Knowledge
- Planner

### Chief of Staff

- Menjaga visi
- Menjaga roadmap
- Menjaga prioritas
- Mengelola backlog
- Mencegah proyek melebar tanpa alasan

### Advisor

- Diskusi umum
- Strategi
- Produktivitas
- Evaluasi keputusan
- Topik di luar bisnis jika diperlukan

### Specialist Router

- Memilih specialist secara otomatis
- Tidak meminta pengguna memilih agent
- Meminta klarifikasi hanya jika permintaan ambigu

## Initial Specialists

- Admin
- Finance
- CTO
- Content
- Creative

Specialist baru dapat ditambahkan tanpa mengubah cara pengguna berinteraksi dengan AIOS.

## Universal Ingestion

AIOS menerima:

- Text
- Image
- Voice
- Audio
- Video
- PDF
- DOC/DOCX
- Spreadsheet
- Web link
- YouTube link

Setiap file asli harus disimpan sebelum diproses.

Lifecycle:

Receive
↓
Store Original
↓
Extract Metadata
↓
Create Manifest
↓
Register
↓
Process
↓
Route
↓
Respond

## Storage

Runtime storage:

- `/opt/aios/data/documents/images`
- `/opt/aios/data/documents/voice`
- `/opt/aios/data/documents/pdf`
- `/opt/aios/data/documents/docs`
- `/opt/aios/data/documents/links`
- `/opt/aios/data/documents/manifests`

File asli tidak disimpan sebagai binary utama di PostgreSQL. PostgreSQL menyimpan identitas, metadata, relasi, status, dan lokasi file.

## Source and Runtime

Source repository:

- `/opt/aios-src`

Runtime:

- `/opt/aios`

Secrets, database data, logs, backups, and original business files must not enter Git.

## Service

AIOS berjalan sebagai systemd service:

- `aios.service`

AIOS harus:

- otomatis aktif setelah reboot
- hanya memiliki satu instance Telegram polling
- dapat dipantau melalui systemctl dan journalctl

## Current Version

Version:

- `0.1.0-alpha`

Completed:

- VPS foundation
- Security baseline
- PostgreSQL
- Git repository
- Telegram Adapter
- Request Context
- Input Classifier
- Universal Ingestion
- Universal Storage
- Metadata Engine
- Automatic Document Manifest
- Mission Control v1
- systemd service

## Short-Term Priorities

1. Shoegabox Admin
2. Content Production System
3. Digital Asset Generator
4. Creative Agent

Every new feature must support at least one of these priorities. Otherwise, it enters the backlog.

## Development Rules

- Satu tahap eksekusi pada satu waktu
- Tahap harus diverifikasi sebelum lanjut
- Untuk perubahan Python besar, replace seluruh file
- Jangan edit potongan kode panjang melalui nano
- Compile sebelum restart service
- Restart service setelah perubahan kode
- Uji melalui Telegram
- Commit milestone yang stabil ke Git
- Jangan menyimpan secret di source code
- Jangan menambah fondasi baru tanpa kebutuhan nyata

## Dependency Direction

Adapters may depend on Core.

Ingestion may depend on App and Storage.

Storage must not depend on Brain or Specialists.

Brain may consume Request Context, Manifest, Registry, Memory, and Knowledge.

Specialists may use approved Core services and business repositories.

Business logic must not be placed inside Telegram Adapter.

## Long-Term Direction

AIOS dapat berkembang menjadi platform yang:

- mengelola operasional bisnis
- menghasilkan konten otomatis
- mengelola website dan aset digital
- menghasilkan materi kreatif
- mendukung banyak bisnis
- memiliki puluhan atau ratusan specialist

Jumlah specialist dapat bertambah tanpa mengubah satu antarmuka utama AIOS.
