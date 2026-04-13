import shutil
from collections import Counter
from pathlib import Path

from config import SortConfig
from detector import YoloDetector
from exif_reader import ExifReader


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"}
JXL_EXTENSION = ".jxl"


class AlbumSorter:
    def __init__(self, config: SortConfig, detector: YoloDetector, exif_reader: ExifReader | None = None) -> None:
        self.config = config
        self.detector = detector
        self.exif_reader = exif_reader or ExifReader()

    def sort(self) -> dict[str, int]:
        summary: Counter[str] = Counter()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        candidate_paths = self.config.source_dir.rglob("*") if self.config.recursive_scan else self.config.source_dir.iterdir()
        for image_path in sorted(candidate_paths):
            if self._is_inside_output_dir(image_path):
                continue

            if not image_path.is_file():
                continue

            suffix = image_path.suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS and suffix != JXL_EXTENSION:
                continue

            category = self._resolve_category(image_path=image_path, suffix=suffix)

            target_dir = self._build_target_dir(category=category, image_path=image_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / image_path.name

            if self.config.copy_mode:
                shutil.copy2(image_path, target_file)
            else:
                shutil.move(image_path, target_file)

            summary[category] += 1

        return dict(summary)

    def _resolve_category(self, image_path: Path, suffix: str) -> str:
        try:
            labels = self.detector.predict_labels(image_path)
        except Exception:
            if suffix == JXL_EXTENSION:
                return self.config.jpeg_xl_bucket
            return self.config.unknown_bucket

        if labels:
            return labels[0]
        if suffix == JXL_EXTENSION:
            return self.config.jpeg_xl_bucket
        return self.config.unknown_bucket

    def _is_inside_output_dir(self, file_path: Path) -> bool:
        try:
            file_path.resolve().relative_to(self.config.output_dir.resolve())
            return True
        except ValueError:
            return False

    def _build_target_dir(self, category: str, image_path: Path) -> Path:
        base_dir = self.config.output_dir / category
        if category not in self.config.scenic_categories:
            return base_dir

        metadata = self.exif_reader.read(image_path)
        camera = self._safe_dir_name(metadata.camera_model or self.config.unknown_camera_bucket)
        lens = self._safe_dir_name(metadata.lens_model or self.config.unknown_lens_bucket)
        return base_dir / camera / lens

    @staticmethod
    def _safe_dir_name(name: str) -> str:
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        clean_name = name
        for char in invalid_chars:
            clean_name = clean_name.replace(char, "_")
        return clean_name.strip() or "unknown"
