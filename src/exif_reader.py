from dataclasses import dataclass
from pathlib import Path

from PIL import Image


EXIF_IFD_TAG = 34665
CAMERA_MODEL_TAG = 272
LENS_MODEL_TAG = 42036


@dataclass(slots=True)
class ExifMetadata:
    camera_model: str | None
    lens_model: str | None


class ExifReader:
    def read(self, image_path: Path) -> ExifMetadata:
        with Image.open(image_path) as image:
            exif = image.getexif()

        camera_model = self._normalize(exif.get(CAMERA_MODEL_TAG))
        lens_model = None

        if hasattr(exif, "get_ifd"):
            exif_ifd = exif.get_ifd(EXIF_IFD_TAG)
            if exif_ifd:
                lens_model = self._normalize(exif_ifd.get(LENS_MODEL_TAG))

        return ExifMetadata(camera_model=camera_model, lens_model=lens_model)

    @staticmethod
    def _normalize(value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode(errors="ignore")
        text = str(value).strip()
        return text or None
