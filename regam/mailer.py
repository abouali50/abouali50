"""E-mails transactionnels (SMTP) : lien de connexion + bienvenue.

Fonctionne avec n'importe quel fournisseur SMTP (Brevo, Resend, Mailjet,
Gmail, OVH…).

Variables d'environnement :
  SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD,
  SMTP_FROM ("Regam <bonjour@regam.ai>"), SMTP_SSL ("1" pour le port 465)
"""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from html import escape

log = logging.getLogger("regam.mailer")


def is_configured() -> bool:
    return bool(os.environ.get("SMTP_HOST"))


def build_login(to: str, link: str, is_new: bool) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Bienvenue sur Regam ✦ ton lien de connexion" if is_new else "Ton lien de connexion Regam"
    msg["From"] = os.environ.get("SMTP_FROM", "Regam <bonjour@regam.ai>")
    msg["To"] = to

    intro = (
        "Bienvenue sur Regam ! Ton compte est prêt et tes 50 crédits offerts t'attendent."
        if is_new
        else "Voici ton lien pour te connecter à Regam."
    )
    msg.set_content(
        f"""{intro}

Clique sur ce lien pour te connecter (valable 30 minutes, une seule fois) :
{link}

Si tu n'es pas à l'origine de cette demande, ignore simplement cet e-mail.

L'équipe Regam
"""
    )
    msg.add_alternative(
        f"""<!doctype html>
<html lang="fr"><body style="margin:0;background:#0C0C10;font-family:Inter,Arial,sans-serif;color:#F3F1EC">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:40px 16px">
    <table role="presentation" width="100%" style="max-width:520px;background:#131319;border:1px solid #2a2a33;border-radius:20px">
      <tr><td style="padding:36px 32px">
        <div style="font-size:22px;font-weight:800;letter-spacing:-.02em"><span style="color:#D4FF3A">R</span> Regam</div>
        <h1 style="font-size:26px;line-height:1.2;margin:28px 0 12px">{"Bienvenue à bord&nbsp;!" if is_new else "Connexion"}</h1>
        <p style="color:#C9C7CF;line-height:1.6;margin:0 0 28px">{escape(intro)}</p>
        <a href="{escape(link)}" style="display:inline-block;background:#D4FF3A;color:#0C0C10;font-weight:700;text-decoration:none;padding:14px 24px;border-radius:999px">Me connecter →</a>
        <p style="color:#9A98A3;font-size:12px;line-height:1.6;margin:36px 0 0">
          Lien valable 30 minutes, utilisable une seule fois.<br/>
          Si tu n'es pas à l'origine de cette demande, ignore simplement cet e-mail.
        </p>
      </td></tr>
    </table>
  </td></tr></table>
</body></html>""",
        subtype="html",
    )
    return msg


def send(msg: EmailMessage) -> bool:
    """Envoie l'e-mail. Ne lève jamais ; renvoie False en cas d'échec."""
    if not is_configured():
        log.warning("SMTP non configuré : e-mail non envoyé à %s", msg["To"])
        return False

    host = os.environ["SMTP_HOST"]
    use_ssl = os.environ.get("SMTP_SSL") == "1"
    port = int(os.environ.get("SMTP_PORT", "465" if use_ssl else "587"))
    user = os.environ.get("SMTP_USER")
    ctx = ssl.create_default_context()
    try:
        server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=15) if use_ssl else smtplib.SMTP(host, port, timeout=15)
        with server:
            if not use_ssl:
                server.starttls(context=ctx)
            if user:
                server.login(user, os.environ.get("SMTP_PASSWORD", ""))
            server.send_message(msg)
        return True
    except Exception:  # noqa: BLE001 — on journalise et on continue
        log.exception("Échec de l'envoi de l'e-mail à %s", msg["To"])
        return False
