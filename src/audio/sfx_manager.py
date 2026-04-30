"""SFX manager — loads WAVs from audio/sfx/ and plays game events."""

import os
import random

import pygame

from src.utils import resource_path


class SfxManager:
    """Plays one-shot SFX and manages ambient loops on reserved channels."""

    CHANNEL_WIND = 0
    CHANNEL_WHISPER = 1
    CHANNEL_HEARTBEAT = 2

    def __init__(self, sfx_dir: str = "audio/sfx"):
        self._dir = resource_path(sfx_dir)
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._volume = 100
        self._master = 80

        pygame.mixer.set_num_channels(16)

        self._load_sounds()

        self._footstep_groups = {
            "grass": sorted(n for n in self._sounds if n.startswith("footstep_grass_")),
            "path": sorted(n for n in self._sounds if n.startswith("footstep_path_")),
            "cabin": sorted(n for n in self._sounds if n.startswith("footstep_cabin_")),
        }
        self._last_footstep: str | None = None

        self._loops: dict[str, int] = {}
        self._loop_scales: dict[str, float] = {}

    def _load_sounds(self):
        if not os.path.isdir(self._dir):
            return
        for fname in os.listdir(self._dir):
            if not fname.endswith(".wav"):
                continue
            name = os.path.splitext(fname)[0]
            try:
                self._sounds[name] = pygame.mixer.Sound(
                    os.path.join(self._dir, fname)
                )
            except Exception as e:
                print(f"SFX load error ({fname}): {e}")

    def _effective_volume(self, scale: float = 1.0) -> float:
        return (self._master / 100) * (self._volume / 100) * scale

    def set_volume(self, sfx_volume: int, master_volume: int | None = None):
        self._volume = sfx_volume
        if master_volume is not None:
            self._master = master_volume
        for name, ch_idx in self._loops.items():
            scale = self._loop_scales.get(name, 1.0)
            pygame.mixer.Channel(ch_idx).set_volume(self._effective_volume(scale))

    def play(self, name: str, scale: float = 1.0):
        s = self._sounds.get(name)
        if not s:
            return
        s.set_volume(self._effective_volume(scale))
        s.play()

    def play_footstep(self, surface: str):
        group = self._footstep_groups.get(surface) or self._footstep_groups.get("grass") or []
        if not group:
            return
        choices = [n for n in group if n != self._last_footstep] or group
        name = random.choice(choices)
        self._last_footstep = name
        self.play(name, scale=0.6)

    def start_loop(self, name: str, channel_idx: int, scale: float = 1.0):
        s = self._sounds.get(name)
        if not s:
            return
        if name in self._loops:
            self.set_loop_scale(name, scale)
            return
        self._loop_scales[name] = scale
        ch = pygame.mixer.Channel(channel_idx)
        ch.set_volume(self._effective_volume(scale))
        ch.play(s, loops=-1, fade_ms=400)
        self._loops[name] = channel_idx

    def set_loop_scale(self, name: str, scale: float):
        scale = max(0.0, min(1.0, scale))
        self._loop_scales[name] = scale
        ch_idx = self._loops.get(name)
        if ch_idx is not None:
            pygame.mixer.Channel(ch_idx).set_volume(self._effective_volume(scale))

    def stop_loop(self, name: str):
        ch_idx = self._loops.pop(name, None)
        self._loop_scales.pop(name, None)
        if ch_idx is not None:
            pygame.mixer.Channel(ch_idx).fadeout(300)

    def stop_all_loops(self):
        for name in list(self._loops.keys()):
            self.stop_loop(name)

    def pause_all(self):
        pygame.mixer.pause()

    def resume_all(self):
        pygame.mixer.unpause()
