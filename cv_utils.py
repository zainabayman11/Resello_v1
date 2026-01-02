from PIL import Image
import imagehash
import io
import numpy as np
import cv2

try:
    import torch
    from transformers import CLIPProcessor, CLIPModel
except Exception:
    # If imports fail, set imported symbols to None so caller can detect
    CLIPModel = None
    CLIPProcessor = None
    torch = None

_model = None
_processor = None


def _load():
    global _model, _processor
    if _model is None:
        if CLIPModel is None or CLIPProcessor is None:
            raise RuntimeError("transformers or torch not available. Install requirements.txt")
        _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch14")
        _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch14")


def _to_image(image_bytes):
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def compute_embedding(image_bytes):
    _load()
    img = _to_image(image_bytes)
    inputs = _processor(images=img, return_tensors="pt")
    with torch.no_grad():
        img_feat = _model.get_image_features(**inputs)
        img_feat = img_feat / img_feat.norm(p=2, dim=-1, keepdim=True)
    return img_feat.cpu().numpy().reshape(-1)


def text_embedding(text):
    _load()
    inputs = _processor(text=[text], return_tensors="pt")
    with torch.no_grad():
        txt_feat = _model.get_text_features(**inputs)
        txt_feat = txt_feat / txt_feat.norm(p=2, dim=-1, keepdim=True)
    return txt_feat.cpu().numpy().reshape(-1)


def _cos_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def is_duplicate_embedding(a, b, thresh=0.95):
    return _cos_sim(a, b) >= thresh


def view_similarity_score(image_bytes, view_text):
    try:
        img_e = compute_embedding(image_bytes)
        txt_e = text_embedding(view_text)
        return _cos_sim(img_e, txt_e)
    except Exception:
        return 0.0


def analyze_damage(image_bytes):
    """Zero-shot damage detection using CLIP similarity. Returns list of issues.

    Each issue: {label, score, severity}
    """
    labels = ["scratches", "crack", "dent", "stain"]
    try:
        img_e = compute_embedding(image_bytes)
    except Exception:
        return []

    results = []
    for lab in labels:
        txt = f"a photo showing {lab}"
        txt_e = text_embedding(txt)
        score = _cos_sim(img_e, txt_e)
        if score > 0.25:
            if score > 0.40:
                sev = "high"
            elif score > 0.32:
                sev = "medium"
            else:
                sev = "low"
            results.append({"label": lab, "score": score, "severity": sev})
    return results


def is_blurry(image_bytes, thresh=100.0):
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True, 0.0
    lap = cv2.Laplacian(img, cv2.CV_64F)
    var = float(lap.var())
    return (var < thresh), var


def image_phash(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return imagehash.phash(img)


def is_duplicate_phash(h1, h2, max_bits_diff=6):
    # h1,h2 are imagehash objects or integers
    return (h1 - h2) <= max_bits_diff


# If core libraries are missing, export None for callable utilities so callers
# (like `app.py`) can detect unavailability and show friendly messages
if CLIPModel is None or CLIPProcessor is None or torch is None:
    compute_embedding = None
    text_embedding = None
    is_duplicate_embedding = None
    view_similarity_score = None
    analyze_damage = None
    is_blurry = None
    image_phash = None
    is_duplicate_phash = None

