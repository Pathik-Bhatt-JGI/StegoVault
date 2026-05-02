"""
Universal Steganography Suite
Hide any data inside any medium — text, image, audio, or video.
"""

import streamlit as st
import numpy as np
import struct
import os
import io
import json
import base64
import wave
import tempfile
import traceback
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import secrets

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StegoVault",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# STYLES  (cyberpunk dark theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #030508;
  --bg2:       #060C12;
  --bg3:       #0A1420;
  --bg4:       #0F1D2E;
  --panel:     #081018;
  --border:    rgba(0,255,179,0.08);
  --border2:   rgba(0,255,179,0.15);
  --border3:   rgba(0,255,179,0.25);
  --green:     #00FFB3;
  --green2:    #00CC8F;
  --cyan:      #00B8FF;
  --violet:    #7B61FF;
  --amber:     #FFD700;
  --red:       #FF3366;
  --orange:    #FF6B35;
  --t1:        #E8F0F8;
  --t2:        #7A95B0;
  --t3:        #3A5570;
  --t4:        #1E3348;
  --mono:      'Share Tech Mono', monospace;
  --display:   'Exo 2', sans-serif;
  --body:      'Rajdhani', sans-serif;
  --r1: 4px; --r2: 8px; --r3: 12px;
}

* { box-sizing: border-box; }
.stApp { background: var(--bg) !important; color: var(--t1); font-family: var(--body); }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.main .block-container { padding: 1.5rem 2rem 5rem; max-width: 1400px; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--green2); border-radius: 2px; }

.stApp::before {
  content: '';
  position: fixed; top:0; left:0; right:0; bottom:0;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(0,255,179,0.025) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(0,184,255,0.02) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 80%, rgba(123,97,255,0.015) 0%, transparent 50%);
  pointer-events: none; z-index: 0;
}
.stApp::after {
  content: '';
  position: fixed; top:0; left:0; right:0; bottom:0;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,179,0.005) 2px, rgba(0,255,179,0.005) 4px);
  pointer-events: none; z-index: 0;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

h1,h2,h3,h4 { font-family: var(--display) !important; font-weight: 700 !important; color: var(--t1) !important; }

.stButton > button {
  background: transparent !important; color: var(--green) !important;
  border: 1px solid var(--border2) !important;
  font-family: var(--mono) !important; font-size: 0.72rem !important;
  letter-spacing: 0.1em !important; text-transform: uppercase !important;
  border-radius: var(--r1) !important; padding: 0.5rem 1.2rem !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: rgba(0,255,179,0.06) !important;
  border-color: var(--green) !important;
  box-shadow: 0 0 20px rgba(0,255,179,0.1) !important;
}
.stButton > button[kind="primary"] {
  background: rgba(0,255,179,0.08) !important;
  border-color: var(--green) !important;
  box-shadow: 0 0 15px rgba(0,255,179,0.08) !important;
}
.stDownloadButton > button {
  background: transparent !important; color: var(--cyan) !important;
  border: 1px solid rgba(0,184,255,0.25) !important;
  font-family: var(--mono) !important; font-size: 0.72rem !important;
  letter-spacing: 0.1em !important; border-radius: var(--r1) !important;
}
.stDownloadButton > button:hover {
  background: rgba(0,184,255,0.06) !important; border-color: var(--cyan) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
  background: var(--bg3) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r1) !important; color: var(--t1) !important;
  font-family: var(--mono) !important; font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--border3) !important;
  box-shadow: 0 0 12px rgba(0,255,179,0.08) !important;
}
.stSelectbox > div > div {
  background: var(--bg3) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r1) !important; color: var(--t1) !important;
  font-family: var(--mono) !important; font-size: 0.82rem !important;
}
textarea {
  background: var(--bg3) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r1) !important; color: var(--t1) !important;
  font-family: var(--mono) !important; font-size: 0.78rem !important;
}
[data-testid="stFileUploader"] > div {
  background: var(--bg2) !important; border: 1px dashed var(--border2) !important;
  border-radius: var(--r2) !important; padding: 20px !important;
}

.stTextInput label, .stNumberInput label, .stSelectbox label,
.stTextArea label, .stCheckbox label, [data-testid="stWidgetLabel"] {
  font-family: var(--mono) !important; font-size: 0.62rem !important;
  letter-spacing: 0.12em !important; text-transform: uppercase !important;
  color: var(--t3) !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: transparent !important; gap: 0 !important;
  border-bottom: 1px solid var(--border) !important;
  margin-bottom: 24px !important; border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono) !important; font-size: 0.65rem !important;
  letter-spacing: 0.12em !important; text-transform: uppercase !important;
  color: var(--t3) !important; padding: 10px 20px !important;
  border-radius: 0 !important; background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] {
  color: var(--green) !important;
  border-bottom: 1px solid var(--green) !important;
  background: transparent !important;
}

[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important; background: var(--bg2) !important;
}
.streamlit-expanderHeader {
  font-family: var(--mono) !important; font-size: 0.72rem !important;
  color: var(--t2) !important; letter-spacing: 0.08em !important;
}

.stRadio > div { gap: 4px; }
.stRadio label {
  background: var(--bg2) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important; padding: 10px 14px !important;
  cursor: pointer !important; transition: all 0.15s ease;
}
.stRadio label:hover { border-color: var(--border2) !important; }
.stRadio [data-testid="stMarkdownContainer"] {
  font-family: var(--mono) !important; font-size: 0.72rem !important;
  color: var(--t2) !important;
}

.stCheckbox label { text-transform: none !important; font-size: 0.78rem !important; color: var(--t2) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 20px 0 !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r2) !important; }

