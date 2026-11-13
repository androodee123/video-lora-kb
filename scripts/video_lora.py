"""Shared video-LoRA membership rules for H3 / Wan / LTX.

A row belongs in the knowledge base only if it is a LoRA-family adapter
(LORA, LoCon, DoRA, or an HF LoRA/IC-LoRA adapter) for a MiniMax H3, Wan,
or LTX *video* base, and can be stacked into T2V/I2V. Image LoRAs,
checkpoints, finetunes, merges, full base models, workflows, ControlNets
that are not LoRAs, VAEs, text encoders, GGUF packs, and other families
are out of scope.

Speed/distill *LoRAs* (lightx2v, CausVid, self-forcing LoRA packs) stay in.
This module never downloads weights.
"""
from __future__ import annotations

import re
from typing import Any

ADAPTER_TYPES = {"LORA", "LoRA", "LoCon", "DoRA", "LoHA", "LoKR", "LyCORIS"}

VIDEO_BASE_PREFIXES = (
    "MiniMax H3",
    "Wan Video",
    "Wan Video 1.3B",
    "LTXV",
    "LTXV2",
    "LTXV 2.3",
    "LTXV 2.5",
)

# Installed RAID filenames that are image LoRAs (or unverified image models)
# even if the same CivitAI page also publishes a video version.
INSTALLED_IMAGE_FILE_RX = re.compile(
    r"(?i)(?:^|/)(?:"
    r".*-krea2(?:-|\.|$)|"
    r".*_krea2(?:-|\.|$)|"
    r"minigirl-onahole-xl|"
    r".*z-image.*|"
    r".*zimage.*"
    r")"
)

LORA_TOKEN_RX = re.compile(
    r"(?i)(loras?|locon|dora|lokr|loha|lycoris|iclora|ic-lora|ic_lora|peft)"
)

DISTILL_RX = re.compile(r"(?i)(lightx2v|causvid|self-forcing|self_forcing)")

HF_VIDEO_BASE_RX = re.compile(
    r"(?i)(wan-?ai|wan2\.[12]|wan2_|wan21|wan22|wan-video|minimax-?h3|minimax_h3|"
    r"lightricks|ltx-?2|ltx-?video|ltxv)"
)

HF_WRONG_BASE_RX = re.compile(
    r"(?i)(hunyuan|hy1\.5|hy15|qwen3|qwen/|lingbot-video|cogvideox|"
    r"stable-diffusion|sdxl|flux\.1|z-image|krea-?2)"
)

VAE_RX = re.compile(r"(?i)(autoencoders?|(^|[-_/])vae($|[-_/])|text-encoder|t5-xxl)")
PROMPT_LORA_RX = re.compile(r"(?i)(prompt-rewriter|prompt_rewriter)")
WORKFLOW_RX = re.compile(r"(?i)workflow")
GGUF_RX = re.compile(r"(?i)gguf")
CONTROLNET_RX = re.compile(r"(?i)controlnet")
QUANT_RX = re.compile(r"(?i)(^|[-_/])(fp8|nvfp4|gguf|awq|gptq|exl2)($|[-_/])")
UPSCALER_PIPELINE_RX = re.compile(r"(?i)(latentupsample|spatial-upscaler|spatial_upscaler)")
SPACE_RX = re.compile(r"(?i)(^|/)spaces?(/|$)")


def is_video_base(base: str | None) -> bool:
    b = (base or "").strip()
    if not b:
        return False
    return b == "MiniMax H3" or b.startswith("Wan Video") or b.startswith("LTX")


def civitai_has_video_base(model: dict | None, rec_bases: list | None = None) -> bool:
    bases = list(rec_bases or [])
    if model:
        for v in model.get("modelVersions") or []:
            if v.get("baseModel"):
                bases.append(v["baseModel"])
    return any(is_video_base(b) for b in bases)


def civitai_is_adapter_type(model: dict | None) -> bool:
    if not model:
        return False
    return (model.get("type") or "") in ADAPTER_TYPES


