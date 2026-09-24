"""Génération d'images IA via fal.ai (modèle FLUX).

Activée uniquement si FAL_KEY est défini. Sans clé, le studio du site reste
en mode démo.

Variables d'environnement :
  FAL_KEY                  clé API fal.ai (https://fal.ai/dashboard/keys)
  REGAM_FAL_MODEL          modèle (défaut : fal-ai/flux/schnell)
  REGAM_GEN_PER_IP_DAY     générations max par IP et par jour (défaut : 5)
  REGAM_GEN_DAILY_CAP      générations max par jour, tous visiteurs (défaut : 200)
"""

import os
from typing import Literal

import httpx
from pydantic import BaseModel, Field

Mode = Literal["avatar", "image"]
Style = Literal["photo", "editorial", "cinema", "studio"]
Morpho = Literal["fine", "moyenne", "athletique", "ronde"]
Ratio = Literal["9:16", "1:1", "16:9"]

STYLE_PROMPTS = {
    "photo": "photorealistic, natural skin texture, 85mm lens, shallow depth of field, sharp focus",
    "editorial": "editorial fashion photography, magazine cover look, refined color grading",
    "cinema": "cinematic film still, anamorphic lens, dramatic lighting, subtle film grain",
    "studio": "professional studio photography, seamless backdrop, softbox lighting",
}
MORPHO_PROMPTS = {
    "fine": "slim build",
    "moyenne": "average build",
    "athletique": "athletic build",
    "ronde": "curvy build",
}
RATIO_SIZES = {"9:16": "portrait_16_9", "1:1": "square_hd", "16:9": "landscape_16_9"}


class GenerateIn(BaseModel):
    mode: Mode = "image"
    prompt: str = Field(min_length=3, max_length=800)
    style: Style = "photo"
    morpho: Morpho = "moyenne"
    ratio: Ratio = "9:16"


class GenerationError(Exception):
    """Erreur à afficher telle quelle à l'utilisateur."""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def is_enabled() -> bool:
    return bool(os.environ.get("FAL_KEY"))


def per_ip_limit() -> int:
    return int(os.environ.get("REGAM_GEN_PER_IP_DAY", "5"))


def daily_cap() -> int:
    return int(os.environ.get("REGAM_GEN_DAILY_CAP", "200"))


def build_prompt(req: GenerateIn) -> str:
    parts = []
    if req.mode == "avatar":
        # Toujours une personne fictive : pas de ressemblance avec des personnes réelles.
        parts.append(f"Portrait of a fictional person, {MORPHO_PROMPTS[req.morpho]}")
    parts.append(req.prompt.strip())
    parts.append(STYLE_PROMPTS[req.style])
    parts.append("high detail, 4k")
    return ", ".join(parts)


def generate_image(req: GenerateIn, client: httpx.Client | None = None) -> dict:
    """Appelle fal.ai et renvoie {"url", "width", "height"}."""
    model = os.environ.get("REGAM_FAL_MODEL", "fal-ai/flux/schnell")
    body = {
        "prompt": build_prompt(req),
        "image_size": RATIO_SIZES[req.ratio],
        "num_images": 1,
        "enable_safety_checker": True,
    }
    headers = {"Authorization": f"Key {os.environ['FAL_KEY']}"}

    own_client = client is None
    client = client or httpx.Client(timeout=90)
    try:
        res = client.post(f"https://fal.run/{model}", json=body, headers=headers)
    except httpx.HTTPError as exc:
        raise GenerationError("Le service de génération ne répond pas. Réessaie dans un instant.") from exc
    finally:
        if own_client:
            client.close()

    if res.status_code == 422:
        raise GenerationError("Ce prompt a été refusé par le modèle. Reformule-le.", 422)
    if res.status_code >= 400:
        raise GenerationError("La génération a échoué. Réessaie dans un instant.")

    data = res.json()
    if any(data.get("has_nsfw_concepts") or []):
        raise GenerationError("Contenu refusé par le filtre de sécurité.", 422)
    images = data.get("images") or []
    if not images or not images[0].get("url"):
        raise GenerationError("Aucune image n'a été renvoyée. Réessaie.")
    img = images[0]
    return {"url": img["url"], "width": img.get("width"), "height": img.get("height")}
