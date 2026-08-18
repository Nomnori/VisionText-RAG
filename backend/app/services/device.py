import torch

from app.config import get_settings


def cuda_available() -> bool:
    return torch.cuda.is_available()


def resolve_device(preference: str = "auto") -> str:
    if preference not in ("auto", ""):
        return preference
    return "cuda" if cuda_available() else "cpu"


def get_gpu_info() -> dict:
    if not cuda_available():
        return {
            "cuda_available": False,
            "device_name": None,
            "device_count": 0,
            "capability": None,
        }

    device_index = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device_index)
    return {
        "cuda_available": True,
        "device_name": props.name,
        "device_count": torch.cuda.device_count(),
        "capability": f"{props.major}.{props.minor}",
        "total_memory_gb": round(props.total_memory / (1024**3), 2),
    }


def get_runtime_devices() -> dict:
    settings = get_settings()
    llm_device = resolve_device(settings.llm_device)
    embedding_device = resolve_device(settings.embedding_device)
    gpu = get_gpu_info()
    return {
        **gpu,
        "llm_device": llm_device,
        "embedding_device": embedding_device,
        "llm_load_in_4bit": settings.llm_load_in_4bit and llm_device == "cuda",
    }
