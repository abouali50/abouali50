(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  $("#year").textContent = new Date().getFullYear();

  /* ---------- Mobile menu ---------- */
  const burger = $("#burger");
  const links = $("#navLinks");
  const setMenu = (open) => {
    links.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", String(open));
  };
  burger.addEventListener("click", () => setMenu(!links.classList.contains("is-open")));
  $$("a", links).forEach((a) => a.addEventListener("click", () => setMenu(false)));

  /* ---------- Hero typing prompt ---------- */
  const prompts = [
    "Avatar femme 30 ans, lumière dorée, rue de Paris",
    "Vidéo UGC : il présente une crème hydratante",
    "Produit sur marbre blanc, éclairage studio, 4K",
    "Motion control : danse à partir de ma vidéo",
  ];
  const typing = $("#heroTyping");
  if (reducedMotion) {
    typing.textContent = prompts[0];
  } else {
    let p = 0, i = 0, deleting = false;
    const tick = () => {
      const text = prompts[p];
      i += deleting ? -1 : 1;
      typing.textContent = text.slice(0, i);
      let delay = deleting ? 22 : 48;
      if (!deleting && i === text.length) { deleting = true; delay = 1800; }
      else if (deleting && i === 0) { deleting = false; p = (p + 1) % prompts.length; delay = 400; }
      setTimeout(tick, delay);
    };
    tick();
  }

  /* ---------- Studio ---------- */
  // Si le serveur a une clé d'API, Avatar et Image appellent un vrai modèle ;
  // sinon (ou en mode Vidéo) le studio reste une démo visuelle.
  const COST = { avatar: 2, image: 1, video: 8 };
  const LABEL = { avatar: "Avatar", image: "Image", video: "Vidéo" };
  const PALETTES = ["", "portrait--2", "portrait--3", "portrait--4", "portrait--5"];
  const STEPS = ["Analyse du prompt…", "Composition de la scène…", "Rendu des détails…", "Upscale 4K…"];
  const studio = { live: false, remaining: 0 };
  let mode = "avatar";
  let busy = false;
  let hasResult = false;

  const isLive = () => studio.live && mode !== "video";
  const choice = (group) => $(`.choices[data-group=${group}] .is-on`);

  const updateCost = () => {
    const cost = $("#cost");
    if (isLive()) cost.textContent = studio.remaining > 0
      ? `· ${studio.remaining} gratuite${studio.remaining > 1 ? "s" : ""} aujourd'hui`
      : "· quota du jour atteint";
    else if (studio.live) cost.textContent = "· démo (bientôt)";
    else cost.textContent = `· ${COST[mode]} crédit${COST[mode] > 1 ? "s" : ""}`;
  };

  fetch("/api/studio")
    .then((r) => (r.ok ? r.json() : { enabled: false }))
    .then((data) => {
      if (!data.enabled) return;
      studio.live = true;
      studio.remaining = data.remaining;
      $("#studioMode").innerHTML = '<span class="live">Studio connecté</span> · Avatar et Image génèrent de vraies images';
      updateCost();
    })
    .catch(() => {});

  const tabs = $$(".tabs [role=tab]");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
    mode = tab.dataset.mode;
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    $$("[data-only]").forEach((el) => { el.hidden = el.dataset.only !== mode; });
    updateCost();
  }));

  $$(".choices").forEach((group) => {
    group.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      $$("button", group).forEach((b) => b.classList.toggle("is-on", b === btn));
      if (btn.dataset.ratio) $("#output").style.setProperty("--ratio", btn.dataset.ratio);
    });
  });

  const out = { empty: $("#outEmpty"), loading: $("#outLoading"), result: $("#outResult") };
  const show = (key) => Object.entries(out).forEach(([k, el]) => { el.hidden = k !== key; });
  const errorBox = $("#studioError");
  const showError = (text) => { errorBox.textContent = text; errorBox.hidden = !text; };

  // Barre de progression : jusqu'à `cap` en `duration` ms, puis attente.
  const progress = (duration, cap = 1) => {
    const bar = $("#loadingBar");
    const txt = $("#loadingText");
    const start = performance.now();
    let stopped = false;
    const frame = (now) => {
      if (stopped) return;
      const t = Math.min(1, (now - start) / duration);
      bar.style.width = `${Math.round(t * cap * 100)}%`;
      txt.textContent = STEPS[Math.min(STEPS.length - 1, Math.floor(t * cap * STEPS.length))];
      if (t < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
    return () => { stopped = true; bar.style.width = "100%"; };
  };

  const showResult = ({ palette = "", img = null, badge }) => {
    const res = out.result;
    res.className = `output__result portrait ${palette}`.trim();
    const image = $("#resultImg");
    image.hidden = !img;
    if (img) {
      image.src = img;
      image.alt = $("#prompt").value.trim();
    } else {
      image.removeAttribute("src");
    }
    $(".dl", res)?.remove();
    if (img) {
      const dl = document.createElement("a");
      dl.className = "dl";
      dl.href = img;
      dl.target = "_blank";
      dl.rel = "noopener";
      dl.textContent = "Ouvrir ↗";
      res.append(dl);
    }
    $("#resultBadge").textContent = badge;
    $("#resultPlay").hidden = mode !== "video" || !!img;
    hasResult = true;
    show("result");
  };

  const addHistory = (entry) => {
    let thumb;
    if (entry.img) {
      thumb = document.createElement("img");
      thumb.src = entry.img;
      thumb.alt = "";
      thumb.addEventListener("click", () => showResult(entry));
    } else {
      thumb = document.createElement("div");
      thumb.className = `portrait ${entry.palette}`.trim();
      thumb.innerHTML = '<svg viewBox="0 0 200 240" preserveAspectRatio="xMidYMax meet"><use href="#silhouette"/></svg>';
    }
    $("#history").prepend(thumb);
  };

  const runDemo = () => new Promise((resolve) => {
    const total = mode === "video" ? 3200 : 2200;
    progress(total);
    setTimeout(() => {
      const palette = PALETTES[Math.floor(Math.random() * PALETTES.length)];
      const entry = { palette, badge: `${LABEL[mode]} · ${mode === "video" ? choice("duree").textContent : "4K"} · démo` };
      showResult(entry);
      addHistory(entry);
      resolve();
    }, total);
  });

  const runLive = async () => {
    const stop = progress(9000, 0.92);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          prompt: $("#prompt").value.trim(),
          style: choice("style").dataset.v,
          morpho: choice("morpho").dataset.v,
          ratio: choice("ratio").textContent,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = typeof data.detail === "string" ? data.detail
          : res.status === 422 ? "Le prompt doit faire entre 3 et 800 caractères." : "La génération a échoué.";
        throw new Error(detail);
      }
      studio.remaining = data.remaining;
      updateCost();
      const img = await new Promise((resolve, reject) => {
        const pre = new Image();
        pre.onload = () => resolve(data.url);
        pre.onerror = () => reject(new Error("Impossible d'afficher l'image générée."));
        pre.src = data.url;
      });
      stop();
      const entry = { img, badge: `${LABEL[mode]} · IA` };
      showResult(entry);
      addHistory(entry);
    } catch (err) {
      stop();
      show(hasResult ? "result" : "empty");
      showError(err.message || "Connexion impossible. Réessaie.");
    }
  };

  $("#generate").addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    showError("");
    show("loading");
    const btn = $("#generate");
    btn.disabled = true;
    try {
      await (isLive() ? runLive() : runDemo());
    } finally {
      busy = false;
      btn.disabled = false;
    }
  });

  /* ---------- Pricing toggle ---------- */
  const billingBtns = $$(".billing button");
  billingBtns.forEach((btn) => btn.addEventListener("click", () => {
    billingBtns.forEach((b) => b.classList.toggle("is-on", b === btn));
    const key = btn.dataset.billing === "year" ? "y" : "m";
    $$(".plan__price span").forEach((s) => { s.textContent = s.dataset[key]; });
  }));

  /* ---------- Plan selection → signup form ---------- */
  const PLAN_NAMES = { decouverte: "Découverte", createur: "Créateur", pro: "Pro" };
  $$("[data-plan]").forEach((a) => a.addEventListener("click", () => {
    const plan = a.dataset.plan;
    $("#plan").value = plan;
    const label = $("#planLabel");
    label.textContent = `Forfait choisi : ${PLAN_NAMES[plan]}`;
    label.hidden = false;
    setTimeout(() => $("#email").focus({ preventScroll: true }), 600);
  }));

  /* ---------- Signup form ---------- */
  const form = $("#signup");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("#email");
    const msg = $("#signupMsg");
    const btn = $("#signupBtn");
    const say = (text, isError = false) => {
      msg.textContent = text;
      msg.classList.toggle("is-error", isError);
    };

    if (!input.value || !input.checkValidity()) {
      say("Entre une adresse e-mail valide.", true);
      input.focus();
      return;
    }

    btn.disabled = true;
    say("Envoi…");
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: input.value.trim(),
          plan: $("#plan").value,
          website: form.elements.website.value,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        say(data.already
          ? "Tu es déjà inscrit·e avec cette adresse : on te recontacte très vite."
          : "C'est noté ! On t'envoie tes 50 crédits dès l'ouverture de ton compte.");
        input.value = "";
      } else if (res.status === 429) {
        say("Trop de tentatives. Réessaie dans une minute.", true);
      } else if (res.status === 422) {
        say("Cette adresse e-mail ne semble pas valide.", true);
      } else {
        say("Les inscriptions ouvrent très bientôt. Écris-nous à contact@regam.ai en attendant.", true);
      }
    } catch {
      say("Connexion impossible. Vérifie ton réseau et réessaie.", true);
    } finally {
      btn.disabled = false;
    }
  });

  /* ---------- Reveal on scroll + counters ---------- */
  const revealTargets = $$(".section__head, .tile, .steps li, .case, .plan, .faq details, .studio, .cta__inner");
  const counters = $$("[data-count]");
  const animateCount = (el) => {
    const target = Number(el.dataset.count);
    if (reducedMotion) { el.textContent = target; return; }
    const start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / 1200);
      el.textContent = Math.round(target * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  if (!("IntersectionObserver" in window)) return;
  revealTargets.forEach((el) => el.classList.add("reveal"));
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      if (el.dataset.count) animateCount(el);
      else el.classList.add("is-in");
      io.unobserve(el);
    });
  }, { threshold: 0.15 });
  [...revealTargets, ...counters].forEach((el) => io.observe(el));
})();
