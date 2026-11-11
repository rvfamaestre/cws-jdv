from pathlib import Path

import pygame

from constants import SFX_DIR


DEFAULT_SFX_NAMES = {
    "ui_select": "ui_select",
    "ui_back": "ui_back",
    "cell_place": "cell_place",
    "cell_remove": "cell_remove",
    "sim_start": "sim_start",
    "pause_toggle": "pause_toggle",
    "reset": "reset",
    "zone_set": "zone_set",
    "save": "save",
    "win": "win",
}

# Preferred order: WAV/OGG for game SFX latency, then MP3 fallback.
SUPPORTED_SFX_EXTENSIONS = (".wav", ".ogg", ".mp3")


class SoundManager:
    def __init__(self, sfx_dir=SFX_DIR):
        self.sfx_dir = Path(sfx_dir)
        self.enabled = False
        self.sounds = {}
        self.current_music = None
        self._init_mixer()
        self._load_default_sounds()

    def _init_mixer(self):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _resolve_sound_path(self, base_name):
        for ext in SUPPORTED_SFX_EXTENSIONS:
            candidate = self.sfx_dir / f"{base_name}{ext}"
            if candidate.is_file():
                return candidate
        return None

    def _resolve_music_path(self, track_name):
        if not track_name:
            return None

        track_path = Path(track_name)
        if track_path.is_absolute() and track_path.is_file():
            return track_path

        # Treat plain names (or relative names) as files inside the sfx directory.
        if track_path.suffix:
            candidate = self.sfx_dir / track_path
            if candidate.is_file():
                return candidate
            return None

        return self._resolve_sound_path(str(track_path))

    def _load_default_sounds(self):
        if not self.enabled:
            return
        for key, base_name in DEFAULT_SFX_NAMES.items():
            path = self._resolve_sound_path(base_name)
            if path is None:
                continue
            try:
                self.sounds[key] = pygame.mixer.Sound(str(path))
            except pygame.error:
                continue

    def play(self, key):
        if not self.enabled:
            return
        sound = self.sounds.get(key)
        if sound is not None:
            sound.play()

    def play_music(self, track_name, loops=-1):
        if not self.enabled:
            return

        music_path = self._resolve_music_path(track_name)
        if music_path is None:
            return

        path_str = str(music_path)
        if self.current_music == path_str and pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.load(path_str)
            pygame.mixer.music.play(loops)
            self.current_music = path_str
        except pygame.error:
            pass

    def stop_music(self):
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        self.current_music = None

    def missing_files(self):
        return [
            f"{base_name} ({', '.join(SUPPORTED_SFX_EXTENSIONS)})"
            for key, base_name in DEFAULT_SFX_NAMES.items()
            if key not in self.sounds
        ]
