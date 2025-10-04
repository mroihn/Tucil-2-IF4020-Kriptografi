# Audio Steganography - Tucil 2 IF4020 Kriptografi

## Deskripsi Program

Program steganografi audio yang memungkinkan penyembunyian file rahasia di dalam file audio menggunakan teknik LSB (Least Significant Bit).

### Fitur Utama
- **Embedding & Extraction**: Menyisipkan dan mengekstrak file rahasia dari audio
- **Enkripsi**: Extended Vigenère Cipher untuk 256 karakter (0-255)
- **Random Positioning**: Sistem posisi acak berdasarkan seed untuk keamanan tambahan
- **N-LSB Steganography**: Dukungan 1-4 LSB untuk kapasitas yang fleksibel
- **PSNR Calculation**: Perhitungan Peak Signal-to-Noise Ratio untuk evaluasi kualitas
- **Web Interface**: API backend dengan FastAPI untuk integrasi frontend

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Web framework untuk REST API
- **Uvicorn** - ASGI server untuk FastAPI

### Audio Processing
- **PyDub** - Library untuk manipulasi audio multi-format
- **NumPy** - Komputasi numerik untuk pemrosesan array audio


## Dependensi

### Python Packages
```txt
pydub>=0.25.1
numpy>=1.25.0
setuptools>=68.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
```

### System Requirements
- **FFmpeg** - Diperlukan untuk PyDub (audio format conversion)
- **Python 3.8+**


## Cara Menjalankan Program

### 1. Jalankan Backend (API)
```bash
cd backend
python main.py
```
Pastikan semua dependensi Python sudah terinstall (`pip install -r requirements.txt`), dan FFmpeg sudah tersedia di PATH.

### 2. Jalankan Frontend (Development Mode)
```bash
cd frontend/app
npm install
npm run dev
```
Frontend  dapat diakses pada `localhost:3000` secara default.

### 3. Struktur Folder
- `backend/` : API FastAPI & logika steganografi audio
- `frontend/app/` : Web app Next.js untuk antarmuka pengguna
- `demo_files/` : Contoh file audio dan file rahasia

## How To Use

1. Upload file audio dan file rahasia melalui web frontend.
2. Pilih jumlah LSB dan masukkan seed untuk random positioning (optional).
3. Jalankan proses embedding/extraction melalui interface.
4. Cek hasil dan evaluasi kualitas audio dengan PSNR.