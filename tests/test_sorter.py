from pathlib import Path

from config import SortConfig
from sorter import AlbumSorter


class FakeDetector:
    def predict_labels(self, image_path: Path) -> list[str]:
        if "cat" in image_path.name:
            return ["cat"]
        if "scenery" in image_path.name:
            return ["scenery"]
        return []


class FakeExifReader:
    def read(self, image_path: Path):
        class Metadata:
            camera_model = "Sony A7C"
            lens_model = "FE 24-70mm F2.8"

        return Metadata()


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


def test_sort_scenery_with_camera_and_lens_subdirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()

    (source / "scenery_001.jpg").write_bytes(b"data")

    config = SortConfig(source_dir=source, output_dir=output, copy_mode=True)
    sorter = AlbumSorter(config=config, detector=FakeDetector(), exif_reader=FakeExifReader())

    summary = sorter.sort()

    assert summary == {"scenery": 1}
    assert (output / "scenery" / "Sony A7C" / "FE 24-70mm F2.8".replace("/", "_") / "scenery_001.jpg").exists()
