"""SentenceTransformer singleton + vector search helpers."""
import json
import os
import threading

from .. import config
from ..exceptions import BadRequestError

_model = None
_model_name = None
_lock = threading.Lock()


def load_model(model_path: str = None):
    """Load (and cache) the local SentenceTransformer model."""
    global _model, _model_name
    path = model_path or config.MODEL_PATH
    with _lock:
        if _model is None or _model_name != path:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(path)
            _model_name = path
    return _model


def encode(text: str, model_path: str = None) -> list[float]:
    model = load_model(model_path)
    return model.encode(text).tolist()


def encode_batch(texts: list[str], model_path: str = None) -> list[list[float]]:
    model = load_model(model_path)
    return model.encode(texts).tolist()


def _model_info(name: str, path: str) -> dict | None:
    config_path = os.path.join(path, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            model_config = json.load(file)
    except (OSError, ValueError):
        return None
    architectures = model_config.get("architectures") or []
    if not any(str(architecture).endswith("Model") for architecture in architectures):
        return None
    dimensions = model_config.get("hidden_size")
    if not isinstance(dimensions, int) or dimensions <= 0:
        return None
    return {
        "name": name,
        "path": path,
        "dims": dimensions,
        "default": os.path.normcase(path) == os.path.normcase(config.MODEL_PATH),
    }


def resolve_model(name: str | None) -> dict:
    model_name = name or os.path.basename(os.path.normpath(config.MODEL_PATH))
    model_path = os.path.join(config.MODELS_DIR, model_name)
    info = _model_info(model_name, model_path)
    if not info:
        raise BadRequestError(f"Embedding 模型不存在或不受支持: {model_name}")
    return info


def resolve_model_path(name: str | None) -> str:
    return resolve_model(name)["path"]


def available_models() -> list[dict]:
    """List local embedding models by scanning models/sentence-transformers/ subfolders."""
    root = config.MODELS_DIR
    result: list[dict] = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            sub = os.path.join(root, name)
            if not os.path.isdir(sub):
                continue
            info = _model_info(name, sub)
            if info:
                result.append(info)
    if not result:
        result.append(resolve_model(None))
    return result
