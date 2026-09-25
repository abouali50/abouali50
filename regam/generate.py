"""Génération IA via fal.ai : images (FLUX) et vidéos (Kling).

Activée uniquement si FAL_KEY est défini. Sans clé, le studio du site reste
en mode démo.

Variables d'environnement :
  FAL_KEY                  clé API fal.ai (https://fal.ai/dashboard/keys)
  REGAM_FAL_MODEL          modèle image (défaut : fal-ai/flux/schnell)
  REGAM_FAL_VIDEO_MODEL    modèle vidéo texte→vidéo (défaut : fal-ai/kling-video/v1.6/standard/text-to-video)
  REGAM_FAL_I2V_MODEL      modèle vidéo image→vidéo (défaut : fal-ai/kling-video/v1.6/standard/image-to-video)
  REGAM_GEN_PER_IP_DAY     générations max par IP et par jour (défaut : 5)
  REGAM_GEN_DAILY_CAP      générations max par jour, tous visiteurs (défaut : 200)
"""

import os
from typing import Literal

import httpx
from pydantic import BaseModel, Field

Mode = Literal["avatar", "image", "video"]
Style = Literal["photo", "editorial", "cinema", "studio"]
Morpho = Literal["fine", "moyenne", "athletique", "ronde"]
Ratio = Literal["9:16", "1:1", "16:9"]
Duration = Literal["5", "10"]

# Coût en crédits de chaque génération.
COSTS = {"avatar": 2, "image": 1, "video:5": 8, "video:10": 16}

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
    duration: Duration = "5"
    # Vidéo à partir d'une image : id d'une génération (image ou avatar) de
    # l'utilisateur. Jamais une URL libre : on n'anime que ses propres créations.
    source_id: int | None = Field(default=None, ge=1)

    @property
    def cost(self) -> int:
        return COSTS[f"video:{self.duration}"] if self.mode == "video" else COSTS[self.mode]


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
    if req.mode == "video" and req.source_id:
        # Image → vidéo : l'image fixe déjà le sujet et le style, le prompt décrit le mouvement.
        return f"{req.prompt.strip()}, natural fluid motion, cinematic camera movement"
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


# ---------------------------------------------------------------- vidéo (file d'attente fal)

def _fal(method: str, url: str, client: httpx.Client | None, **kwargs) -> httpx.Response:
    headers = {"Authorization": f"Key {os.environ['FAL_KEY']}"}
    own = client is None
    client = client or httpx.Client(timeout=30)
    try:
        return client.request(method, url, headers=headers, **kwargs)
    except httpx.HTTPError as exc:
        raise GenerationError("Le service vidéo ne répond pas. Réessaie dans un instant.") from exc
    finally:
        if own:
            client.close()


def submit_video(req: GenerateIn, client: httpx.Client | None = None, image_url: str | None = None) -> dict:
    """Met la vidéo en file d'attente. Renvoie {"status_url", "response_url"}.

    Avec `image_url`, anime cette image (le format suit celui de l'image).
    """
    body = {"prompt": build_prompt(req), "duration": req.duration}
    if image_url:
        model = os.environ.get("REGAM_FAL_I2V_MODEL", "fal-ai/kling-video/v1.6/standard/image-to-video")
        body["image_url"] = image_url
    else:
        model = os.environ.get("REGAM_FAL_VIDEO_MODEL", "fal-ai/kling-video/v1.6/standard/text-to-video")
        body["aspect_ratio"] = req.ratio
    res = _fal("POST", f"https://queue.fal.run/{model}", client, json=body)
    if res.status_code == 422:
        raise GenerationError("Ce prompt a été refusé par le modèle. Reformule-le.", 422)
    if res.status_code >= 400:
        raise GenerationError("La vidéo n'a pas pu être lancée. Réessaie dans un instant.")
    data = res.json()
    if not data.get("status_url") or not data.get("response_url"):
        raise GenerationError("Réponse inattendue du service vidéo.")
    return {"status_url": data["status_url"], "response_url": data["response_url"]}


def poll_video(status_url: str, response_url: str, client: httpx.Client | None = None) -> str | None:
    """Renvoie l'URL de la vidéo quand elle est prête, None si encore en cours.

    Lève GenerationError si la génération a échoué.
    """
    try:
        res = _fal("GET", status_url, client)
    except GenerationError:
        return None  # réseau indisponible : on réessaiera au prochain passage
    if res.status_code >= 500:
        return None  # incident passager : on réessaiera au prochain passage
    if res.status_code >= 400:
        raise GenerationError("La vidéo a échoué.")
    if res.json().get("status") != "COMPLETED":
        return None

    res = _fal("GET", response_url, client)
    if res.status_code >= 400:
        raise GenerationError("La vidéo a échoué ou a été refusée par le filtre de sécurité.", 422)
    url = ((res.json() or {}).get("video") or {}).get("url")
    if not url:
        raise GenerationError("Aucune vidéo n'a été renvoyée.")
    return url
