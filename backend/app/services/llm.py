from functools import lru_cache

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.config import get_settings

THINK_CLOSE_TAG = "<" + "/think>"


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._tokenizer = None
        self._model = None

    def _resolve_device(self) -> str:
        if self.settings.llm_device != "auto":
            return self.settings.llm_device
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        device = self._resolve_device()
        model_kwargs: dict = {"trust_remote_code": True}

        if self.settings.llm_load_in_4bit and device == "cuda":
            try:
                from transformers import BitsAndBytesConfig

                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["device_map"] = "auto"
            except ImportError:
                model_kwargs["torch_dtype"] = torch.float16
                model_kwargs["device_map"] = "auto"
        else:
            model_kwargs["torch_dtype"] = torch.float16 if device == "cuda" else torch.float32
            model_kwargs["device_map"] = "auto" if device == "cuda" else None

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.settings.llm_model_path,
            trust_remote_code=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.settings.llm_model_path,
            **model_kwargs,
        )

        if device == "cpu" and model_kwargs.get("device_map") is None:
            self._model = self._model.to(device)

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        lowered = text.lower()
        if THINK_CLOSE_TAG in lowered:
            index = lowered.rfind(THINK_CLOSE_TAG)
            return text[index + len(THINK_CLOSE_TAG) :].strip()
        open_tag = "<" + "think>"
        if open_tag in lowered:
            index = lowered.find(open_tag)
            return text[:index].strip()
        return text.strip()

    def generate(self, prompt: str) -> str:
        self._ensure_loaded()
        assert self._tokenizer is not None
        assert self._model is not None

        messages = [{"role": "user", "content": prompt}]
        if hasattr(self._tokenizer, "apply_chat_template"):
            formatted = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            formatted = prompt

        inputs = self._tokenizer(formatted, return_tensors="pt")
        device = next(self._model.parameters()).device
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=self.settings.llm_max_new_tokens,
                temperature=self.settings.llm_temperature,
                do_sample=self.settings.llm_temperature > 0,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        generated = output_ids[0][inputs["input_ids"].shape[-1] :]
        text = self._tokenizer.decode(generated, skip_special_tokens=True)
        return self._strip_think_tags(text)


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()
