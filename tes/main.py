import os
import sys
import struct
import random
import hashlib
import json
from typing import Optional, Tuple, List
import numpy as np
from pydub import AudioSegment


class VigenereCipher:
    """Extended Vigenère Cipher untuk 256 karakter (0-255)"""
    
    def __init__(self, key: str):
        self.key = key
        
    def _extend_key(self, text_length: int) -> bytes:
        """Memperpanjang kunci sesuai panjang teks"""
        if not self.key:
            raise ValueError("Kunci tidak boleh kosong")
        
        key_bytes = self.key.encode('utf-8', errors='ignore')
        extended = (key_bytes * (text_length // len(key_bytes) + 1))[:text_length]
        return extended
    
    def encrypt(self, data: bytes) -> bytes:
        """Enkripsi data menggunakan extended Vigenère cipher"""
        if not data:
            return b''
        
        key_extended = self._extend_key(len(data))
        encrypted = bytearray()
        
        for i in range(len(data)):
            encrypted_byte = (data[i] + key_extended[i]) % 256
            encrypted.append(encrypted_byte)
        
        return bytes(encrypted)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Dekripsi data menggunakan extended Vigenère cipher"""
        if not encrypted_data:
            return b''
        
        key_extended = self._extend_key(len(encrypted_data))
        decrypted = bytearray()
        
        for i in range(len(encrypted_data)):
            decrypted_byte = (encrypted_data[i] - key_extended[i]) % 256
            decrypted.append(decrypted_byte)
        
        return bytes(decrypted)


class RandomPositionGenerator:
    """Generator untuk posisi acak berdasarkan seed"""
    
    def __init__(self, seed_string: str, max_positions: int):
        # Konversi string seed ke integer menggunakan hash
        seed_hash = hashlib.md5(seed_string.encode('utf-8')).hexdigest()
        self.seed = int(seed_hash, 16) % (2**32)  # Batasi ke 32-bit
        self.max_positions = max_positions
        self._positions = None
        
    def generate_positions(self, count: int) -> List[int]:
        """Generate daftar posisi acak unik"""
        if count > self.max_positions:
            raise ValueError(f"Jumlah posisi ({count}) melebihi maksimum ({self.max_positions})")
        
        # Generate positions sekali saja dan cache
        if self._positions is None:
            random.seed(self.seed)
            positions = list(range(self.max_positions))
            random.shuffle(positions)
            self._positions = positions
        
        return self._positions[:count]


class AudioSteganography:
    """Kelas utama untuk steganografi audio - FIXED VERSION"""
    
    SIGNATURE = b'AUDIOSTG'  # Signature untuk identifikasi (8 bytes)
    METADATA_SIZE_BYTES = 4  # 4 bytes untuk ukuran metadata
    
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.channels = None
        
    def load_audio(self, file_path: str) -> bool:
        """Load file audio (MP3, WAV, FLAC, dll)"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} tidak ditemukan!")
                return False
            
            # Deteksi format file
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.mp3':
                audio = AudioSegment.from_mp3(file_path)
            elif ext == '.wav':
                audio = AudioSegment.from_wav(file_path)
            elif ext == '.flac':
                audio = AudioSegment.from_file(file_path, format="flac")
            elif ext == '.ogg':
                audio = AudioSegment.from_ogg(file_path)
            else:
                # Coba auto-detect
                audio = AudioSegment.from_file(file_path)
            
            # Konversi ke raw audio data
            self.audio_data = np.array(audio.get_array_of_samples(), dtype=np.int16)
            self.sample_rate = audio.frame_rate
            self.channels = audio.channels
            
            # Jika stereo, reshape menjadi 2D array
            if self.channels == 2:
                self.audio_data = self.audio_data.reshape(-1, 2)
            
            print(f"Audio dimuat: {len(self.audio_data)} samples, "
                  f"{self.sample_rate}Hz, {self.channels} channel(s)")
                  
            # Peringatan untuk file MP3
            if ext == '.mp3':
                print("⚠ PERINGATAN: File MP3 menggunakan kompression lossy!")
                print("  Untuk steganografi terbaik, gunakan format lossless (WAV, FLAC)")
                
            return True
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False
    
    def save_audio(self, file_path: str) -> bool:
        """Simpan audio data ke file (WAV untuk steganografi, MP3 untuk hasil akhir)"""
        try:
            if self.audio_data is None:
                print("Error: Tidak ada audio data untuk disimpan")
                return False
                
            # Flatten audio data jika stereo
            if self.channels == 2:
                audio_array = self.audio_data.flatten()
            else:
                audio_array = self.audio_data
            
            # Buat AudioSegment dari array
            audio = AudioSegment(
                audio_array.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,  # 16-bit
                channels=self.channels
            )
            
            # Buat directory jika belum ada
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # PENTING: Untuk steganografi, simpan sebagai WAV (lossless) 
            # agar LSB tidak rusak akibat MP3 compression
            if file_path.lower().endswith('.mp3'):
                # Ganti ekstensi ke .wav untuk steganografi
                wav_path = file_path[:-4] + '_stego.wav'
                audio.export(wav_path, format="wav")
                print(f"⚠ PENTING: Audio disimpan sebagai WAV (lossless) untuk menjaga steganografi")
                print(f"✓ File stego: {wav_path}")
                print(f"💡 Tip: Gunakan file .wav untuk ekstraksi, bukan .mp3")
                
                # Optional: buat juga versi MP3 untuk distribusi (tapi data stego akan rusak)
                try:
                    audio.export(file_path, format="mp3", bitrate="320k")
                    print(f"✓ File MP3 (untuk distribusi, data stego mungkin rusak): {file_path}")
                except:
                    pass
                    
                return True
            else:
                # Jika ekstensi bukan .mp3, simpan sesuai format yang diminta
                format_map = {
                    '.wav': 'wav',
                    '.flac': 'flac', 
                    '.ogg': 'ogg'
                }
                
                ext = os.path.splitext(file_path)[1].lower()
                format_name = format_map.get(ext, 'wav')
                
                audio.export(file_path, format=format_name)
                print(f"Audio disimpan ke: {file_path}")
                return True
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def calculate_capacity(self, n_lsb: int) -> int:
        """Hitung kapasitas penyisipan dalam bytes"""
        if self.audio_data is None:
            return 0
        
        total_samples = self.audio_data.size
        total_bits = total_samples * n_lsb
        
        # Dikurangi space untuk signature dan metadata
        signature_bits = len(self.SIGNATURE) * 8
        metadata_size_bits = self.METADATA_SIZE_BYTES * 8
        
        available_bits = total_bits - signature_bits - metadata_size_bits
        available_bytes = available_bits // 8
        
        return max(0, available_bytes)
    def _extract_bits_random(self, n_lsb: int, start_sample: int, n_bits: int, seed_string: str) -> list[int]:
        """Ekstraksi bit dari audio menggunakan posisi acak"""
        if self.audio_data is None:
            raise ValueError("Audio data tidak dimuat")
        
        total_samples = self.audio_data.size
        
        # Flatten audio
        if self.channels == 2:
            flat_audio = self.audio_data.flatten()
        else:
            flat_audio = self.audio_data
        
        # Generator posisi acak
        pos_gen = RandomPositionGenerator(seed_string, total_samples)
        all_positions = pos_gen.generate_positions(total_samples)
        
        # Ambil posisi setelah header (start_sample)
        data_positions = [pos for pos in all_positions if pos >= start_sample]
        
        # Hitung jumlah sampel yang diperlukan
        required_samples = (n_bits + n_lsb - 1) // n_lsb
        data_positions = data_positions[:required_samples]
        
        extracted_bits = []
        for sample_pos in data_positions:
            if len(extracted_bits) >= n_bits:
                break
            
            sample = int(flat_audio[sample_pos])
            bits_value = sample & ((1 << n_lsb) - 1)
            
            for i in range(n_lsb):
                if len(extracted_bits) >= n_bits:
                    break
                extracted_bits.append((bits_value >> i) & 1)
        
        return extracted_bits

    def _extract_bits_sequential(self, n_lsb: int, start_sample: int, num_bits: int) -> List[int]:
        """Ekstrak bits secara berurutan mulai dari sample tertentu (FIXED)"""
        if self.audio_data is None:
            raise ValueError("Audio data tidak dimuat")
        
        total_samples = self.audio_data.size
        if self.channels == 2:
            flat_audio = self.audio_data.flatten()
        else:
            flat_audio = self.audio_data
        
        extracted_bits = []
        current_sample = start_sample
        
        # For 1-LSB extraction (used for header parts: signature, metadata_size, metadata)
        if n_lsb == 1:
            for i in range(num_bits):
                if current_sample >= total_samples:
                    break
                sample = int(flat_audio[current_sample])
                bit = sample & 1  # Extract LSB
                extracted_bits.append(bit)
                current_sample += 1
        else:
            # For n-LSB extraction (used for secret data)
            bits_needed = num_bits
            
            while bits_needed > 0 and current_sample < total_samples:
                sample = int(flat_audio[current_sample])
                
                # Extract n bits from this sample (LSB first order to match embedding)
                bits_to_extract = min(n_lsb, bits_needed)
                
                for bit_pos in range(bits_to_extract):
                    bit = (sample >> bit_pos) & 1
                    extracted_bits.append(bit)
                    bits_needed -= 1
                    
                    if bits_needed <= 0:
                        break
                
                current_sample += 1
        
        return extracted_bits[:num_bits]
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Konversi list of bits ke bytes (FIXED)"""
        # Pad to nearest byte boundary
        while len(bits) % 8 != 0:
            bits.append(0)
        
        data = bytearray()
        for i in range(0, len(bits), 8):
            byte_val = 0
            # Reconstruct byte: first bit goes to MSB (bit 7), last bit goes to LSB (bit 0)
            for j in range(8):
                if i + j < len(bits):
                    byte_val |= (bits[i + j] << (7 - j))
            data.append(byte_val)
        
        return bytes(data)
    
    def _embed_bits(self, data: bytes, n_lsb: int, use_random: bool, 
                    seed_string: str) -> bool:
        """Sisipkan data ke dalam audio menggunakan n-LSB (FIXED)"""
        try:
            if self.audio_data is None:
                raise ValueError("Audio data tidak dimuat")
            
            total_samples = self.audio_data.size
            # Buat copy untuk menghindari modifikasi original
            if self.channels == 2:
                flat_audio = self.audio_data.flatten().copy()
            else:
                flat_audio = self.audio_data.copy()
            
            print(f"Memulai embedding: {len(data)} bytes, n_lsb={n_lsb}, random={use_random}")
            
            # Pisahkan data menjadi bagian-bagian
            signature = self.SIGNATURE
            metadata_size_bytes = data[len(signature):len(signature) + self.METADATA_SIZE_BYTES]
            metadata_size = struct.unpack('<I', metadata_size_bytes)[0]
            metadata = data[len(signature) + self.METADATA_SIZE_BYTES:len(signature) + self.METADATA_SIZE_BYTES + metadata_size]
            secret_data = data[len(signature) + self.METADATA_SIZE_BYTES + metadata_size:]
            
            print(f"✓ Data breakdown:")
            print(f"  - Signature: {len(signature)} bytes")
            print(f"  - Metadata size: {len(metadata_size_bytes)} bytes (value: {metadata_size})")
            print(f"  - Metadata: {len(metadata)} bytes")
            print(f"  - Secret data: {len(secret_data)} bytes")
            
            current_sample = 0
            
            # Helper function to embed data with 1-LSB
            def embed_1lsb(data_bytes, start_sample):
                sample_idx = start_sample
                for byte in data_bytes:
                    for bit_pos in range(8):
                        if sample_idx >= total_samples:
                            raise ValueError("Tidak cukup ruang untuk data")
                        
                        bit = (byte >> (7 - bit_pos)) & 1  # MSB first (bit 7, 6, 5, ... 0)
                        sample = int(flat_audio[sample_idx])
                        sample = (sample & ~1) | bit  # Set LSB
                        flat_audio[sample_idx] = sample
                        sample_idx += 1
                return sample_idx
            
            # 1. Embed signature dengan 1-LSB berurutan
            current_sample = embed_1lsb(signature, current_sample)
            print(f"✓ Signature embedded pada samples 0-{current_sample-1}")
            
            # 2. Embed metadata size dengan 1-LSB berurutan  
            current_sample = embed_1lsb(metadata_size_bytes, current_sample)
            print(f"✓ Metadata size embedded pada samples {current_sample-32}-{current_sample-1}")
            
            # 3. Embed metadata dengan 1-LSB berurutan
            current_sample = embed_1lsb(metadata, current_sample)
            print(f"✓ Metadata embedded pada samples {current_sample - len(metadata)*8}-{current_sample-1}")
            
            # 4. Embed secret data dengan n-LSB
            if len(secret_data) > 0:
                secret_bits = []
                for byte in secret_data:
                    for bit_pos in range(8):
                        secret_bits.append((byte >> (7 - bit_pos)) & 1)  # MSB first
                
                required_samples = (len(secret_bits) + n_lsb - 1) // n_lsb
                
                if use_random:
                    # Generate posisi acak untuk data
                    pos_gen = RandomPositionGenerator(seed_string, total_samples)
                    all_positions = pos_gen.generate_positions(total_samples)
                    # Ambil posisi setelah header
                    data_positions = [pos for pos in all_positions if pos >= current_sample]
                    data_positions = data_positions[:required_samples]
                    print(f"✓ Menggunakan {len(data_positions)} posisi acak")
                else:
                    # Posisi berurutan
                    data_positions = list(range(current_sample, current_sample + required_samples))
                    print(f"✓ Menggunakan {len(data_positions)} posisi berurutan")
                
                # Embed secret data dengan n-LSB
                bit_index = 0
                for sample_pos in data_positions:
                    if sample_pos >= total_samples or bit_index >= len(secret_bits):
                        break
                    
                    sample = int(flat_audio[sample_pos])
                    
                    # Clear n LSBs
                    mask = ~((1 << n_lsb) - 1)
                    sample_cleared = sample & mask
                    
                    # Ambil n bits berikutnya
                    bits_value = 0
                    bits_to_embed = min(n_lsb, len(secret_bits) - bit_index)
                    
                    # Store bits from LSB to MSB within the n-bit group (to match extraction)
                    for i in range(bits_to_embed):
                        bits_value |= (secret_bits[bit_index + i] << i)
                    
                    sample_new = sample_cleared | bits_value
                    flat_audio[sample_pos] = sample_new
                    bit_index += n_lsb
                
                print(f"✓ Secret data embedded: {bit_index} bits dari {len(secret_bits)} bits")
            
            # Kembalikan ke bentuk asli
            if self.channels == 2:
                self.audio_data = flat_audio.reshape(-1, 2)
            else:
                self.audio_data = flat_audio
            
            # Verifikasi embedding
            verify_bits = self._extract_bits_sequential(1, 0, len(self.SIGNATURE) * 8)
            verify_data = self._bits_to_bytes(verify_bits)
            if verify_data == self.SIGNATURE:
                print("✓ Embedding verification: Signature match")
            else:
                print("✗ Embedding verification: Signature mismatch")
                print(f"  Expected: {self.SIGNATURE.hex()}")
                print(f"  Got: {verify_data.hex()}")
            
            return True
            
        except Exception as e:
            print(f"Error embedding bits: {e}")
            import traceback
            traceback.print_exc()
            return False

    def embed_message(self, secret_file: str, output_file: str, 
                     stego_key: str, n_lsb: int = 1, 
                     use_encryption: bool = False, 
                     use_random: bool = False) -> bool:
        """Sisipkan pesan rahasia ke dalam audio"""
        try:
            # Baca file pesan rahasia
            with open(secret_file, 'rb') as f:
                secret_data = f.read()
            
            print(f"✓ File rahasia: {len(secret_data)} bytes")
            
            # Persiapkan metadata
            file_info = {
                'original_name': os.path.basename(secret_file),
                'file_size': len(secret_data),
                'extension': os.path.splitext(secret_file)[1],
                'encrypted': use_encryption,
                'random_positions': use_random,
                'n_lsb': n_lsb
            }
            
            metadata = json.dumps(file_info, ensure_ascii=False).encode('utf-8')
            metadata_size = len(metadata)
            metadata_size_bytes = struct.pack('<I', metadata_size)
            
            print(f"✓ Metadata size: {metadata_size} bytes")
            
            # Enkripsi data jika diperlukan
            if use_encryption:
                print("✓ Mengenkripsi data...")
                cipher = VigenereCipher(stego_key)
                secret_data = cipher.encrypt(secret_data)
                print(f"✓ Data terenkripsi: {len(secret_data)} bytes")
            
            # Gabungkan semua data dengan urutan yang benar
            full_data = (self.SIGNATURE + 
                        metadata_size_bytes + 
                        metadata + 
                        secret_data)
            
            print(f"✓ Total data untuk disisipkan: {len(full_data)} bytes")
            
            # Cek kapasitas
            capacity = self.calculate_capacity(n_lsb)
            if len(full_data) > capacity:
                print(f"✗ Error: Data terlalu besar ({len(full_data)} bytes) "
                      f"untuk kapasitas ({capacity} bytes)")
                return False
            
            print(f"✓ Kapasitas tersedia: {capacity} bytes")
            
            # Sisipkan data
            if not self._embed_bits(full_data, n_lsb, use_random, stego_key):
                return False
            
            # Simpan hasil
            return self.save_audio(output_file)
            
        except Exception as e:
            print(f"✗ Error embedding message: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_message(self, output_file: str, stego_key: str) -> bool:
        """Ekstrak pesan rahasia dari audio (FIXED)"""
        try:
            if self.audio_data is None:
                print("✗ Error: Audio data tidak dimuat")
                return False
            
            total_samples = self.audio_data.size
            print(f"Memulai ekstraksi dari {total_samples} samples...")
            
            # 1. Ekstrak signature (64 bits dengan 1-LSB berurutan)
            signature_bits = self._extract_bits_sequential(1, 0, len(self.SIGNATURE) * 8)
            signature_data = self._bits_to_bytes(signature_bits)
            
            print(f"Signature extracted: {signature_data.hex()}")
            print(f"Expected signature: {self.SIGNATURE.hex()}")
            
            if signature_data != self.SIGNATURE:
                print("✗ Error: Signature tidak valid. File mungkin tidak mengandung pesan tersembunyi.")
                return False
            
            print("✓ Signature valid ditemukan")
            
            # 2. Ekstrak metadata size (32 bits dengan 1-LSB berurutan)
            metadata_size_start_sample = len(self.SIGNATURE) * 8
            metadata_size_bits = self._extract_bits_sequential(1, metadata_size_start_sample, self.METADATA_SIZE_BYTES * 8)
            metadata_size_data = self._bits_to_bytes(metadata_size_bits)
            
            if len(metadata_size_data) < self.METADATA_SIZE_BYTES:
                print("✗ Error: Tidak dapat membaca ukuran metadata")
                return False
                
            metadata_size = struct.unpack('<I', metadata_size_data)[0]
            print(f"✓ Ukuran metadata: {metadata_size} bytes")
            
            if metadata_size > 10000 or metadata_size == 0:
                print(f"✗ Error: Ukuran metadata tidak valid: {metadata_size}")
                return False
            
            # 3. Ekstrak metadata (dengan 1-LSB berurutan)
            metadata_start_sample = metadata_size_start_sample + (self.METADATA_SIZE_BYTES * 8)
            metadata_bits = self._extract_bits_sequential(1, metadata_start_sample, metadata_size * 8)
            metadata_data = self._bits_to_bytes(metadata_bits)
            
            try:
                metadata = json.loads(metadata_data.decode('utf-8'))
                print("✓ Metadata berhasil dibaca")
                print(f"✓ Metadata: {metadata}")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"✗ Error parsing metadata: {e}")
                print(f"Metadata raw (hex): {metadata_data.hex()}")
                print(f"Metadata raw: {metadata_data[:100]}...")
                return False
            
            # Validasi metadata
            required_keys = ['file_size', 'n_lsb', 'encrypted', 'random_positions']
            if not all(key in metadata for key in required_keys):
                print(f"✗ Error: Metadata tidak lengkap")
                print(f"Metadata keys: {list(metadata.keys())}")
                return False
            
            n_lsb = metadata['n_lsb']
            use_random = metadata['random_positions']
            use_encryption = metadata['encrypted']
            file_size = metadata['file_size']
            
            print(f"✓ Parameter ekstraksi: n_lsb={n_lsb}, random={use_random}, encrypted={use_encryption}, file_size={file_size}")
            
            # 4. Ekstrak data rahasia dengan n-LSB
            data_start_sample = metadata_start_sample + (metadata_size * 8)
            data_bits_needed = file_size * 8
            
            print(f"✓ Memulai ekstraksi data dari sample {data_start_sample} dengan n_lsb={n_lsb}")
            
            if use_random:
                secret_bits = self._extract_bits_random(n_lsb, data_start_sample, 
                                            data_bits_needed, stego_key)
            else:
                secret_bits = self._extract_bits_sequential(n_lsb, data_start_sample, data_bits_needed)
            
            secret_data = self._bits_to_bytes(secret_bits)
            
            if len(secret_data) > file_size:
                secret_data = secret_data[:file_size]
                print(f"✓ Data dipotong ke {file_size} bytes")
            
            print(f"✓ Data rahasia diekstrak: {len(secret_data)} bytes")
            
            # Dekripsi jika diperlukan
            if use_encryption:
                print("✓ Mendekripsi data...")
                cipher = VigenereCipher(stego_key)
                secret_data = cipher.decrypt(secret_data)
                print(f"✓ Data terdekripsi: {len(secret_data)} bytes")
            
            # Simpan file
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(secret_data)
            
            original_name = metadata.get('original_name', 'file_terekstrak')
            original_ext = metadata.get('extension', '')
            print(f"✓ Pesan berhasil diekstrak ke: {output_file}")
            print(f"✓ File asli: {original_name}{original_ext}")
            print(f"✓ Ukuran: {len(secret_data)} bytes")
            
            return True
            
        except Exception as e:
            print(f"✗ Error extracting message: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def calculate_psnr(self, original_audio_path: str, stego_audio_path: str) -> Optional[float]:
        temp_files = []  # Track temporary files untuk cleanup
        
        try:
            # Validasi file exists
            if not os.path.exists(original_audio_path):
                print(f"✗ File asli tidak ditemukan: {original_audio_path}")
                return None
            
            if not os.path.exists(stego_audio_path):
                print(f"✗ File stego tidak ditemukan: {stego_audio_path}")
                return None
            
            print("Mempersiapkan file untuk perhitungan PSNR...")
            
            # Helper function untuk convert ke WAV jika diperlukan
            def ensure_wav(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.wav':
                    print(f"✓ {os.path.basename(file_path)} sudah format WAV")
                    return file_path, False  # Return path dan flag bukan temporary
                
                # Bukan WAV, perlu konversi
                print(f"⚠ {os.path.basename(file_path)} bukan WAV, converting ke PCM...")
                
                # Load audio
                if ext == '.mp3':
                    audio = AudioSegment.from_mp3(file_path)
                elif ext == '.flac':
                    audio = AudioSegment.from_file(file_path, format="flac")
                elif ext == '.ogg':
                    audio = AudioSegment.from_ogg(file_path)
                else:
                    audio = AudioSegment.from_file(file_path)
                
                # Buat temporary WAV file
                import tempfile
                temp_fd, temp_path = tempfile.mkstemp(suffix='.wav', prefix='psnr_temp_')
                os.close(temp_fd)
                
                # Export ke WAV (PCM)
                audio.export(temp_path, format="wav")
                print(f"✓ Converted ke: {temp_path}")
                
                return temp_path, True  # Return path dan flag adalah temporary
            
            # Ensure kedua file adalah WAV
            original_wav_path, original_is_temp = ensure_wav(original_audio_path)
            stego_wav_path, stego_is_temp = ensure_wav(stego_audio_path)
            
            # Track temporary files untuk cleanup
            if original_is_temp:
                temp_files.append(original_wav_path)
            if stego_is_temp:
                temp_files.append(stego_wav_path)
            
            print("\n" + "="*50)
            print("Menghitung PSNR pada data PCM (WAV)...")
            print("="*50)
            
            # Load audio WAV (x[n] dan y[n])
            original_audio = AudioSegment.from_wav(original_wav_path)
            stego_audio = AudioSegment.from_wav(stego_wav_path)
            
            # Konversi ke numpy array (16-bit PCM)
            x = np.array(original_audio.get_array_of_samples(), dtype=np.int16)
            y = np.array(stego_audio.get_array_of_samples(), dtype=np.int16)
            
            # Info channel
            print(f"✓ Audio asli: {original_audio.channels} channel(s), {original_audio.frame_rate} Hz")
            print(f"✓ Audio stego: {stego_audio.channels} channel(s), {stego_audio.frame_rate} Hz")
            
            # Flatten jika stereo
            if original_audio.channels == 2:
                x = x.reshape(-1, 2).flatten()
            if stego_audio.channels == 2:
                y = y.reshape(-1, 2).flatten()
            
            # Align jumlah sampel (ambil minimum)
            N = min(len(x), len(y))
            x = x[:N]
            y = y[:N]
            
            print(f"✓ Jumlah sampel ter-align (N): {N:,}")
            
            # Hitung MSE = (1/N) * Σ(x[n] - y[n])²
            differences = x.astype(np.float64) - y.astype(np.float64)
            squared_diff = differences ** 2
            mse = np.sum(squared_diff) / N
            
            print(f"✓ MSE: {mse:.6f}")
            
            # Jika MSE = 0, audio identik (PSNR = infinity)
            if mse == 0:
                print("✓ MSE = 0, audio PCM identik!")
                return float('inf')
            
            # MAX untuk 16-bit PCM signed
            MAX = 32767.0
            
            # Hitung PSNR = 10 * log10(MAX² / MSE)
            psnr = 10 * np.log10((MAX ** 2) / mse)
            
            return psnr
            
        except Exception as e:
            print(f"✗ Error calculating PSNR: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # Cleanup temporary WAV files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"✓ Cleanup: {temp_file}")
                except Exception as e:
                    print(f"⚠ Warning: Gagal hapus temporary file {temp_file}: {e}")


def main():
    """Fungsi utama program"""
    print("=== Audio Steganography Program (FIXED - Support MP3/WAV/FLAC) ===")
    print("⚠ PENTING: MP3 menggunakan compression lossy yang dapat merusak data steganografi!")
    print("💡 REKOMENDASI: Gunakan format lossless (WAV, FLAC) untuk hasil terbaik")
    print("")
    print("1. Embed message")
    print("2. Extract message") 
    print("3. Calculate capacity")
    print("4. Calculate PSNR")
    
    choice = input("\nPilih opsi (1-4): ").strip()
    
    stego = AudioSteganography()
    
    if choice == '1':
        # Embed message
        print("\n=== EMBED MESSAGE ===")
        cover_file = input("Path file audio cover (MP3/WAV/FLAC): ").strip()
        if not stego.load_audio(cover_file):
            return
        
        secret_file = input("Path file pesan rahasia: ").strip()
        if not os.path.exists(secret_file):
            print("✗ File pesan rahasia tidak ditemukan!")
            return
        
        # Saran nama output berdasarkan format
        suggested_ext = '.wav' if cover_file.lower().endswith('.mp3') else os.path.splitext(cover_file)[1]
        output_file = input(f"Path output file stego (rekomen: *{suggested_ext}): ").strip()
        
        stego_key = input("Kunci stego (min 6 karakter): ").strip()
        
        if len(stego_key) < 6:
            print("✗ Kunci terlalu pendek! Minimal 6 karakter.")
            return
        
        try:
            n_lsb = int(input("Jumlah LSB (1-4): ").strip())
            if not 1 <= n_lsb <= 4:
                print("✗ Jumlah LSB harus antara 1-4!")
                return
        except ValueError:
            print("✗ Jumlah LSB harus angka!")
            return
        
        use_encryption = input("Gunakan enkripsi? (y/n): ").strip().lower() == 'y'
        use_random = input("Gunakan posisi acak? (y/n): ").strip().lower() == 'y'
        
        # Cek kapasitas
        capacity = stego.calculate_capacity(n_lsb)
        file_size = os.path.getsize(secret_file)
        
        print(f"\n✓ Kapasitas tersedia: {capacity} bytes")
        print(f"✓ Ukuran file rahasia: {file_size} bytes")
        
        if file_size > capacity:
            print("✗ Error: File terlalu besar untuk kapasitas yang tersedia!")
            print(f"  Perlu: {file_size} bytes, tersedia: {capacity} bytes")
            return
        
        if stego.embed_message(secret_file, output_file, stego_key, 
                              n_lsb, use_encryption, use_random):
            print("\n✅ PENYISIPAN BERHASIL!")
            
            if output_file.lower().endswith('.mp3'):
                actual_stego_file = output_file[:-4] + '_stego.wav'
                print("\n💡 Untuk PSNR, menggunakan file WAV yang dihasilkan")
            else:
                actual_stego_file = output_file
            
            # Hitung PSNR hanya jika cover juga WAV atau dapat dikonversi
            print("\n--- Menghitung PSNR ---")
            psnr = stego.calculate_psnr(cover_file, actual_stego_file)
            
            if psnr is not None:
                if psnr == float('inf'):
                    print("✓ PSNR: ∞ dB (identik)")
                else:
                    print(f"✓ PSNR: {psnr:.2f} dB")
                    if psnr < 30:
                        print("⚠ PSNR < 30 dB: Perubahan cukup signifikan")
                    elif psnr < 40:
                        print("✓ Kualitas: Baik (PSNR 30-40 dB)")
                    elif psnr < 50:
                        print("✓ Kualitas: Sangat Baik (PSNR 40-50 dB)")
                    else:
                        print("✓ Kualitas: Excellent (PSNR > 50 dB)")
        else:
            print("\n❌ PENYISIPAN GAGAL!")
    
    elif choice == '2':
        # Extract message
        print("\n=== EXTRACT MESSAGE ===")
        print("💡 Gunakan file WAV yang dihasilkan saat embedding untuk hasil terbaik")
        stego_file = input("Path file audio stego: ").strip()
        if not stego.load_audio(stego_file):
            return
        
        output_file = input("Path output file hasil ekstraksi: ").strip()
        stego_key = input("Kunci stego: ").strip()
        
        if stego.extract_message(output_file, stego_key):
            print("\n✅ EKSTRAKSI BERHASIL!")
        else:
            print("\n❌ EKSTRAKSI GAGAL!")
            if stego_file.lower().endswith('.mp3'):
                print("💡 Tips: Coba gunakan file WAV jika tersedia, karena MP3 lossy compression")
                print("         dapat merusak data steganografi.")
    
    elif choice == '3':
        # Calculate capacity
        print("\n=== CALCULATE CAPACITY ===")
        cover_file = input("Path file audio: ").strip()
        if not stego.load_audio(cover_file):
            return
        
        try:
            n_lsb = int(input("Jumlah LSB (1-4): ").strip())
            if not 1 <= n_lsb <= 4:
                print("✗ Jumlah LSB harus antara 1-4!")
                return
        except ValueError:
            print("✗ Jumlah LSB harus angka!")
            return
        
        capacity = stego.calculate_capacity(n_lsb)
        print(f"✓ Kapasitas penyisipan: {capacity} bytes ({capacity/1024:.2f} KB)")
    
    elif choice == '4':
        # Calculate PSNR
        print("\n=== CALCULATE PSNR ===")
        original_file = input("Path file audio asli: ").strip()
        stego_file = input("Path file audio stego: ").strip()
        
        if not stego.load_audio(stego_file):
            return
        
        psnr = stego.calculate_psnr(original_file)
        if psnr is not None:
            print("\n" + "="*50)
            if psnr == float('inf'):
                print("✅ PSNR: ∞ dB (audio PCM identik)")
            else:
                print(f"✅ PSNR: {psnr:.2f} dB")
                print("="*50)
                
                # Interpretasi (relatif untuk audio)
                if psnr < 30:
                    print("⚠ PSNR < 30 dB: Perbedaan cukup signifikan")
                elif psnr < 40:
                    print("✓ PSNR 30-40 dB: Perbedaan kecil")
                elif psnr < 50:
                    print("✓ PSNR 40-50 dB: Perbedaan sangat kecil")
                else:
                    print("✓ PSNR > 50 dB: Hampir identik")
        else:
            print("✗ Gagal menghitung PSNR!")
    
    else:
        print("✗ Pilihan tidak valid!")


if __name__ == "__main__":
    main()