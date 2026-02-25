"""Generate synthesized sound effects for Mind of Seasons."""

import math
import os
import random
import struct
import wave

import numpy as np

SAMPLE_RATE = 44100
OUT_DIR = os.path.join(os.path.dirname(__file__), "audio", "sfx")
os.makedirs(OUT_DIR, exist_ok=True)


def save_wav(filename: str, samples: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Save float samples (-1..1) as 16-bit WAV."""
    path = os.path.join(OUT_DIR, filename)
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767).astype(np.int16)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(int_samples.tobytes())
    print(f"  -> {path}")


def envelope(length: int, attack: float = 0.01, decay: float = 0.1,
             sustain: float = 0.7, release: float = 0.2) -> np.ndarray:
    """ADSR envelope."""
    a = int(attack * length)
    d = int(decay * length)
    r = int(release * length)
    s = length - a - d - r
    if s < 0:
        s = 0
        r = length - a - d
    env = np.concatenate([
        np.linspace(0, 1, max(a, 1)),
        np.linspace(1, sustain, max(d, 1)),
        np.full(max(s, 0), sustain),
        np.linspace(sustain, 0, max(r, 1)),
    ])
    return env[:length]


def noise(length: int) -> np.ndarray:
    return np.random.uniform(-1, 1, length)


def sine(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def square(freq: float, duration: float) -> np.ndarray:
    return np.sign(sine(freq, duration))


def saw(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return 2 * (freq * t - np.floor(0.5 + freq * t))


# =========================================================================
# MOVEMENT
# =========================================================================

def gen_footstep_grass():
    """Short crunchy noise burst — grass step."""
    for i in range(4):
        dur = 0.08 + random.uniform(-0.01, 0.01)
        n = int(SAMPLE_RATE * dur)
        s = noise(n)
        # bandpass-ish: multiply by mid-freq sine
        freq = 800 + random.uniform(-100, 100)
        t = np.linspace(0, dur, n, endpoint=False)
        s = s * np.sin(2 * np.pi * freq * t)
        s *= envelope(n, attack=0.005, decay=0.02, sustain=0.3, release=0.4)
        s *= 0.5
        save_wav(f"footstep_grass_{i+1}.wav", s)


def gen_footstep_path():
    """Harder tap — wooden path."""
    for i in range(4):
        dur = 0.06
        n = int(SAMPLE_RATE * dur)
        freq = 300 + random.uniform(-30, 30)
        s = sine(freq, dur) * 0.6 + noise(n) * 0.15
        s *= envelope(n, attack=0.002, decay=0.01, sustain=0.2, release=0.5)
        s *= 0.6
        save_wav(f"footstep_path_{i+1}.wav", s)


def gen_footstep_cabin():
    """Wooden creak — cabin floor."""
    for i in range(4):
        dur = 0.1
        n = int(SAMPLE_RATE * dur)
        freq = 180 + random.uniform(-20, 20)
        s = sine(freq, dur) * 0.5 + sine(freq * 2.3, dur) * 0.2 + noise(n) * 0.1
        s *= envelope(n, attack=0.005, decay=0.03, sustain=0.3, release=0.5)
        s *= 0.5
        save_wav(f"footstep_cabin_{i+1}.wav", s)


# =========================================================================
# INTERACTIONS
# =========================================================================

def gen_item_pickup():
    """Short rising swoosh/plop for collectible."""
    dur = 0.25
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Rising frequency
    freq = 400 + 800 * (t / dur)
    s = np.sin(2 * np.pi * freq * t) * 0.5
    s += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2
    s *= envelope(n, attack=0.01, decay=0.05, sustain=0.6, release=0.3)
    s *= 0.6
    save_wav("item_pickup.wav", s)


def gen_npc_dialog():
    """Undertale-style blip for dialog text."""
    dur = 0.06
    n = int(SAMPLE_RATE * dur)
    s = square(440, dur) * 0.3
    s *= envelope(n, attack=0.005, decay=0.01, sustain=0.5, release=0.3)
    save_wav("dialog_blip.wav", s)


# =========================================================================
# COFFEE SYSTEM
# =========================================================================

def gen_coffee_brew():
    """3-second bubbling/gurgling sound."""
    dur = 3.0
    n = int(SAMPLE_RATE * dur)
    s = np.zeros(n)
    # Base: low rumble
    s += sine(80, dur) * 0.15
    # Bubbles: random short sine pops
    rng = np.random.default_rng(42)
    for _ in range(60):
        start = rng.integers(0, n - 2000)
        blen = rng.integers(400, 1500)
        freq = rng.uniform(200, 600)
        t_b = np.linspace(0, blen / SAMPLE_RATE, blen, endpoint=False)
        bubble = np.sin(2 * np.pi * freq * t_b)
        bubble *= envelope(blen, attack=0.05, decay=0.1, sustain=0.3, release=0.5)
        bubble *= rng.uniform(0.1, 0.3)
        end = min(start + blen, n)
        s[start:end] += bubble[:end - start]
    # Hiss layer
    hiss = noise(n) * 0.05
    t = np.linspace(0, dur, n, endpoint=False)
    hiss *= np.sin(2 * np.pi * 3000 * t)  # high freq filter
    s += hiss
    s *= envelope(n, attack=0.3, decay=0.1, sustain=0.8, release=0.2)
    s = np.clip(s, -1, 1) * 0.7
    save_wav("coffee_brew.wav", s)


def gen_coffee_drink():
    """Short gulp/slurp."""
    dur = 0.4
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Gulping: low freq modulated noise
    s = noise(n) * 0.4
    mod = np.sin(2 * np.pi * 8 * t)  # 8 Hz modulation
    s *= (0.5 + 0.5 * mod)
    s *= envelope(n, attack=0.02, decay=0.05, sustain=0.6, release=0.3)
    # Low thump at start
    thump_n = int(SAMPLE_RATE * 0.08)
    thump = sine(100, 0.08) * 0.5
    thump *= envelope(thump_n, attack=0.005, decay=0.02, sustain=0.2, release=0.6)
    s[:thump_n] += thump
    s = np.clip(s, -1, 1) * 0.6
    save_wav("coffee_drink.wav", s)


# =========================================================================
# CABIN
# =========================================================================

def gen_cat_place():
    """Soft thump for placing cat down."""
    dur = 0.2
    n = int(SAMPLE_RATE * dur)
    s = sine(120, dur) * 0.5 + noise(n) * 0.1
    s *= envelope(n, attack=0.005, decay=0.03, sustain=0.2, release=0.6)
    s *= 0.5
    save_wav("cat_place.wav", s)


def gen_door_creak():
    """Short door creak — frequency sweep with noise."""
    dur = 0.5
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Creaking: slow frequency wobble
    freq = 250 + 150 * np.sin(2 * np.pi * 3 * t)
    s = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE) * 0.4
    s += noise(n) * 0.08
    s *= envelope(n, attack=0.05, decay=0.1, sustain=0.6, release=0.3)
    s *= 0.5
    save_wav("door_creak.wav", s)


# =========================================================================
# UI / MENU
# =========================================================================

def gen_ui_hover():
    """Short tick for menu hover."""
    dur = 0.03
    n = int(SAMPLE_RATE * dur)
    s = square(1000, dur) * 0.25
    s *= envelope(n, attack=0.002, decay=0.005, sustain=0.3, release=0.5)
    save_wav("ui_hover.wav", s)


def gen_ui_confirm():
    """Melodic confirm — two rising notes."""
    dur = 0.15
    n = int(SAMPLE_RATE * dur)
    n_half = n // 2
    s1 = sine(523, dur / 2) * 0.4  # C5
    s1 *= envelope(n_half, attack=0.005, decay=0.02, sustain=0.6, release=0.3)
    s2 = sine(659, dur / 2) * 0.4  # E5
    s2 *= envelope(n_half, attack=0.005, decay=0.02, sustain=0.6, release=0.3)
    s = np.concatenate([s1, s2])
    save_wav("ui_confirm.wav", s)


def gen_inventory_open():
    """Paper rustling — filtered noise."""
    dur = 0.3
    n = int(SAMPLE_RATE * dur)
    s = noise(n)
    # Multiple bandpass via sine multiplication
    t = np.linspace(0, dur, n, endpoint=False)
    s = s * (np.sin(2 * np.pi * 2000 * t) * 0.4 + np.sin(2 * np.pi * 4000 * t) * 0.3)
    s *= envelope(n, attack=0.02, decay=0.05, sustain=0.5, release=0.4)
    s *= 0.4
    save_wav("inventory_open.wav", s)


# =========================================================================
# GAME OVER / TENSION
# =========================================================================

def gen_whisper_ambient():
    """Eerie whisper — breathy noise with slow modulation."""
    dur = 2.0
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    s = noise(n)
    # Breathy bandpass
    s = s * np.sin(2 * np.pi * 800 * t) * 0.3
    # Slow amplitude modulation for eeriness
    s *= (0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * t))
    s *= envelope(n, attack=0.2, decay=0.1, sustain=0.7, release=0.3)
    s *= 0.4
    save_wav("whisper_ambient.wav", s)


def gen_enemy_catch():
    """Loud whoosh + distorted noise burst for game over catch."""
    dur = 0.8
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Descending whoosh
    freq = 1200 - 1000 * (t / dur)
    whoosh = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE) * 0.5
    # Noise burst
    burst = noise(n) * 0.4
    s = whoosh + burst
    s *= envelope(n, attack=0.01, decay=0.05, sustain=0.7, release=0.3)
    s *= 0.7
    save_wav("enemy_catch.wav", s)


def gen_heartbeat():
    """Slowing heartbeat for fatigue death."""
    dur = 4.0
    n = int(SAMPLE_RATE * dur)
    s = np.zeros(n)
    # Heartbeat: pairs of thuds, gradually slowing
    beat_times = []
    t_pos = 0.0
    interval = 0.6
    while t_pos < dur - 0.3:
        beat_times.append(t_pos)
        beat_times.append(t_pos + 0.15)  # double-beat
        interval *= 1.15  # slow down
        t_pos += interval
    for bt in beat_times:
        start = int(bt * SAMPLE_RATE)
        beat_dur = 0.1
        bn = int(beat_dur * SAMPLE_RATE)
        if start + bn > n:
            break
        beat = sine(50, beat_dur) * 0.7
        beat *= envelope(bn, attack=0.005, decay=0.02, sustain=0.3, release=0.6)
        s[start:start + bn] += beat
    # Fade out overall
    s *= np.linspace(1, 0, n)
    s = np.clip(s, -1, 1) * 0.8
    save_wav("heartbeat.wav", s)


# =========================================================================
# AMBIENT
# =========================================================================

def gen_wind_loop():
    """Gentle wind loop — filtered noise with slow modulation."""
    dur = 5.0
    n = int(SAMPLE_RATE * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    s = noise(n)
    # Low-pass feel: multiply by low freq sines
    s = s * (np.sin(2 * np.pi * 300 * t) * 0.3 + np.sin(2 * np.pi * 150 * t) * 0.4)
    # Slow modulation
    s *= (0.4 + 0.6 * np.sin(2 * np.pi * 0.3 * t))
    # Smooth start and end for looping
    fade = int(SAMPLE_RATE * 0.5)
    s[:fade] *= np.linspace(0, 1, fade)
    s[-fade:] *= np.linspace(1, 0, fade)
    s *= 0.3
    save_wav("wind_loop.wav", s)


# =========================================================================

if __name__ == "__main__":
    print("Generating SFX for Mind of Seasons...\n")

    print("[Movement]")
    gen_footstep_grass()
    gen_footstep_path()
    gen_footstep_cabin()

    print("\n[Interactions]")
    gen_item_pickup()
    gen_npc_dialog()

    print("\n[Coffee]")
    gen_coffee_brew()
    gen_coffee_drink()

    print("\n[Cabin]")
    gen_cat_place()
    gen_door_creak()

    print("\n[UI]")
    gen_ui_hover()
    gen_ui_confirm()
    gen_inventory_open()

    print("\n[Game Over / Tension]")
    gen_whisper_ambient()
    gen_enemy_catch()
    gen_heartbeat()

    print("\n[Ambient]")
    gen_wind_loop()

    print("\nDone! All files in:", OUT_DIR)
