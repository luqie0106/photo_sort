import argparse
from pathlib import Path

from config import SortConfig
from detector import YoloDetector
from sorter import AlbumSorter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort photo albums with YOLO detection labels.")
    parser.add_argument("source", type=Path, help="Source folder containing photos")
    parser.add_argument("output", type=Path, help="Target folder for sorted photos")
    parser.add_argument("--model", default="yolo26n.pt", help="YOLO model file or model name")
    parser.add_argument("--conf", type=float, default=0.35, help="Confidence threshold")
    parser.add_argument("--move", action="store_true", help="Move files instead of copying")
    parser.add_argument("--recursive", action="store_true", help="Recursively process nested subfolders")
    parser.add_argument("--unknown-bucket", default="unknown", help="Folder name for unmatched images")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SortConfig(
        source_dir=args.source,
        output_dir=args.output,
        model_name=args.model,
        confidence=args.conf,
        copy_mode=not args.move,
        unknown_bucket=args.unknown_bucket,
        recursive_scan=args.recursive,
    )

    detector = YoloDetector(model_name=config.model_name, confidence=config.confidence)
    sorter = AlbumSorter(config=config, detector=detector)
    summary = sorter.sort()

    if not summary:
        print("No supported images found.")
        return

    print("Sorting complete:")
    for category, count in sorted(summary.items()):
        print(f"- {category}: {count}")


if __name__ == "__main__":
    main()
