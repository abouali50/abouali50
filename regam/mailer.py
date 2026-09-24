"""Envoi de l'e-mail de bienvenue via SMTP.

Fonctionne avec n'importe quel fournisseur SMTP (Brevo, Resend, Mailjet,
Gmail, OVH…). Si SMTP_HOST n'est pas défini, l'envoi est simplement ignoré.

Variables d'environnement :
  SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD,
  SMTP_FROM ("Regam <bonjour@regam.ai>"), SMTP_SSL ("1" pour le port 465),
  REGAM_SITE_URL (lien dans l'e-mail, ex. https://regam.ai)
"""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

log = logging.getLogger("regam.mailer")

PLAN_NAMES = {"decouverte": "Découverte", "createur": "Créateur", "pro": "Pro"}


def is_configured() -> bool:
    return bool(os.environ.get("SMTP_HOST"))


def build_welcome(to: str, plan: str) -> EmailMessage:
    site = os.environ.get("REGAM_SITE_URL", "https://regam.ai").rstrip("/")
    plan_name = PLAN_NAMES.get(plan, "Découverte")

    msg = EmailMessage()
    msg["Subject"] = "Bienvenue sur Regam ✦ tes 50 crédits t'attendent"
    msg["From"] = os.environ.get("SMTP_FROM", "Regam <bonjour@regam.ai>")
    msg["To"] = to
    msg.set_content(
        f"""Bienvenue sur Regam !

Merci pour ton inscription (forfait choisi : {plan_name}).
Tes 50 crédits offerts seront disponibles dès l'ouverture de ton compte :
on t'écrit dès que c'est prêt.

En attendant, teste le studio : {site}/#studio

À très vite,
L'équipe Regam

Tu reçois cet e-mail car tu t'es inscrit·e sur {site}.
Pour supprimer tes données, réponds simplement à ce message.
"""
    )
    msg.add_alternative(
        f"""<!doctype html>
<html lang="fr"><body style="margin:0;background:#0C0C10;font-family:Inter,Arial,sans-serif;color:#F3F1EC">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:40px 16px">
    <table role="presentation" width="100%" style="max-width:520px;background:#131319;border:1px solid #2a2a33;border-radius:20px">
      <tr><td style="padding:36px 32px">
        <div style="font-size:22px;font-weight:800;letter-spacing:-.02em">
          <span style="color:#D4FF3A">R</span> Regam
        </div>
        <h1 style="font-size:26px;line-height:1.2;margin:28px 0 12px">Bienvenue à bord&nbsp;!</h1>
        <p style="color:#C9C7CF;line-height:1.6;margin:0 0 12px">
          Merci pour ton inscription (forfait choisi&nbsp;: <strong style="color:#F3F1EC">{escape(plan_name)}</strong>).
        </p>
        <p style="color:#C9C7CF;line-height:1.6;margin:0 0 28px">
          Tes <strong style="color:#D4FF3A">50 crédits offerts</strong> seront disponibles dès l'ouverture de ton compte.
          On t'écrit dès que c'est prêt.
        </p>
        <a href="{escape(site)}/#studio" style="display:inline-block;background:#D4FF3A;color:#0C0C10;font-weight:700;text-decoration:none;padding:14px 24px;border-radius:999px">Tester le studio →</a>
        <p style="color:#9A98A3;font-size:12px;line-height:1.6;margin:36px 0 0">
          Tu reçois cet e-mail car tu t'es inscrit·e sur {escape(site)}.
          Pour supprimer tes données, réponds simplement à ce message.
        </p>
      </td></tr>
    </table>
  </td></tr></table>
</body></html>""",
        subtype="html",
    )
    return msg


def send_welcome(to: str, plan: str) -> None:
    """Envoie l'e-mail. Ne lève jamais : un échec d'envoi ne doit pas casser l'inscription."""
    if not is_configured():
        log.info("SMTP non configuré : e-mail de bienvenue non envoyé à %s", to)
        return

    host = os.environ["SMTP_HOST"]
    use_ssl = os.environ.get("SMTP_SSL") == "1"
    port = int(os.environ.get("SMTP_PORT", "465" if use_ssl else "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    msg = build_welcome(to, plan)
    ctx = ssl.create_default_context()

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
        with server:
            if not use_ssl:
                server.starttls(context=ctx)
            if user:
                server.login(user, password or "")
            server.send_message(msg)
        log.info("E-mail de bienvenue envoyé à %s", to)
    except Exception:  # noqa: BLE001 — on journalise et on continue
        log.exception("Échec de l'envoi de l'e-mail de bienvenue à %s", to)
