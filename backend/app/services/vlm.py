import logging

import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from app.config import get_settings
from app.services.device import resolve_device

logger = logging.getLogger(__name__)

_vlm_instance: "VLMService | None" = None


class VLMService:
    IMAGE_PROMPT = (
        "请详细描述这张图片中的内容，包括可见文字、图表、结构和关键信息。"
        "输出简洁的中文描述，便于知识库检索。"
    )

    def __init__(self) -> None:
        self.settings = get_settings()
        self.device = resolve_device(self.settings.vlm_device)
        self._model = None
        self._processor = None

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._processor is not None:
            return

        model_path = self.settings.vlm_model_path
        logger.info("[vlm] loading %s on %s", model_path, self.device)

        model_kwargs: dict = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
        }
        if self.device == "cuda":
            model_kwargs["device_map"] = "auto"
        else:
            model_kwargs["device_map"] = None

        self._processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path, **model_kwargs)

        if self.device == "cpu" and model_kwargs.get("device_map") is None:
            self._model = self._model.to(self.device)

    def describe_image(self, image_path: str) -> str:
        self._ensure_loaded()
        assert self._model is not None
        assert self._processor is not None

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": self.IMAGE_PROMPT},
                ],
            }
        ]

        text = self._processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        try:
            from qwen_vl_utils import process_vision_info

            image_inputs, video_inputs = process_vision_info(messages)
        except ImportError as exc:
            raise RuntimeError("未安装 qwen-vl-utils，请运行: pip install qwen-vl-utils") from exc

        inputs = self._processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        device = next(self._model.parameters()).device
        inputs = inputs.to(device)

        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=self.settings.vlm_max_new_tokens,
                do_sample=False,
            )

        generated = output_ids[:, inputs["input_ids"].shape[-1] :]
        result = self._processor.batch_decode(
            generated,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return result[0].strip() if result else ""

    def unload(self) -> None:
        self._model = None
        self._processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def get_vlm_service() -> VLMService:
    global _vlm_instance
    if _vlm_instance is None:
        _vlm_instance = VLMService()
    return _vlm_instance


def unload_vlm_service() -> None:
    global _vlm_instance
    if _vlm_instance is not None:
        _vlm_instance.unload()
        _vlm_instance = None
