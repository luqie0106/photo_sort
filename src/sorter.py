import shutil
from collections import Counter
from pathlib import Path

from config import SortConfig
from detector import YoloDetector


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"}


class AlbumSorter:
    def __init__(self, config: SortConfig, detector: YoloDetector) -> None:
        self.config = config
        self.detector = detector

    def sort(self) -> dict[str, int]:
        summary: Counter[str] = Counter()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        for image_path in sorted(self.config.source_dir.rglob("*")):
            if self._is_inside_output_dir(image_path):
                continue

            if not image_path.is_file() or image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            labels = self.detector.predict_labels(image_path)
            category = labels[0] if labels else self.config.unknown_bucket

            target_dir = self.config.output_dir / category
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / image_path.name

            if self.config.copy_mode:
                shutil.copy2(image_path, target_file)
            else:
                shutil.move(image_path, target_file)

            summary[category] += 1

        return dict(summary)

    def _is_inside_output_dir(self, file_path: Path) -> bool:
        try:
            file_path.resolve().relative_to(self.config.output_dir.resolve())
            return True
        except ValueError:
            return False