/* Custom component styles */
.hero-banner {
  background: linear-gradient(135deg, var(--bg2) 0%, rgba(0,255,179,0.03) 50%, var(--bg2) 100%);
  border: 1px solid var(--border2);
  border-radius: var(--r3);
  padding: 28px 32px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.hero-banner::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--green), var(--cyan), transparent);
}
.hero-eyebrow {
  font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.25em;
  text-transform: uppercase; color: var(--green); margin-bottom: 10px;
}
.hero-title {
  font-family: var(--display); font-size: 2.4rem; font-weight: 800;
  letter-spacing: -0.03em; color: var(--t1); line-height: 1;
  margin-bottom: 8px;
}
.hero-title span { color: var(--green); }
.hero-sub { font-family: var(--body); color: var(--t2); font-size: 0.9rem; line-height: 1.6; }

.panel {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--r2); padding: 20px 22px; margin-bottom: 14px;
  position: relative; overflow: hidden;
}
.panel::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--green), transparent); opacity: 0.2;
}
.panel-title {
  font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.2em;
  text-transform: uppercase; color: var(--green); margin-bottom: 14px;
  padding-bottom: 8px; border-bottom: 1px solid var(--border);
}

.kpi { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--r2); padding: 16px 18px; }
.kpi-label { font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--t3); margin-bottom: 8px; }
.kpi-value { font-family: var(--display); font-size: 1.6rem; font-weight: 700; color: var(--green); }
.kpi-sub { font-family: var(--mono); font-size: 0.68rem; color: var(--t3); margin-top: 4px; }

.abox { background: var(--bg2); border: 1px solid var(--border); border-left: 2px solid;
  border-radius: 0 var(--r2) var(--r2) 0; padding: 12px 16px; margin: 10px 0;
  font-family: var(--mono); font-size: 0.72rem; line-height: 1.6; color: var(--t2); }
.abox-green { border-left-color: var(--green); }
.abox-amber { border-left-color: var(--amber); }
.abox-red   { border-left-color: var(--red); }
.abox-cyan  { border-left-color: var(--cyan); }

.bd { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 2px;
  font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.08em;
  background: var(--bg3); color: var(--t2); border: 1px solid var(--border); }
.bd-g { color: var(--green); border-color: rgba(0,255,179,0.2); background: rgba(0,255,179,0.05); }
.bd-c { color: var(--cyan);  border-color: rgba(0,184,255,0.2); background: rgba(0,184,255,0.05); }
.bd-a { color: var(--amber); border-color: rgba(255,215,0,0.2);  background: rgba(255,215,0,0.05); }
.bd-r { color: var(--red);   border-color: rgba(255,51,102,0.2); background: rgba(255,51,102,0.05); }

.success-box {
  background: rgba(0,255,179,0.04); border: 1px solid rgba(0,255,179,0.2);
  border-radius: var(--r2); padding: 18px 20px; margin: 12px 0;
}
.success-title { font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.15em;
  text-transform: uppercase; color: var(--green); margin-bottom: 8px; }
.success-content { font-family: var(--mono); font-size: 0.8rem; color: var(--t1);
  word-break: break-all; line-height: 1.7; }

.capacity-bar-wrap { background: var(--bg3); border-radius: 2px; height: 6px; overflow: hidden; margin: 8px 0; }
.capacity-bar { height: 100%; border-radius: 2px; transition: width 0.4s ease; }

.method-card {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: var(--r2); padding: 14px 16px; margin: 6px 0;
  cursor: pointer; transition: all 0.15s;
}
.method-card:hover { border-color: var(--border2); background: rgba(0,255,179,0.02); }

.step-indicator {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  background: rgba(0,255,179,0.1); border: 1px solid rgba(0,255,179,0.3);
  font-family: var(--mono); font-size: 0.65rem; color: var(--green);
  margin-right: 8px; flex-shrink: 0;
}

.warn-box {
  background: rgba(255,215,0,0.03); border: 1px solid rgba(255,215,0,0.15);
  border-left: 2px solid var(--amber); border-radius: 0 var(--r2) var(--r2) 0;
  padding: 12px 16px; margin: 10px 0;
  font-family: var(--mono); font-size: 0.7rem; color: var(--amber); line-height: 1.6;
}

