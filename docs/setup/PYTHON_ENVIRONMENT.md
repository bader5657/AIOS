# AIOS Python Environment

Status: Aktif  
Berlaku Mulai: Sprint 18

## Tujuan

Dokumen ini menjelaskan cara menyiapkan lingkungan Python untuk pengembangan dan pengujian AIOS tanpa mengubah Python bawaan sistem operasi.

## Versi Python

AIOS saat ini menggunakan:

- Python 3.12
- Virtual environment melalui `venv`
- Pytest sebagai test runner

## Membuat Virtual Environment

Jalankan dari root repository:

```bash
cd /opt/aios-src
python3 -m venv .venv

