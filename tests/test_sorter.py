from pathlib import Path

from config import SortConfig
from sorter import AlbumSorter


class FakeDetector:
    def predict_labels(self, image_path: Path) -> list[str]:
        if "cat" in image_path.name:
            return ["cat"]
        return []


def test_sort_copy_mode(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()

    (source / "cat_001.jpg").write_bytes(b"data")
    (source / "random_001.jpg").write_bytes(b"data")

    config = SortConfig(source_dir=source, output_dir=output, copy_mode=True)
    sorter = AlbumSorter(config=config, detector=FakeDetector())

    summary = sorter.sort()

    assert summary == {"cat": 1, "unknown": 1}
    assert (output / "cat" / "cat_001.jpg").exists()
    assert (output / "unknown" / "random_001.jpg").exists()
    assert (source / "cat_001.jpg").exists()
