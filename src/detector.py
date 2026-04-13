from pathlib import Path

from ultralytics import YOLO

from model_store import resolve_project_model_path


class YoloDetector:
    def __init__(self, model_name: str = "yolo26n.pt", confidence: float = 0.35) -> None:
        project_root = Path(__file__).resolve().parents[1]
        local_model_path = resolve_project_model_path(model_name=model_name, project_root=project_root)
        self.model = YOLO(str(local_model_path))
        self.model_path = local_model_path
        self.confidence = confidence

    def predict_labels(self, image_path: Path) -> list[str]:
        results = self.model.predict(str(image_path), conf=self.confidence, verbose=False)
        if not results:
            return []

        result = results[0]
        if result.boxes is None or result.boxes.cls is None:
            return []

        label_ids = [int(label_id) for label_id in result.boxes.cls.tolist()]
        labels = [result.names[label_id] for label_id in label_ids]
        return labels
