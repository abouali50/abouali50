(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const PLAN_NAMES = { decouverte: "Découverte", createur: "Créateur", pro: "Pro" };
  const PLAN_RANK = { decouverte: 0, createur: 1, pro: 2 };
  const params = new URLSearchParams(location.search);
  const wantedPlan = PLAN_NAMES[params.get("plan")] && params.get("plan") !== "decouverte" ? params.get("plan") : null;
  let yearly = false;
  let user = null;
  let available = [];

  const api = async (path, body) => {
    const res = await fetch(path, body === undefined ? {} : {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(typeof data.detail === "string" ? data.detail : "Une erreur est survenue. Réessaie.");
      err.status = res.status;
      throw err;
    }
    return data;
  };

  const view = (name) => ["Loading", "Login", "Dash"].forEach((v) => { $(`#view${v}`).hidden = v !== name; });
  const toast = (text, isError = false) => {
    const t = $("#toast");
    t.textContent = text;
    t.classList.toggle("is-error", isError);
    t.hidden = !text;
  };
  const say = (el, text, isError = false) => {
    el.textContent = text;
    el.classList.toggle("is-error", isError);
  };

  /* ---------- Connexion ---------- */
  const showLogin = () => {
    if (wantedPlan) {
      const intent = $("#planIntent");
      intent.textContent = `Connecte-toi pour passer au forfait ${PLAN_NAMES[wantedPlan]}.`;
      intent.hidden = false;
    }
    view("Login");
    $("#loginEmail").focus();
  };

  $("#loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("#loginEmail");
    const msg = $("#loginMsg");
    const btn = $("#loginBtn");
    if (!input.value || !input.checkValidity()) {
      say(msg, "Entre une adresse e-mail valide.", true);
      return;
    }
    btn.disabled = true;
    say(msg, "Envoi…");
    try {
      const data = await api("/api/auth/request", {
        email: input.value.trim(),
        plan: wantedPlan || "decouverte",
        next: wantedPlan ? `/compte.html?plan=${wantedPlan}` : null,
        website: e.target.elements.website.value,
      });
      if (data.dev_link) {
        msg.innerHTML = 'Mode développement : <a href="" id="devLink">ouvrir le lien de connexion</a>';
        $("#devLink").href = data.dev_link;
      } else {
        say(msg, `Lien envoyé à ${input.value.trim()} ! Vérifie ta boîte mail (et les spams).`);
      }
    } catch (err) {
      say(msg, err.message, true);
    } finally {
      btn.disabled = false;
    }
  });

  /* ---------- Tableau de bord ---------- */
  const renderUser = () => {
    $("#dashEmail").textContent = user.email;
    $("#dashCredits").textContent = user.credits.toLocaleString("fr-FR");
    $("#dashPlan").textContent = PLAN_NAMES[user.plan];
    $("#dashPlanNote").textContent = user.plan === "decouverte"
      ? "Passe à Créateur pour débloquer la vidéo."
      : "Tes crédits sont rechargés à chaque échéance.";
    $("#portalBtn").hidden = !user.has_billing;

    $$("[data-plan-card]").forEach((card) => {
      const plan = card.dataset.planCard;
      const btn = $("[data-checkout]", card);
      const isCurrent = user.plan === plan;
      const subscribed = user.plan !== "decouverte";
      const buyable = available.some((p) => p.plan === plan && p.yearly === yearly);
      card.classList.toggle("is-wanted", plan === wantedPlan && !isCurrent);
      // Déjà abonné·e : on change de forfait dans l'espace client Stripe (pas de 2e abonnement).
      btn.disabled = isCurrent || (!subscribed && !buyable) || (subscribed && !user.has_billing);
      btn.textContent = isCurrent ? "Forfait actuel"
        : subscribed ? `Passer à ${PLAN_NAMES[plan]}`
        : !buyable ? "Bientôt disponible"
        : `Choisir ${PLAN_NAMES[plan]}`;
    });
  };

  const renderGallery = (items) => {
    const gallery = $("#gallery");
    gallery.textContent = "";
    $("#galleryEmpty").hidden = items.length > 0;
    items.forEach((g) => {
      const fig = document.createElement("figure");
      fig.className = `gallery__item is-${g.status}`;
      if (g.status === "done" && g.url) {
        const link = document.createElement("a");
        link.href = g.url;
        link.target = "_blank";
        link.rel = "noopener";
        let media;
        if (g.mode === "video") {
          media = document.createElement("video");
          media.src = `${g.url}#t=0.1`; // affiche la première image comme aperçu
          media.preload = "metadata";
          media.muted = true;
          media.loop = true;
          media.playsInline = true;
          media.addEventListener("mouseenter", () => media.play().catch(() => {}));
          media.addEventListener("mouseleave", () => media.pause());
        } else {
          media = document.createElement("img");
          media.src = g.url;
          media.loading = "lazy";
          media.alt = g.prompt;
        }
        link.append(media);
        fig.append(link);
        if (g.mode !== "video" && user.plan !== "decouverte") {
          const anim = document.createElement("a");
          anim.className = "gallery__animate";
          anim.href = `/?animer=${g.id}#studio`;
          anim.textContent = "Animer →";
          fig.append(anim);
        }
      } else {
        const ph = document.createElement("div");
        ph.className = "gallery__ph";
        ph.textContent = g.status === "pending" ? "En cours…" : "Échec · remboursé";
        fig.append(ph);
      }
      const cap = document.createElement("figcaption");
      const label = { image: "Image", avatar: "Avatar", video: "Vidéo" }[g.mode] || g.mode;
      cap.textContent = `${label} · ${new Date(g.created_at).toLocaleDateString("fr-FR")}`;
      cap.title = g.prompt;
      fig.append(cap);
      gallery.append(fig);
    });
  };

  const loadDash = async () => {
    const [billing, gens] = await Promise.all([
      api("/api/billing").catch(() => ({ plans: [] })),
      api("/api/me/generations").catch(() => []),
    ]);
    available = billing.plans || [];
    renderUser();
    renderGallery(gens);
    view("Dash");
    if (wantedPlan) $("#upgrade").scrollIntoView({ behavior: "smooth", block: "start" });
  };

  $$(".billing button").forEach((btn) => btn.addEventListener("click", () => {
    yearly = btn.dataset.billing === "year";
    $$(".billing button").forEach((b) => b.classList.toggle("is-on", b === btn));
    $$(".plan__price span").forEach((s) => { s.textContent = s.dataset[yearly ? "y" : "m"]; });
    renderUser();
  }));

  const openPortal = async () => {
    try {
      location.href = (await api("/api/billing/portal", {})).url;
    } catch (err) {
      toast(err.message, true);
    }
  };

  $$("[data-checkout]").forEach((btn) => btn.addEventListener("click", async () => {
    if (user.plan !== "decouverte") {
      openPortal();
      return;
    }
    const msg = $("#billingMsg");
    btn.disabled = true;
    say(msg, "Redirection vers le paiement sécurisé…");
    try {
      const { url } = await api("/api/billing/checkout", { plan: btn.dataset.checkout, yearly });
      location.href = url;
    } catch (err) {
      say(msg, err.message, true);
      btn.disabled = false;
    }
  }));

  $("#portalBtn").addEventListener("click", openPortal);

  $("#logoutBtn").addEventListener("click", async () => {
    await api("/api/auth/logout", {}).catch(() => {});
    user = null;
    showLogin();
  });

  /* ---------- Démarrage ---------- */
  const start = async () => {
    // 1. Retour depuis le lien magique : /compte.html#token=…
    const token = new URLSearchParams(location.hash.slice(1)).get("token");
    if (token) {
      history.replaceState(null, "", location.pathname + location.search);
      try {
        const data = await api("/api/auth/verify", { token });
        if (data.next && data.next !== location.pathname + location.search) {
          location.replace(data.next);
          return;
        }
      } catch (err) {
        toast(err.message, true);
      }
    }

    // 2. Retour depuis Stripe
    const payment = params.get("paiement");
    if (payment === "ok") toast("Paiement reçu, merci ! Tes crédits arrivent dans quelques secondes.");
    if (payment === "annule") toast("Paiement annulé. Tu n'as pas été débité·e.");

    try {
      user = await api("/api/me");
    } catch {
      showLogin();
      return;
    }
    await loadDash();

    // Stripe confirme le paiement par webhook : on rafraîchit le solde.
    if (payment === "ok") {
      const before = user.credits;
      for (let i = 0; i < 5 && user.credits === before; i += 1) {
        await new Promise((r) => setTimeout(r, 2000));
        user = await api("/api/me").catch(() => user);
      }
      renderUser();
    }
  };

  // Lien magique ouvert alors que la page compte est déjà affichée (même onglet) :
  // seul le fragment #token=… change, la page n'est pas rechargée.
  window.addEventListener("hashchange", () => {
    if (location.hash.includes("token=")) {
      view("Loading");
      start();
    }
  });

  start();
})();
