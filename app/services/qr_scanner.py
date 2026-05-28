"""QR code decoder service using OpenCV."""
import cv2
import numpy as np


def decode_qr(image_bytes: bytes) -> str | None:
    """Decodes QR code from image bytes. Returns the text if found, else None."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            return data.strip()
    except Exception:
        pass
    return None
