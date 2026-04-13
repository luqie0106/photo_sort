import os
import shutil
from pathlib import Path

from ultralytics.utils.downloads import attempt_download_asset


def resolve_project_model_path(model_name: str, project_root: Path) -> Path:
    project_root.mkdir(parents=True, exist_ok=True)
    target_path = project_root / Path(model_name).name

    if target_path.exists():
        return target_path

    input_path = Path(model_name)
    if input_path.exists():
        shutil.copy2(input_path, target_path)
        return target_path

    previous_cwd = Path.cwd()
    try:
        os.chdir(project_root)
        downloaded = Path(attempt_download_asset(Path(model_name).name))
    except Exception as exc:
        raise FileNotFoundError(
            f"Unable to download model '{model_name}'. Please place it at: {target_path}"
        ) from exc
    finally:
        os.chdir(previous_cwd)

    downloaded_path = downloaded.resolve()
    if downloaded_path != target_path.resolve():
        shutil.copy2(downloaded_path, target_path)

    return target_path
