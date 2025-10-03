import os
import time
import struct
import json
import hashlib
import random
from typing import Optional

import numpy as np
from pydub import AudioSegment
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import UploadFile as StarletteUploadFile
from pathlib import Path

import uvicorn

from script import VigenereCipher, RandomPositionGenerator, AudioSteganography

app = FastAPI(title="Audio Steganography API")

# Allow CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(upload: StarletteUploadFile, subdir: str = "") -> str:
    subdir_path = UPLOAD_DIR / subdir
    subdir_path.mkdir(parents=True, exist_ok=True)
    filename = f"{int(time.time()*1000)}_{upload.filename}"
    file_path = subdir_path / filename
    with open(file_path, "wb") as f:
        f.write(upload.file.read())
    return str(file_path)


def parse_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    v = str(value).lower()
    return v in ("1", "true", "yes", "y")


def compute_psnr_from_files(original_path: str, stego_path: str) -> Optional[float]:
    try:
        orig = AudioSegment.from_file(original_path)
        stego = AudioSegment.from_file(stego_path)
        orig_arr = np.array(orig.get_array_of_samples(), dtype=np.int16)
        stego_arr = np.array(stego.get_array_of_samples(), dtype=np.int16)
        if orig.channels == 2:
            orig_arr = orig_arr.reshape(-1, 2)
        if stego.channels == 2:
            stego_arr = stego_arr.reshape(-1, 2)
        orig_flat = orig_arr.flatten()
        stego_flat = stego_arr.flatten()
        min_len = min(orig_flat.size, stego_flat.size)
        if min_len == 0:
            return None
        orig_flat = orig_flat[:min_len].astype(np.float64)
        stego_flat = stego_flat[:min_len].astype(np.float64)
        mse = np.mean((orig_flat - stego_flat) ** 2)
        if mse == 0:
            return float("inf")
        max_val = 2**15 - 1
        psnr = 20 * np.log10(max_val / np.sqrt(mse))
        return float(psnr)
    except Exception as e:
        print("PSNR calc error:", e)
        return None


@app.post("/embed")
async def api_embed(
    cover_file: UploadFile = File(...),
    secret_file: UploadFile = File(...),
    stego_key: str = Form(...),
    n_lsb: int = Form(1),
    use_encryption: bool = Form(False),
    use_random: bool = Form(False)
):
    try:
        cover_path = save_uploaded_file(cover_file, subdir="covers")
        secret_path = save_uploaded_file(secret_file, subdir="secrets")

        if not stego_key or len(stego_key) < 6:
            return JSONResponse({"success": False, "error": "stego_key required (min 6 chars)"}, status_code=400)

        if not (1 <= n_lsb <= 4):
            return JSONResponse({"success": False, "error": "n_lsb must be 1-4"}, status_code=400)

        use_encryption = parse_bool(use_encryption)
        use_random = parse_bool(use_random)

        # --- Output file has same name as cover file ---
        cover_name = os.path.basename(cover_path)
        ext = os.path.splitext(cover_name)[1].lower() or ".wav"
        out_path = UPLOAD_DIR / "stego" / cover_name
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # --- Load and embed ---
        stego = AudioSteganography()
        if not stego.load_audio(cover_path):
            return JSONResponse({"success": False, "error": "Failed to load cover audio"}, status_code=500)

        capacity = stego.calculate_capacity(n_lsb)
        secret_size = os.path.getsize(secret_path)
        if secret_size > capacity:
            return JSONResponse(
                {"success": False, "error": "Secret too large for cover capacity", "capacity": capacity, "secret_size": secret_size},
                status_code=400,
            )

        ok = stego.embed_message(secret_path, str(out_path), stego_key, 
                                 n_lsb=n_lsb, use_encryption=use_encryption, use_random=use_random)
        if not ok:
            return JSONResponse({"success": False, "error": "Embedding failed"}, status_code=500)

        # --- Delete secret file after embedding ---
        try:
            os.remove(secret_path)
        except Exception as cleanup_err:
            print(f"Warning: could not delete secret file {secret_path}: {cleanup_err}")

        # --- Compute PSNR and return ---
        psnr = compute_psnr_from_files(cover_path, str(out_path))
        rel_path = os.path.relpath(out_path, start=BASE_DIR)

        return {"success": True, "embed_file": rel_path, "psnr_score": psnr}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/extract")
async def api_extract(
    stego_file: UploadFile = File(...),
    stego_key: str = Form(...),
):
    try:
        stego_path = save_uploaded_file(stego_file, subdir="stego_uploads")

        if not stego_key:
            return JSONResponse({"success": False, "error": "stego_key is required"}, status_code=400)

        stego = AudioSteganography()
        if not stego.load_audio(stego_path):
            return JSONResponse({"success": False, "error": "Failed to load stego audio"}, status_code=500)

        out_path = stego.extract_message(stego_key)
        if not out_path:
            return JSONResponse({"success": False, "error": "Extraction failed"}, status_code=400)

        rel_path = os.path.relpath(out_path, start=BASE_DIR)
        return {"success": True, "file": rel_path}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)