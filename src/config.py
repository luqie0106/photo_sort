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