def installed_file_is_image_lora(file: str | None, path: str | None = None) -> str | None:
    """Return a reason if this RAID filename is an image LoRA, else None."""
    blob = f"{path or ''} {file or ''}".replace("\\", "/")
    name = (file or "").split("/")[-1]
    path_s = (path or "").split("/")[-1]
    check = name or path_s
    if re.search(r"(?i)krea2", check):
        return "installed image LoRA (krea2/Krea 2 filename); not the video-base weights"
    if re.search(r"(?i)minigirl-onahole-xl", check):
        return "installed image LoRA (XL/Pony filename); the MiniMax H3 video version uses a different file"
    if re.search(r"(?i)z-image|zimage", check):
        return "filename indicates Z-Image (image model); not verified as a video LoRA"
    return None


def _tags_blob(tags) -> str:
    parts = []
    for t in tags or []:
        if isinstance(t, str):
            parts.append(t)
        elif isinstance(t, dict) and t.get("name"):
            parts.append(t["name"])
    return " ".join(parts)


def hf_is_video_lora(hf_id: str | None, tags=None, card: dict | None = None) -> tuple[bool, str | None]:
    """Return (keep, reason_if_dropped) for a Hugging Face repo."""
    hid = hf_id or ""
    name = hid.split("/")[-1]
    tag_s = _tags_blob(tags)
    ident = f"{hid} {tag_s}".lower()
    card = card or {}
    rel = (card.get("base_model_relation") or "")
    if isinstance(rel, str):
        rel = rel.lower()
    hf_bases = " ".join(card.get("hf_base_model") or [])
    base_blob = f"{ident} {hf_bases}".lower()

    if SPACE_RX.search(hid):
        return False, "space"
    if GGUF_RX.search(ident):
        return False, "gguf"
    if VAE_RX.search(name) or VAE_RX.search(hid):
        return False, "vae"
    if PROMPT_LORA_RX.search(ident):
        return False, "text_encoder_or_prompt_lora"
    if re.search(r"(?i)hunyuan|hy1\.5|hy15", ident) and not re.search(r"(?i)(wan|ltx|minimax)", name):
        return False, "non_target_family"
    if WORKFLOW_RX.search(name) and not re.search(r"(?i)lora", name.split("workflow")[0] if "workflow" in name.lower() else name):
        # "Foo-Workflow" or "Workflow_for_..._LoRA" is a workflow pack
        return False, "workflow"
    if WORKFLOW_RX.search(name):
        return False, "workflow"
    if CONTROLNET_RX.search(ident) and not LORA_TOKEN_RX.search(ident):
        return False, "controlnet_not_lora"
    if UPSCALER_PIPELINE_RX.search(ident) and not LORA_TOKEN_RX.search(name):
        return False, "upscaler_not_lora"

    has_lora_token = bool(
        LORA_TOKEN_RX.search(ident)
        or LORA_TOKEN_RX.search(name)
        or rel == "adapter"
        or "peft" in ident
    )
    # Official LTX IC-LoRAs sometimes omit a "lora" tag.
    if re.search(r"(?i)ic-?lora|iclora", hid):
        has_lora_token = True

    is_distill_lora = bool(DISTILL_RX.search(ident) and has_lora_token)
    is_lightx2v_lora = bool(
        re.search(r"(?i)lightx2v", hid)
        and has_lora_token
        and HF_VIDEO_BASE_RX.search(base_blob)
    )

    # Quantised *base* checkpoints (fp8/nvfp4 of LTX-2.3, Self-Forcing-FP8, etc.)
    if QUANT_RX.search(name) and not has_lora_token:
        return False, "quantised_checkpoint"
    if QUANT_RX.search(name) and not LORA_TOKEN_RX.search(name) and rel in ("finetune", "quantized", "quantised", "merge"):
        return False, "quantised_checkpoint"

    # lightx2v / CausVid speed packs for Wan or MiniMax H3 stay in even when
    # Hub tags omit the word "lora" (Lightning, StepDistill, Distill-Models).
    # Quantised full checkpoints already returned above.
    if DISTILL_RX.search(hid) or re.search(r"(?i)(lightning|stepdistill|cfgdistill|distill-loras|distill-models)", name):
        if HF_VIDEO_BASE_RX.search(f"{hid} {tag_s} {hf_bases}") and not (
            VAE_RX.search(name) or PROMPT_LORA_RX.search(ident) or re.search(r"(?i)hunyuan|hy1\.5", ident)
        ):
            return True, None

    # Full official base models / distilled full models / Fun Control-InP finetunes
    if not has_lora_token and not is_distill_lora:
        if re.search(r"(?i)(^|/)(LTX-2(?:\.\d)?|LTX-Video|LTX-2\.5-Diffusers|LTX-2\.5-Pre-Trained)($|-(fp8|nvfp4|dev|distilled))", hid):
            return False, "full_base_model"
        if re.search(r"(?i)Fun-(?:\d+(?:\.\d+)?B|A14B|V[\d.]+).*?(Control|InP)|VACE-Fun", hid) and not LORA_TOKEN_RX.search(name):
            return False, "full_finetune"
        if rel in ("finetune", "merge") and not LORA_TOKEN_RX.search(name):
            return False, "full_finetune_or_merge"
        return False, "full_model_or_not_lora"

    # LoRA merges of a *base model* (not a LoRA adapter pack)
    if re.search(r"(?i)lora[_-]?merge", name) and rel == "finetune" and not re.search(r"(?i)adapter", ident):
        return False, "merge"

    # Must target a Wan / LTX / MiniMax H3 video base (name, tags, or card).
    on_video = bool(HF_VIDEO_BASE_RX.search(base_blob) or HF_VIDEO_BASE_RX.search(hid))
    on_wrong = bool(HF_WRONG_BASE_RX.search(hf_bases) or HF_WRONG_BASE_RX.search(tag_s))
    if on_wrong and not on_video:
        return False, "non_target_base"
    if not on_video and not is_lightx2v_lora and not is_distill_lora:
        # still allow if the repo name clearly is Wan/LTX/H3
        if not re.search(r"(?i)(wan|ltx|minimax|h3)", name):
            return False, "non_target_base"

    return True, None


