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


## How To Use

