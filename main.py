import importlib
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"


def _ensure_src_on_path() -> None:
    if str(SRC_PATH) not in sys.path:
        sys.path.insert(0, str(SRC_PATH))


def _prompt_path(prompt: str) -> Path:
    while True:
        value = input(prompt).strip()
        path = Path(value).expanduser()
        if path.exists() and path.is_dir():
            return path
        print("路径无效，请输入存在的文件夹路径。")


def _prompt_optional_float(prompt: str, default: float) -> float:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("输入无效，使用默认值。")
        return default


def run_console() -> None:
    _ensure_src_on_path()
    sort_config = importlib.import_module("config").SortConfig
    detector_cls = importlib.import_module("detector").YoloDetector
    sorter_cls = importlib.import_module("sorter").AlbumSorter

    print("请输入要整理的目录信息：")
    source_dir = _prompt_path("源目录路径: ")
    output_dir = _prompt_path("目标目录路径: ")
    confidence = _prompt_optional_float("置信度(默认0.35): ", 0.35)
    unknown_bucket = input("未识别目录名(默认unknown): ").strip() or "unknown"
    copy_mode = (input("处理方式 copy/move (默认copy): ").strip().lower() or "copy") != "move"

    config = sort_config(
        source_dir=source_dir,
        output_dir=output_dir,
        model_name="yolo26n.pt",
        confidence=confidence,
        copy_mode=copy_mode,
        unknown_bucket=unknown_bucket,
    )

    try:
        detector = detector_cls(model_name=config.model_name, confidence=config.confidence)
    except FileNotFoundError as exc:
        print(f"自动下载模型失败: {exc}")
        local_model = input("请输入本地 .pt 模型路径（留空则退出）: ").strip()
        if not local_model:
            print("未提供本地模型，已退出。")
            return
        local_model_path = Path(local_model).expanduser()
        if not local_model_path.exists():
            print("本地模型路径无效，已退出。")
            return
        config.model_name = str(local_model_path)
        detector = detector_cls(model_name=config.model_name, confidence=config.confidence)

    sorter = sorter_cls(config=config, detector=detector)
    summary = sorter.sort()

    print(f"模型缓存路径: {detector.model_path}")
    if not summary:
        print("未发现支持的图片文件。")
        return

    print("整理完成：")
    for category, count in sorted(summary.items()):
        print(f"- {category}: {count}")


def run_gui_or_fallback(force_console: bool = False) -> None:
    _ensure_src_on_path()
    if force_console:
        run_console()
        return

    try:
        launch_gui = importlib.import_module("gui").launch_gui
        launch_gui()
    except Exception:
        print("GUI 启动失败，已切换到命令行交互模式。")
        run_console()


def _parse_force_console(args: list[str]) -> bool:
    return "--cli" in args


if __name__ == "__main__":
    run_gui_or_fallback(force_console=_parse_force_console(sys.argv[1:]))