@media (max-width: 768px) {
  .main .block-container { padding: 0.75rem 0.75rem 5rem; }
  .hero-title { font-size: 1.6rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CORE ENGINE  —  Binary / Metadata
# ─────────────────────────────────────────────

def file_to_binary(data: bytes) -> str:
    """Convert raw bytes to binary string (e.g. b'A' -> '01000001')."""
    return ''.join(format(byte, '08b') for byte in data)


def binary_to_file(bits: str) -> bytes:
    """Convert binary string back to raw bytes."""
    if len(bits) % 8 != 0:
        bits = bits[:len(bits) - (len(bits) % 8)]
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def add_metadata(payload: bytes, filename: str, extension: str) -> bytes:
    """
    Prepend a JSON header (terminated by b'\\x00\\x00') containing
    the original filename and extension, then the raw payload.
    """
    meta = json.dumps({"name": filename, "ext": extension}).encode("utf-8")
    return meta + b'\x00\x00' + payload


def extract_metadata(data: bytes) -> tuple[dict, bytes]:
    """Split off the JSON header and return (meta_dict, raw_payload)."""
    sep = data.find(b'\x00\x00')
    if sep == -1:
        raise ValueError("Metadata delimiter not found — wrong password or corrupt data?")
    meta = json.loads(data[:sep].decode("utf-8"))
    return meta, data[sep + 2:]


# ─────────────────────────────────────────────
# ENCRYPTION / DECRYPTION
# ─────────────────────────────────────────────

_SALT_LEN = 16
_NONCE_LEN = 12


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte AES key from a password using scrypt."""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))


def encrypt_data(data: bytes, password: str) -> bytes:
    """AES-256-GCM encrypt; output = salt + nonce + ciphertext."""
    salt  = secrets.token_bytes(_SALT_LEN)
    nonce = secrets.token_bytes(_NONCE_LEN)
    key   = _derive_key(password, salt)
    ct    = AESGCM(key).encrypt(nonce, data, None)
    return salt + nonce + ct


def decrypt_data(data: bytes, password: str) -> bytes:
    """AES-256-GCM decrypt."""
    salt  = data[:_SALT_LEN]
    nonce = data[_SALT_LEN:_SALT_LEN + _NONCE_LEN]
    ct    = data[_SALT_LEN + _NONCE_LEN:]
    key   = _derive_key(password, salt)
    return AESGCM(key).decrypt(nonce, ct, None)


# ─────────────────────────────────────────────
# TEXT ↔ TEXT  (zero-width Unicode steganography)
# ─────────────────────────────────────────────

ZW_SPACE = '\u200B'   # 0
ZW_NJOINER = '\u200C'  # 1
ZW_JOINER = '\u200D'   # separator between bytes (readability)


def encode_text(cover: str, secret_bytes: bytes) -> str:
    """
    Hide secret_bytes inside cover using zero-width characters.
    ZW_SPACE = bit 0, ZW_NJOINER = bit 1, ZW_JOINER = byte separator.
    A length prefix (4 bytes big-endian) is prepended so we know
    exactly how many bytes to extract on decode.
    """
    length_prefix = struct.pack('>I', len(secret_bytes))
    all_bytes = length_prefix + secret_bytes
    parts = []
    for b in all_bytes:
        for bit in format(b, '08b'):
            parts.append(ZW_NJOINER if bit == '1' else ZW_SPACE)
        parts.append(ZW_JOINER)           # byte separator
    hidden = ''.join(parts)
    # Insert the hidden string right after the first character of cover
    if len(cover) == 0:
        return hidden
    return cover[0] + hidden + cover[1:]


def decode_text(encoded: str) -> bytes:
    """
    Extract hidden bytes from a zero-width encoded string.
    Returns raw bytes; caller is responsible for interpreting them.
    """
    zw_chars = {ZW_SPACE, ZW_NJOINER, ZW_JOINER}
    bits_per_byte = []
    current_bits = []

    for ch in encoded:
        if ch == ZW_SPACE:
            current_bits.append('0')
        elif ch == ZW_NJOINER:
            current_bits.append('1')
        elif ch == ZW_JOINER:
            if len(current_bits) == 8:
                bits_per_byte.append(''.join(current_bits))
            current_bits = []

    if not bits_per_byte:
        raise ValueError("No hidden data found in the provided text.")

    all_bytes = bytes(int(b, 2) for b in bits_per_byte)
    if len(all_bytes) < 4:
        raise ValueError("Hidden data too short — possibly corrupt.")
    length = struct.unpack('>I', all_bytes[:4])[0]
    return all_bytes[4: 4 + length]


# ─────────────────────────────────────────────
# IMAGE  LSB  steganography
# ─────────────────────────────────────────────

_IMG_MAGIC = b'STGV1'   # 5-byte magic marker
_IMG_LEN_BYTES = 4      # 4-byte big-endian length after magic


def encode_image(img: Image.Image, payload: bytes) -> Image.Image:
    """
    Embed payload into a PIL Image using LSB substitution.
    Format: MAGIC (5B) + LEN (4B) + DATA
    Uses the LSB of every colour channel of every pixel.
    """
    img = img.convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    flat = pixels.flatten()

    data = _IMG_MAGIC + struct.pack('>I', len(payload)) + payload
    bits = file_to_binary(data)

    capacity = len(flat)
    if len(bits) > capacity:
        raise ValueError(
            f"Cover image too small.  Need {len(bits)} bits, "
            f"have {capacity} bits ({capacity // 8} bytes)."
        )

    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)

    new_pixels = flat.reshape(pixels.shape)
    return Image.fromarray(new_pixels, "RGB")


def decode_image(img: Image.Image) -> bytes:
    """Extract LSB-encoded payload from a PIL Image."""
    img = img.convert("RGB")
    flat = np.array(img, dtype=np.uint8).flatten()
    bits = ''.join(str(b & 1) for b in flat)

    # Read magic (5 bytes = 40 bits)
    magic_bits  = 40
    len_bits    = 32
    magic = binary_to_file(bits[:magic_bits])
    if magic != _IMG_MAGIC:
        raise ValueError("No StegVault signature found.  Wrong image?")

    length = struct.unpack('>I', binary_to_file(bits[magic_bits:magic_bits + len_bits]))[0]
    start  = magic_bits + len_bits
    end    = start + length * 8
    return binary_to_file(bits[start:end])


# ─────────────────────────────────────────────
# AUDIO  LSB  steganography  (WAV)
# ─────────────────────────────────────────────

_WAV_MAGIC = b'SGAV1'


def encode_audio(wav_bytes: bytes, payload: bytes) -> bytes:
    """
    Embed payload into a WAV file using LSB of audio samples.
    Input/output are raw bytes of a WAV file.
    """
    with io.BytesIO(wav_bytes) as bio:
        with wave.open(bio, 'rb') as wf:
            params     = wf.getparams()
            n_frames   = wf.getnframes()
            samp_width = wf.getsampwidth()
            raw        = wf.readframes(n_frames)

    samples = np.frombuffer(raw, dtype=np.uint8).copy()
    data    = _WAV_MAGIC + struct.pack('>I', len(payload)) + payload
    bits    = file_to_binary(data)

    if len(bits) > len(samples):
        raise ValueError(
            f"Audio too short.  Need {len(bits)} bits, have {len(samples)}."
        )

    for i, bit in enumerate(bits):
        samples[i] = (samples[i] & 0xFE) | int(bit)

    out_io = io.BytesIO()
    with wave.open(out_io, 'wb') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(samples.tobytes())
    return out_io.getvalue()


def decode_audio(wav_bytes: bytes) -> bytes:
    """Extract LSB-encoded payload from a WAV file."""
    with io.BytesIO(wav_bytes) as bio:
        with wave.open(bio, 'rb') as wf:
            raw = wf.readframes(wf.getnframes())

    samples = np.frombuffer(raw, dtype=np.uint8)
    bits    = ''.join(str(b & 1) for b in samples)

    magic = binary_to_file(bits[:40])
    if magic != _WAV_MAGIC:
        raise ValueError("No StegVault audio signature found.")

    length = struct.unpack('>I', binary_to_file(bits[40:72]))[0]
    return binary_to_file(bits[72: 72 + length * 8])


# ─────────────────────────────────────────────
# VIDEO  steganography  (MP4 via OpenCV)
# ─────────────────────────────────────────────

def encode_video(video_bytes: bytes, payload: bytes) -> bytes:
    """
    Embed payload into the first N frames of an MP4 using LSB on blue channel.
    Writes a MAGIC + LEN header in frame 0 before the actual data.
    """
    try:
        import cv2
    except ImportError:
        raise ImportError("OpenCV (cv2) is required for video steganography.")

    _VID_MAGIC = b'SGVD1'
    data  = _VID_MAGIC + struct.pack('>I', len(payload)) + payload
    bits  = file_to_binary(data)
    bit_i = 0
    total = len(bits)

    # Write to temp file (OpenCV needs a path)
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_in:
        tmp_in.write(video_bytes)
        in_path = tmp_in.name

    out_path = in_path.replace('.mp4', '_steg.mp4')

    cap  = cv2.VideoCapture(in_path)
    fps  = cap.get(cv2.CAP_PROP_FPS) or 24
    fw   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fh   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out  = cv2.VideoWriter(out_path, fourcc, fps, (fw, fh))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if bit_i < total:
            flat = frame[:, :, 0].flatten().copy()  # blue channel
            embed_count = min(len(flat), total - bit_i)
            for j in range(embed_count):
                flat[j] = (flat[j] & 0xFE) | int(bits[bit_i])
                bit_i += 1
            frame[:, :, 0] = flat.reshape(fh, fw)
        out.write(frame)

    cap.release()
    out.release()

    if bit_i < total:
        os.unlink(in_path)
        os.unlink(out_path)
        raise ValueError("Video too short to hold all payload data.")

    with open(out_path, 'rb') as f:
        result = f.read()
    os.unlink(in_path)
    os.unlink(out_path)
    return result


def decode_video(video_bytes: bytes) -> bytes:
    """Extract LSB-encoded payload from an MP4 video."""
    try:
        import cv2
    except ImportError:
        raise ImportError("OpenCV (cv2) is required for video steganography.")

    _VID_MAGIC = b'SGVD1'
    bits = []

    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        flat = frame[:, :, 0].flatten()
        bits.extend([str(b & 1) for b in flat])
        # Early exit once we have enough
        if len(bits) >= (40 + 32 + 0):
            bit_str = ''.join(bits)
            if len(bit_str) >= 72:
                try:
                    magic = binary_to_file(bit_str[:40])
                    if magic == _VID_MAGIC:
                        length = struct.unpack('>I', binary_to_file(bit_str[40:72]))[0]
                        needed = 72 + length * 8
                        if len(bit_str) >= needed:
                            break
                except Exception:
                    pass
    cap.release()
    os.unlink(tmp_path)

    bit_str = ''.join(bits)
    magic = binary_to_file(bit_str[:40])
    if magic != _VID_MAGIC:
        raise ValueError("No StegVault video signature found.")
    length = struct.unpack('>I', binary_to_file(bit_str[40:72]))[0]
    return binary_to_file(bit_str[72: 72 + length * 8])


# ─────────────────────────────────────────────
# CAPACITY HELPERS
# ─────────────────────────────────────────────

def image_capacity_bytes(img: Image.Image) -> int:
    img = img.convert("RGB")
    pixels = np.array(img)
    return (pixels.size - len(_IMG_MAGIC) - _IMG_LEN_BYTES)


def audio_capacity_bytes(wav_bytes: bytes) -> int:
    try:
        with io.BytesIO(wav_bytes) as bio:
            with wave.open(bio, 'rb') as wf:
                n = wf.getnframes() * wf.getsampwidth() * wf.getnchannels()
        return (n - len(_WAV_MAGIC) - 4)
    except Exception:
        return 0


# ─────────────────────────────────────────────
# MIME / DOWNLOAD HELPERS
# ─────────────────────────────────────────────

_MIME_MAP = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "gif": "image/gif", "bmp": "image/bmp", "webp": "image/webp",
    "wav": "audio/wav", "mp3": "audio/mpeg", "ogg": "audio/ogg",
    "mp4": "video/mp4", "avi": "video/x-msvideo", "mkv": "video/x-matroska",
    "pdf": "application/pdf", "zip": "application/zip",
    "txt": "text/plain", "json": "application/json",
}


def mime_for(ext: str) -> str:
    return _MIME_MAP.get(ext.lower().lstrip('.'), "application/octet-stream")


def fmt_bytes(n: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────

def panel(title: str, content_fn):
    st.markdown(f"""<div class="panel"><div class="panel-title">{title}</div>""",
                unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def abox(msg: str, kind: str = "green"):
    st.markdown(f'<div class="abox abox-{kind}">{msg}</div>', unsafe_allow_html=True)


def warn(msg: str):
    st.markdown(f'<div class="warn-box">⚠ {msg}</div>', unsafe_allow_html=True)


def capacity_display(used: int, total: int, label: str = "Capacity"):
    pct = min(100, used / max(total, 1) * 100)
    color = "#00FFB3" if pct < 70 else "#FFD700" if pct < 90 else "#FF3366"
    st.markdown(f"""
    <div style="margin:12px 0">
      <div style="display:flex;justify-content:space-between;font-family:var(--mono);
                  font-size:0.65rem;color:var(--t3);margin-bottom:4px">
        <span>{label}</span>
        <span style="color:{'var(--amber)' if pct>70 else 'var(--green)'}">{pct:.1f}%</span>
      </div>
      <div class="capacity-bar-wrap">
        <div class="capacity-bar"
             style="width:{pct:.1f}%;background:{color};"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-family:var(--mono);
                  font-size:0.6rem;color:var(--t4);margin-top:3px">
        <span>Used: {fmt_bytes(used)}</span>
        <span>Max: {fmt_bytes(total)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def copy_button_js(text: str, btn_label: str = "Copy Encoded Text"):
    """Render a JS-powered copy button for arbitrary text (incl. zero-width chars)."""
    b64 = base64.b64encode(text.encode("utf-8")).decode()
    uid = secrets.token_hex(4)
    st.markdown(f"""
    <script>
    function copySteg_{uid}() {{
        var raw = atob("{b64}");
        var arr = new Uint8Array(raw.length);
        for (var i=0;i<raw.length;i++) arr[i]=raw.charCodeAt(i);
        var blob = new Blob([arr],{{type:"text/plain;charset=utf-8"}});
        var item = new ClipboardItem({{"text/plain":blob}});
        navigator.clipboard.write([item]).then(function(){{
            document.getElementById('cp_btn_{uid}').textContent = '✓ Copied!';
            setTimeout(function(){{document.getElementById('cp_btn_{uid}').textContent='{btn_label}';}},2000);
        }});
    }}
    </script>
    <button id="cp_btn_{uid}" onclick="copySteg_{uid}()"
      style="background:transparent;color:#00FFB3;border:1px solid rgba(0,255,179,0.25);
             font-family:'Share Tech Mono',monospace;font-size:0.72rem;letter-spacing:0.1em;
             text-transform:uppercase;border-radius:4px;padding:8px 18px;cursor:pointer;
             transition:all 0.2s;margin-top:8px"
      onmouseover="this.style.background='rgba(0,255,179,0.06)'"
      onmouseout="this.style.background='transparent'">
      {btn_label}
    </button>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
  <div class="hero-eyebrow">▸ Universal Steganography Suite  v2.0</div>
  <div class="hero-title">Stego<span>Vault</span></div>
  <div class="hero-sub">
    Hide any file inside any medium — text, image, audio, or video.<br>
    Zero-width Unicode · LSB pixel encoding · AES-256-GCM encryption.
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────

tab_enc, tab_dec, tab_about = st.tabs([
    "⬡  ENCODE  —  Hide Data",
    "⬡  DECODE  —  Reveal Data",
    "⬡  HOW IT WORKS",
])

# ═══════════════════════════════════════════════
#  ENCODE TAB
# ═══════════════════════════════════════════════

with tab_enc:
    # ── Step 1: Secret payload ──────────────────
    st.markdown("""<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--green);padding-bottom:8px;border-bottom:1px solid var(--border);
    margin-bottom:16px">
    <span style="background:rgba(0,255,179,0.1);border:1px solid rgba(0,255,179,0.25);
    border-radius:2px;padding:2px 7px;margin-right:8px">01</span>
    SECRET PAYLOAD — What do you want to hide?
    </div>""", unsafe_allow_html=True)

    payload_mode = st.radio(
        "Secret type",
        ["Type text message", "Upload any file"],
        horizontal=True,
        label_visibility="collapsed",
    )

    secret_bytes = None
    secret_filename = "secret.txt"
    secret_ext = "txt"

    if payload_mode == "Type text message":
        secret_text = st.text_area(
            "Secret message",
            placeholder="Enter the text you want to hide…",
            height=100,
        )
        if secret_text:
            secret_bytes = secret_text.encode("utf-8")
            st.markdown(f'<span class="bd bd-g">Payload size: {fmt_bytes(len(secret_bytes))}</span>',
                        unsafe_allow_html=True)
    else:
        secret_file = st.file_uploader(
            "Upload secret file (any type)",
            type=None,
            key="secret_uploader",
            help="Any file — image, PDF, audio, video, zip, etc."
        )
        if secret_file:
            secret_bytes = secret_file.read()
            secret_filename = secret_file.name
            secret_ext = os.path.splitext(secret_file.name)[1].lstrip('.')
            st.markdown(
                f'<span class="bd bd-g">{secret_file.name}</span>&nbsp;'
                f'<span class="bd bd-c">{secret_ext.upper()}</span>&nbsp;'
                f'<span class="bd">{fmt_bytes(len(secret_bytes))}</span>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 2: Encryption ──────────────────────
    st.markdown("""<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--green);padding-bottom:8px;border-bottom:1px solid var(--border);
    margin-bottom:16px">
    <span style="background:rgba(0,255,179,0.1);border:1px solid rgba(0,255,179,0.25);
    border-radius:2px;padding:2px 7px;margin-right:8px">02</span>
    ENCRYPTION  (OPTIONAL)
    </div>""", unsafe_allow_html=True)

    use_enc = st.checkbox("🔒 Encrypt payload with AES-256-GCM before embedding", value=False)
    enc_password = ""
    if use_enc:
        enc_password = st.text_input("Encryption password", type="password",
                                     placeholder="Strong passphrase…")
        if enc_password:
            abox("Payload will be encrypted.  You must remember this password to decode.", "cyan")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 3: Cover medium ────────────────────
    st.markdown("""<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--green);padding-bottom:8px;border-bottom:1px solid var(--border);
    margin-bottom:16px">
    <span style="background:rgba(0,255,179,0.1);border:1px solid rgba(0,255,179,0.25);
    border-radius:2px;padding:2px 7px;margin-right:8px">03</span>
    COVER MEDIUM — Where to hide it?
    </div>""", unsafe_allow_html=True)

    cover_type = st.selectbox(
        "Cover type",
        ["Text (Zero-Width Unicode)", "Image (LSB PNG/BMP)", "Audio (LSB WAV)", "Video (LSB MP4)"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dynamic cover UI ────────────────────────
    cover_text   = None
    cover_img    = None
    cover_wav    = None
    cover_vid    = None

    if cover_type == "Text (Zero-Width Unicode)":
        cover_text = st.text_area(
            "Cover text",
            value="Hello there!",
            height=80,
            help="Visible text. The secret is hidden as invisible zero-width chars inside it."
        )
        warn("Zero-width chars survive plain-text copy/paste but may be stripped by "
             "rich-text editors, email clients, and some social platforms (WhatsApp compresses images).")

    elif cover_type == "Image (LSB PNG/BMP)":
        cover_img_file = st.file_uploader(
            "Cover image (PNG or BMP preferred — JPEG will re-compress and destroy data)",
            type=["png", "bmp", "tiff"],
            key="cover_img",
        )
        if cover_img_file:
            cover_img = Image.open(cover_img_file)
            cap = image_capacity_bytes(cover_img)
            st.image(cover_img, caption=f"Cover: {cover_img_file.name}", use_container_width=True)
            if secret_bytes:
                capacity_display(len(secret_bytes), cap, "Payload vs Image Capacity")
                if len(secret_bytes) > cap:
                    abox(f"Payload too large! Max {fmt_bytes(cap)} for this image.", "red")
        warn("Always share the stego image as PNG.  Never re-compress.  "
             "WhatsApp & Instagram WILL destroy hidden data via JPEG compression.")

    elif cover_type == "Audio (LSB WAV)":
        cover_wav_file = st.file_uploader(
            "Cover WAV file (PCM WAV only — MP3 compression destroys LSB data)",
            type=["wav"],
            key="cover_wav",
        )
        if cover_wav_file:
            cover_wav = cover_wav_file.read()
            cap = audio_capacity_bytes(cover_wav)
            st.markdown(f'<span class="bd bd-g">Audio capacity: {fmt_bytes(cap)}</span>',
                        unsafe_allow_html=True)
            if secret_bytes:
                capacity_display(len(secret_bytes), cap, "Payload vs Audio Capacity")
                if len(secret_bytes) > cap:
                    abox(f"Payload too large! Max {fmt_bytes(cap)} for this audio file.", "red")
        warn("Keep the output as WAV.  Converting to MP3/AAC will destroy the hidden data.")

    elif cover_type == "Video (LSB MP4)":
        cover_vid_file = st.file_uploader(
            "Cover video (MP4)",
            type=["mp4", "avi"],
            key="cover_vid",
        )
        if cover_vid_file:
            cover_vid = cover_vid_file.read()
            st.markdown(f'<span class="bd bd-c">Video loaded: {fmt_bytes(len(cover_vid))}</span>',
                        unsafe_allow_html=True)
        warn("Video re-encoding (e.g. by YouTube, WhatsApp) will destroy hidden data.  "
             "Share the stego file directly without transcoding.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Encode button ────────────────────────────
    encode_btn = st.button("⬡  ENCODE  —  HIDE THE PAYLOAD", type="primary", use_container_width=True)

    if encode_btn:
        if not secret_bytes:
            abox("Please provide a secret message or file first.", "red")
        else:
            try:
                with st.spinner("Encoding…"):
                    # Build full payload: metadata + raw bytes
                    full_payload = add_metadata(secret_bytes, secret_filename, secret_ext)

                    # Optionally encrypt
                    if use_enc and enc_password:
                        full_payload = encrypt_data(full_payload, enc_password)
                        # Tag so decoder knows it's encrypted
                        full_payload = b'ENC:' + full_payload
                    elif use_enc and not enc_password:
                        abox("Please enter an encryption password or uncheck encryption.", "amber")
                        st.stop()

                    # ── TEXT cover ──
                    if cover_type == "Text (Zero-Width Unicode)":
                        if not cover_text:
                            abox("Please enter some cover text.", "amber")
                            st.stop()
                        result_text = encode_text(cover_text, full_payload)
                        st.markdown("""<div class="success-box">
                        <div class="success-title">✓ Encoding Successful — Text Output</div>
                        <div class="success-content">The encoded text visually looks identical to your cover text.
                        Zero-width Unicode characters carry the hidden payload invisibly.</div>
                        </div>""", unsafe_allow_html=True)
                        preview = result_text.replace('\u200B', '').replace('\u200C', '').replace('\u200D', '')
                        st.text_area("Encoded text (visual preview — hidden chars removed for display)",
                                     value=preview, height=80, disabled=True)
                        abox(f"Hidden payload: {fmt_bytes(len(full_payload))} · "
                             f"Zero-width chars embedded: {sum(1 for c in result_text if c in {chr(0x200B),chr(0x200C),chr(0x200D)})}", "green")
                        copy_button_js(result_text, "Copy Encoded Text (with hidden data)")
                        st.download_button(
                            label="⬡ Download Encoded Text File",
                            data=result_text.encode("utf-8"),
                            file_name="steg_encoded.txt",
                            mime="text/plain",
                        )

                    # ── IMAGE cover ──
                    elif cover_type == "Image (LSB PNG/BMP)":
                        if cover_img is None:
                            abox("Please upload a cover image.", "amber")
                            st.stop()
                        result_img = encode_image(cover_img, full_payload)
                        buf = io.BytesIO()
                        result_img.save(buf, format="PNG")
                        buf.seek(0)
                        out_bytes = buf.getvalue()
                        st.markdown("""<div class="success-box">
                        <div class="success-title">✓ Encoding Successful — Image Output</div>
                        <div class="success-content">The stego image is visually identical to the original.
                        Download and share as PNG only — never JPEG-compress.</div>
                        </div>""", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(cover_img, caption="Original", use_container_width=True)
                        with col2:
                            st.image(result_img, caption="Stego (hidden data inside)", use_container_width=True)
                        st.download_button(
                            label="⬡ Download Stego PNG",
                            data=out_bytes,
                            file_name="steg_encoded.png",
                            mime="image/png",
                        )

                    # ── AUDIO cover ──
                    elif cover_type == "Audio (LSB WAV)":
                        if cover_wav is None:
                            abox("Please upload a WAV file.", "amber")
                            st.stop()
                        result_wav = encode_audio(cover_wav, full_payload)
                        st.markdown("""<div class="success-box">
                        <div class="success-title">✓ Encoding Successful — Audio Output</div>
                        <div class="success-content">The stego WAV sounds identical to the original.
                        Share as WAV only — never convert to MP3/AAC.</div>
                        </div>""", unsafe_allow_html=True)
                        st.audio(result_wav, format="audio/wav")
                        st.download_button(
                            label="⬡ Download Stego WAV",
                            data=result_wav,
                            file_name="steg_encoded.wav",
                            mime="audio/wav",
                        )

                    # ── VIDEO cover ──
                    elif cover_type == "Video (LSB MP4)":
                        if cover_vid is None:
                            abox("Please upload a video file.", "amber")
                            st.stop()
                        result_vid = encode_video(cover_vid, full_payload)
                        st.markdown("""<div class="success-box">
                        <div class="success-title">✓ Encoding Successful — Video Output</div>
                        <div class="success-content">The stego video looks identical to the original.
                        Share the file directly — do not re-transcode.</div>
                        </div>""", unsafe_allow_html=True)
                        st.download_button(
                            label="⬡ Download Stego MP4",
                            data=result_vid,
                            file_name="steg_encoded.mp4",
                            mime="video/mp4",
                        )

            except Exception as e:
                abox(f"Error during encoding: {e}", "red")
                with st.expander("Debug traceback"):
                    st.code(traceback.format_exc())


# ═══════════════════════════════════════════════
#  DECODE TAB
# ═══════════════════════════════════════════════

with tab_dec:
    st.markdown("""<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--cyan);padding-bottom:8px;border-bottom:1px solid var(--border);
    margin-bottom:16px">
    <span style="background:rgba(0,184,255,0.1);border:1px solid rgba(0,184,255,0.25);
    border-radius:2px;padding:2px 7px;margin-right:8px">01</span>
    ENCODED MEDIUM — Paste or upload the stego carrier
    </div>""", unsafe_allow_html=True)

    dec_mode = st.radio(
        "Input mode",
        ["Paste encoded text", "Upload encoded file"],
        horizontal=True,
        label_visibility="collapsed",
        key="dec_mode",
    )

    encoded_text = None
    encoded_file_bytes = None
    encoded_type = None

    if dec_mode == "Paste encoded text":
        encoded_text = st.text_area(
            "Paste the encoded text here (zero-width characters will be invisible)",
            height=100,
            placeholder="Paste the text that contains hidden data…",
            key="paste_enc",
        )
        if encoded_text:
            zw_count = sum(1 for c in encoded_text if c in {'\u200B', '\u200C', '\u200D'})
            if zw_count > 0:
                abox(f"Detected {zw_count:,} hidden zero-width characters in the pasted text.", "green")
            else:
                abox("No zero-width characters detected.  Make sure you pasted the full encoded text.", "amber")
            encoded_type = "text"
    else:
        enc_file = st.file_uploader(
            "Upload encoded file (PNG, WAV, MP4, or TXT)",
            type=["png", "bmp", "tiff", "wav", "mp4", "avi", "txt"],
            key="dec_file",
        )
        if enc_file:
            encoded_file_bytes = enc_file.read()
            ext = os.path.splitext(enc_file.name)[1].lower()
            if ext in ('.png', '.bmp', '.tiff'):
                encoded_type = "image"
            elif ext == '.wav':
                encoded_type = "audio"
            elif ext in ('.mp4', '.avi'):
                encoded_type = "video"
            elif ext == '.txt':
                encoded_type = "text"
                encoded_text = encoded_file_bytes.decode("utf-8")
                zw_count = sum(1 for c in encoded_text if c in {'\u200B', '\u200C', '\u200D'})
                abox(f"Text file loaded. {zw_count:,} zero-width characters detected.", "green" if zw_count else "amber")
            st.markdown(
                f'<span class="bd bd-c">{enc_file.name}</span>&nbsp;'
                f'<span class="bd">{fmt_bytes(len(encoded_file_bytes))}</span>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Decryption ──────────────────────────────
    st.markdown("""<div style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--cyan);padding-bottom:8px;border-bottom:1px solid var(--border);
    margin-bottom:16px">
    <span style="background:rgba(0,184,255,0.1);border:1px solid rgba(0,184,255,0.25);
    border-radius:2px;padding:2px 7px;margin-right:8px">02</span>
    DECRYPTION (if payload was encrypted)
    </div>""", unsafe_allow_html=True)

    dec_password = st.text_input("Decryption password (leave blank if not encrypted)",
                                  type="password", key="dec_pw",
                                  placeholder="Enter password if used during encoding…")

    st.markdown("<br>", unsafe_allow_html=True)

    decode_btn = st.button("⬡  DECODE  —  REVEAL THE PAYLOAD", type="primary", use_container_width=True)

    if decode_btn:
        if encoded_type is None:
            abox("Please paste encoded text or upload an encoded file.", "red")
        else:
            try:
                with st.spinner("Decoding…"):
                    # ── Extract raw bytes from medium ──
                    if encoded_type == "text":
                        if not encoded_text:
                            abox("No text to decode.", "red")
                            st.stop()
                        raw = decode_text(encoded_text)

                    elif encoded_type == "image":
                        img = Image.open(io.BytesIO(encoded_file_bytes))
                        raw = decode_image(img)

                    elif encoded_type == "audio":
                        raw = decode_audio(encoded_file_bytes)

                    elif encoded_type == "video":
                        raw = decode_video(encoded_file_bytes)

                    # ── Decrypt if needed ──
                    is_encrypted = raw[:4] == b'ENC:'
                    if is_encrypted:
                        if not dec_password:
                            abox("This payload is encrypted.  Please enter the password.", "amber")
                            st.stop()
                        raw = decrypt_data(raw[4:], dec_password)

                    # ── Extract metadata + payload ──
                    meta, payload = extract_metadata(raw)
                    orig_name = meta.get("name", "recovered_file")
                    orig_ext  = meta.get("ext", "bin")

                    st.markdown(f"""<div class="success-box">
                    <div class="success-title">✓ Decoding Successful</div>
                    <div class="success-content">
                    Original file: <b>{orig_name}</b><br>
                    Extension: <b>.{orig_ext}</b><br>
                    Recovered size: <b>{fmt_bytes(len(payload))}</b><br>
                    Encrypted: <b>{'Yes' if is_encrypted else 'No'}</b>
                    </div></div>""", unsafe_allow_html=True)

                    # ── Display / download ──
                    # If text, show inline
                    if orig_ext in ('txt',) or (orig_ext == '' and len(payload) < 50_000):
                        try:
                            decoded_str = payload.decode("utf-8")
                            st.markdown('<div class="panel-title" style="margin-top:16px">RECOVERED MESSAGE</div>',
                                        unsafe_allow_html=True)
                            st.text_area("Recovered text", value=decoded_str, height=150, disabled=True)
                        except UnicodeDecodeError:
                            pass

                    # If image, preview
                    if orig_ext in ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'):
                        try:
                            rec_img = Image.open(io.BytesIO(payload))
                            st.image(rec_img, caption=f"Recovered: {orig_name}", use_container_width=True)
                        except Exception:
                            pass

                    # If audio, playback
                    if orig_ext in ('wav', 'mp3', 'ogg'):
                        st.audio(payload, format=mime_for(orig_ext))

                    # Always offer download
                    st.download_button(
                        label=f"⬡ Download Recovered File — {orig_name}",
                        data=payload,
                        file_name=orig_name,
                        mime=mime_for(orig_ext),
                    )

            except Exception as e:
                abox(f"Decoding failed: {e}", "red")
                with st.expander("Debug traceback"):
                    st.code(traceback.format_exc())


# ═══════════════════════════════════════════════
#  HOW IT WORKS TAB
# ═══════════════════════════════════════════════

with tab_about:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
<div class="panel">
<div class="panel-title">⬡ THE UNIVERSAL PIPELINE</div>
<div style="font-family:var(--mono);font-size:0.75rem;color:var(--t2);line-height:2.2">

<span style="color:var(--green)">ANY SECRET FILE</span>
<span style="color:var(--t4)"> ──────────────────</span>
<br>
&nbsp;&nbsp;↓ <span style="color:var(--t3)">file_to_binary() → raw bytes</span>
<br>
&nbsp;&nbsp;↓ <span style="color:var(--t3)">add_metadata() → name + extension prefix</span>
<br>
&nbsp;&nbsp;↓ <span style="color:var(--cyan)">encrypt_data() → AES-256-GCM (optional)</span>
<br>
&nbsp;&nbsp;↓ <span style="color:var(--violet)">embed into cover medium</span>
<br>
<br>
<span style="color:var(--green)">ENCODED CARRIER</span>  ← visually unchanged
<br><br>
<span style="color:var(--amber)">DECODE PATH (reverse)</span>
<br>
&nbsp;&nbsp;↓ extract bits from carrier
<br>
&nbsp;&nbsp;↓ <span style="color:var(--cyan)">decrypt_data() (if encrypted)</span>
<br>
&nbsp;&nbsp;↓ extract_metadata() → recover name/ext
<br>
&nbsp;&nbsp;↓ binary_to_file() → original bytes
<br>
<span style="color:var(--green)">ORIGINAL FILE RESTORED</span>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="panel">
<div class="panel-title">⬡ TEXT STEGANOGRAPHY — Zero-Width Unicode</div>
<div style="font-family:var(--mono);font-size:0.72rem;color:var(--t2);line-height:1.9">

Each byte of the payload is encoded as 8 invisible characters:<br>
<span style="color:var(--green)">U+200B (Zero Width Space)</span> = bit <b>0</b><br>
<span style="color:var(--amber)">U+200C (Zero Width Non-Joiner)</span> = bit <b>1</b><br>
<span style="color:var(--t3)">U+200D (Zero Width Joiner)</span> = byte separator<br><br>

A 4-byte length prefix ensures exact reconstruction.<br>
The hidden string is inserted after the first visible character.<br>
The output text looks <b>completely normal</b> to the human eye.
</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="panel">
<div class="panel-title">⬡ LSB IMAGE</div>
<div style="font-family:var(--mono);font-size:0.7rem;color:var(--t2);line-height:1.8">
Replaces the <b>least significant bit</b> of each RGB channel of each pixel.<br><br>
A 1920×1080 RGB image holds ≈ <span style="color:var(--green)">777 KB</span> of hidden data.<br><br>
The visual change is imperceptible (±1 in 0-255 range).
</div>
</div>

<div class="panel">
<div class="panel-title">⬡ LSB AUDIO (WAV)</div>
<div style="font-family:var(--mono);font-size:0.7rem;color:var(--t2);line-height:1.8">
Modifies the LSB of each audio sample byte.<br><br>
A 60-second 44.1 kHz stereo WAV holds ≈ <span style="color:var(--cyan)">10 MB</span>.<br><br>
The audio quality change is inaudible (SNR change &lt;0.01 dB).
</div>
</div>

<div class="panel">
<div class="panel-title">⬡ VIDEO (MP4 frames)</div>
<div style="font-family:var(--mono);font-size:0.7rem;color:var(--t2);line-height:1.8">
Extracts frames via OpenCV, modifies LSB of the blue channel.<br><br>
Capacity = frames × width × height bytes.<br><br>
A 10-sec 1080p video ≈ <span style="color:var(--violet)">hundreds of MB</span> capacity.
</div>
</div>

<div class="panel">
<div class="panel-title">⬡ ENCRYPTION</div>
<div style="font-family:var(--mono);font-size:0.7rem;color:var(--t2);line-height:1.8">
<b>AES-256-GCM</b> authenticated encryption.<br><br>
Key derivation: <b>scrypt</b> (N=16384, r=8, p=1).<br><br>
Random 16-byte salt + 12-byte nonce per encode.<br><br>
Even if the stego image is found, without the password the payload is unreadable.
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="warn-box">
⚠ PLATFORM WARNING<br><br>
WhatsApp, Instagram, Facebook, and most social platforms <b>recompress images and audio</b>
using lossy codecs.  This DESTROYS LSB-encoded data.<br><br>
Safe channels: email attachment, Telegram (as file not photo), direct file transfer, cloud storage.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding-top:16px;border-top:1px solid rgba(0,255,179,0.06);
text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.6rem;
color:rgba(58,85,112,0.6);letter-spacing:0.15em">
STEGOVAULT · UNIVERSAL STEGANOGRAPHY ENGINE · AES-256-GCM · LSB · ZERO-WIDTH UNICODE
</div>
""", unsafe_allow_html=True)
