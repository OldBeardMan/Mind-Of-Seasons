"""Minecraft-style music manager — random tracks with silence gaps."""

import os
import random
import time

import pygame

from src.utils import resource_path

MUSIC_END_EVENT = pygame.USEREVENT + 10


class MusicManager:
    """Handles background music playback with random gaps between tracks."""

    def __init__(self, music_dir: str = "audio/music"):
        self._dir = resource_path(music_dir)
        self._tracks: list[str] = []
        self._last_track: str | None = None
        self._playing = False
        self._paused = False
        self._gap_min = 10  # seconds of silence between tracks
        self._gap_max = 30
        self._gap_end: float | None = None  # timestamp when gap ends
        self._volume = 0.6  # 0.0 – 1.0
        self._master = 0.8

        self._scan_tracks()
        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)

    # ------------------------------------------------------------------

    def _scan_tracks(self):
        if not os.path.isdir(self._dir):
            return
        self._tracks = sorted(
            os.path.join(self._dir, f)
            for f in os.listdir(self._dir)
            if f.endswith((".ogg", ".wav", ".mp3"))
        )

    def _pick_track(self) -> str | None:
        if not self._tracks:
            return None
        choices = [t for t in self._tracks if t != self._last_track]
        if not choices:
            choices = self._tracks
        return random.choice(choices)

    def _effective_volume(self) -> float:
        return (self._master / 100) * (self._volume / 100)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_volume(self, music_volume: int, master_volume: int | None = None):
        """Set volume (0-100 scale from settings)."""
        self._volume = music_volume
        if master_volume is not None:
            self._master = master_volume
        pygame.mixer.music.set_volume(self._effective_volume())

    def start(self):
        """Start music cycle — begins with a short gap then first track."""
        self._playing = True
        self._paused = False
        self._gap_end = time.time() + random.uniform(2, 5)

    def stop(self):
        """Stop music completely."""
        self._playing = False
        self._paused = False
        self._gap_end = None
        pygame.mixer.music.stop()

    def pause(self):
        if self._playing and not self._paused:
            self._paused = True
            pygame.mixer.music.pause()

    def resume(self):
        if self._playing and self._paused:
            self._paused = False
            pygame.mixer.music.unpause()

    def handle_event(self, event: pygame.event.Event):
        """Call from main event loop — detects track end."""
        if event.type == MUSIC_END_EVENT and self._playing and not self._paused:
            # Track finished → start silence gap
            gap = random.uniform(self._gap_min, self._gap_max)
            self._gap_end = time.time() + gap

    def update(self):
        """Call once per frame. Starts next track when gap expires."""
        if not self._playing or self._paused:
            return
        if self._gap_end is None:
            return
        if time.time() >= self._gap_end:
            self._gap_end = None
            self._play_next()

    def _play_next(self):
        track = self._pick_track()
        if not track:
            return
        self._last_track = track
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(self._effective_volume())
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Music error: {e}")
