from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SortConfig:
    source_dir: Path
    output_dir: Path
    model_name: str = "yolo26n.pt"
    confidence: float = 0.35
    copy_mode: bool = True
    unknown_bucket: str = "unknown"
    scenic_categories: tuple[str, ...] = ("scenery",)
    unknown_camera_bucket: str = "unknown_camera"
    unknown_lens_bucket: str = "unknown_lens"
    jpeg_xl_bucket: str = "jpeg-xl"
    recursive_scan: bool = False