def classify_record(rec: dict, civitai_model: dict | None = None, hf_index_item: dict | None = None, hf_card: dict | None = None) -> tuple[bool, str | None]:
    """Decide whether a compiled catalog row should stay. Installed image LoRAs are dropped with a reason."""
    src = rec.get("source")
    if rec.get("installed"):
        reason = installed_file_is_image_lora(rec.get("file"), rec.get("path"))
        if reason:
            return False, reason

    if src == "huggingface" or rec.get("hf_id"):
        tags = (hf_index_item or {}).get("tags") if hf_index_item else rec.get("hf_tags")
        return hf_is_video_lora(rec.get("hf_id"), tags, hf_card)

    if rec.get("civitai_model_id") and civitai_model:
        if not civitai_is_adapter_type(civitai_model):
            t = civitai_model.get("type") or "unknown"
            return False, f"civitai_type:{t}"
        bases = rec.get("bases") or ([rec.get("base")] if rec.get("base") else [])
        if not civitai_has_video_base(civitai_model, bases):
            return False, "no_video_base"
        return True, None

    # Inventory / local / fuzzpuppy / unverified stubs: keep if they look like
    # video LoRAs (family folder + name), unless already caught as image files.
    if rec.get("installed") or src in ("inventory", "local", "fuzzpuppy"):
        return True, None

    if src == "civitai":
        bases = rec.get("bases") or ([rec.get("base")] if rec.get("base") else [])
        if not any(is_video_base(b) for b in bases):
            return False, "no_video_base"
        return True, None

    return True, None
