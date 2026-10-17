"""Asset manager with fallback placeholders for missing art assets."""

import pathlib
import pygame


class AssetManager:
    """Manages asset loading, caching, and safe procedural fallback placeholders."""

    def __init__(self, asset_dir: pathlib.Path) -> None:
        self.asset_dir: pathlib.Path = pathlib.Path(asset_dir)
        self._images: dict[str, pygame.Surface] = {}
        self._frames: dict[str, list[pygame.Surface]] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def _create_placeholder(self, size: tuple[int, int]) -> pygame.Surface:
        """Create a stylized square placeholder using pygame.draw."""
        w, h = max(1, size[0]), max(1, size[1])
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Procedural square with border and cross/gem
        color = (130, 80, 220, 220)
        border_color = (240, 210, 80, 255)
        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=max(2, min(w, h) // 8))
        pygame.draw.rect(surf, border_color, (0, 0, w, h), width=2, border_radius=max(2, min(w, h) // 8))
        return surf

    def image(self, relative_path: str, size: tuple[int, int] | None = None) -> pygame.Surface:
        """Retrieve an image by relative path or generate a safe procedural placeholder."""
        cache_key = f"{relative_path}_{size}"
        if cache_key in self._images:
            return self._images[cache_key]

        target_size = size or (48, 48)
        full_path = self.asset_dir / relative_path

        if full_path.is_file():
            try:
                loaded = pygame.image.load(str(full_path)).convert_alpha()
                if size is not None:
                    loaded = pygame.transform.smoothscale(loaded, size)
                self._images[cache_key] = loaded
                return loaded
            except Exception:
                pass

        # Safe placeholder fallback
        placeholder = self._create_placeholder(target_size)
        self._images[cache_key] = placeholder
        return placeholder

    def frames(self, relative_dir: str, size: tuple[int, int] | None = None) -> list[pygame.Surface]:
        """Retrieve a list of animation frames from a directory or return an empty frame list."""
        cache_key = f"{relative_dir}_{size}"
        if cache_key in self._frames:
            return self._frames[cache_key]

        full_dir = self.asset_dir / relative_dir
        frame_list: list[pygame.Surface] = []

        if full_dir.is_dir():
            files = sorted(
                [f for f in full_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")],
                key=lambda p: p.stem,
            )
            for f in files:
                try:
                    surf = pygame.image.load(str(f)).convert_alpha()
                    if size is not None:
                        surf = pygame.transform.smoothscale(surf, size)
                    frame_list.append(surf)
                except Exception:
                    pass

        self._frames[cache_key] = frame_list
        return frame_list

    def sound(self, relative_path: str) -> pygame.mixer.Sound | None:
        """Retrieve a sound effect or safely return None if absent."""
        if relative_path in self._sounds:
            return self._sounds[relative_path]

        full_path = self.asset_dir / relative_path
        if full_path.is_file() and pygame.mixer.get_init():
            try:
                snd = pygame.mixer.Sound(str(full_path))
                self._sounds[relative_path] = snd
                return snd
            except Exception:
                return None
        return None

    def clear(self) -> None:
        """Clear all cached surfaces and sounds."""
        self._images.clear()
        self._frames.clear()
        self._sounds.clear()
