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
  // Trois états :
  //  - démo : pas de serveur ou pas de clé d'API → animation locale ;
  //  - visiteur : quelques essais gratuits (images) par jour ;
  //  - connecté·e : chaque génération consomme des crédits ; vidéo selon le forfait.
  const COST = { avatar: 2, image: 1, video: 8 };
  const LABEL = { avatar: "Avatar", image: "Image", video: "Vidéo" };
  const PALETTES = ["", "portrait--2", "portrait--3", "portrait--4", "portrait--5"];
  const STEPS = ["Analyse du prompt…", "Composition de la scène…", "Rendu des détails…", "Upscale 4K…"];
  const VIDEO_STEPS = ["Mise en file d'attente…", "Animation de la scène…", "Rendu des images…", "Encodage de la vidéo…"];
  const studio = { live: false, remaining: 0, user: null };
  let mode = "avatar";
  let busy = false;
  let hasResult = false;
  let animateSource = null; // { id, url } : image à animer en mode Vidéo
  let lastEntry = null;

  const choice = (group) => $(`.choices[data-group=${group}] .is-on`);
  const costOf = () => (mode === "video" ? (choice("duree").textContent.startsWith("10") ? 16 : 8) : COST[mode]);
  const canVideo = () => !!studio.user && studio.user.plan !== "decouverte";
  // Le mode courant appelle-t-il vraiment le modèle ?
  const isLive = () => studio.live && (mode !== "video" || canVideo());
  const plural = (n, word) => `${n} ${word}${n > 1 ? "s" : ""}`;

  const updateStudioInfo = () => {
    const cost = $("#cost");
    const info = $("#studioAccount");
    if (!studio.live) {
      cost.textContent = `· ${plural(costOf(), "crédit")}`;
      return;
    }
    info.hidden = false;
    if (studio.user) {
      cost.textContent = mode === "video" && !canVideo() ? "· démo" : `· ${plural(costOf(), "crédit")}`;
      info.innerHTML = mode === "video" && !canVideo()
        ? 'La vidéo est incluse dès le forfait Créateur. <a href="/compte.html?plan=createur">Voir les forfaits</a>'
        : `Solde : <b></b> · <a href="/compte.html">Mon compte</a>`;
      const b = $("b", info);
      if (b) b.textContent = plural(studio.user.credits, "crédit");
    } else {
      cost.textContent = mode === "video" ? "· démo"
        : studio.remaining > 0 ? `· ${studio.remaining} essai${studio.remaining > 1 ? "s" : ""} gratuit${studio.remaining > 1 ? "s" : ""}`
        : "· essais du jour épuisés";
      info.innerHTML = '<a href="/compte.html">Crée un compte gratuit</a> pour recevoir 50 crédits et débloquer la vidéo.';
    }
  };

  const setUser = (user) => {
    studio.user = user;
    const nav = $("#navAccount");
    if (user) nav.textContent = `Mon compte · ${user.credits}`;
    updateStudioInfo();
  };

  fetch("/api/studio")
    .then((r) => (r.ok ? r.json() : { enabled: false }))
    .then((data) => {
      if (!data.enabled) {
        // Pas d'IA branchée : on regarde quand même si la personne est connectée.
        fetch("/api/me").then((r) => (r.ok ? r.json() : null)).then((u) => u && setUser(u)).catch(() => {});
        return;
      }
      studio.live = true;
      studio.remaining = data.remaining;
      $("#studioMode").innerHTML = '<span class="live">Studio connecté</span> · générations réelles';
      setUser(data.user);
      const wanted = Number(new URLSearchParams(location.search).get("animer"));
      if (wanted && canVideo()) {
        fetch("/api/me/generations").then((r) => (r.ok ? r.json() : [])).then((items) => {
          const g = items.find((it) => it.id === wanted && it.status === "done" && it.mode !== "video");
          if (g) animate({ id: g.id, url: g.url });
        }).catch(() => {});
      }
    })
    .catch(() => {});

  const tabs = $$(".tabs [role=tab]");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
    mode = tab.dataset.mode;
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    $$("[data-only]").forEach((el) => { el.hidden = el.dataset.only !== mode; });
    renderSource();
    updateStudioInfo();
  }));

  /* Image → vidéo */
  const selectTab = (name) => $(`.tabs [data-mode=${name}]`).click();
  const renderSource = () => {
    const chip = $("#sourceChip");
    const animating = !!animateSource && mode === "video";
    chip.hidden = !animating;
    // L'image de départ fixe déjà le style et le format.
    ["style", "ratio"].forEach((g) => { $(`.choices[data-group=${g}]`).closest(".field").hidden = animating; });
    if (animateSource) $("#sourceImg").src = animateSource.url;
    $("#prompt").placeholder = animateSource && mode === "video"
      ? "Décris le mouvement : elle sourit, la caméra avance lentement…"
      : "";
  };
  const animate = (source) => {
    animateSource = source;
    selectTab("video");
    const prompt = $("#prompt");
    prompt.value = "";
    renderSource();
    prompt.focus({ preventScroll: true });
    $("#studio").scrollIntoView({ behavior: "smooth", block: "start" });
  };
  $("#sourceClear").addEventListener("click", () => {
    animateSource = null;
    renderSource();
  });
  $("#animateBtn").addEventListener("click", () => {
    if (lastEntry?.id) animate({ id: lastEntry.id, url: lastEntry.img });
  });

  $$(".choices").forEach((group) => {
    group.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      $$("button", group).forEach((b) => b.classList.toggle("is-on", b === btn));
      if (btn.dataset.ratio) $("#output").style.setProperty("--ratio", btn.dataset.ratio);
      updateStudioInfo();
    });
  });

  const out = { empty: $("#outEmpty"), loading: $("#outLoading"), result: $("#outResult") };
  const show = (key) => Object.entries(out).forEach(([k, el]) => { el.hidden = k !== key; });
  const errorBox = $("#studioError");
  const showError = (text) => { errorBox.textContent = text; errorBox.hidden = !text; };

  // Barre de progression : jusqu'à `cap` en `duration` ms, puis attente.
  const progress = (duration, cap = 1, steps = STEPS) => {
    const bar = $("#loadingBar");
    const txt = $("#loadingText");
    const start = performance.now();
    let stopped = false;
    const frame = (now) => {
      if (stopped) return;
      const t = Math.min(1, (now - start) / duration);
      bar.style.width = `${Math.round(t * cap * 100)}%`;
      txt.textContent = steps[Math.min(steps.length - 1, Math.floor(t * cap * steps.length))];
      if (t < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
    return () => { stopped = true; bar.style.width = "100%"; };
  };

  const showResult = ({ palette = "", img = null, video = null, badge, id = null }) => {
    const res = out.result;
    res.className = `output__result portrait ${palette}`.trim();
    const image = $("#resultImg");
    const vid = $("#resultVideo");
    image.hidden = !img;
    vid.hidden = !video;
    if (img) {
      image.src = img;
      image.alt = $("#prompt").value.trim();
    } else {
      image.removeAttribute("src");
    }
    if (video) {
      vid.src = video;
      vid.play().catch(() => {});
    } else {
      vid.pause();
      vid.removeAttribute("src");
    }
    $(".dl", res)?.remove();
    const media = img || video;
    if (media) {
      const dl = document.createElement("a");
      dl.className = "dl";
      dl.href = media;
      dl.target = "_blank";
      dl.rel = "noopener";
      dl.textContent = "Ouvrir ↗";
      res.append(dl);
    }
    $("#resultBadge").textContent = badge;
    $("#resultPlay").hidden = mode !== "video" || !!media;
    lastEntry = { img, id };
    $("#animateBtn").hidden = !(img && id && canVideo());
    hasResult = true;
    show("result");
  };

  const addHistory = (entry) => {
    let thumb;
    if (entry.img || entry.video) {
      thumb = document.createElement(entry.video ? "video" : "img");
      thumb.src = entry.img || entry.video;
      if (entry.video) thumb.muted = true;
      else thumb.alt = "";
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

  const postJSON = async (url, body) => {
    const res = await fetch(url, {
      method: body ? "POST" : "GET",
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(typeof data.detail === "string" ? data.detail
        : res.status === 422 ? "Le prompt doit faire entre 3 et 800 caractères." : "La génération a échoué.");
    }
    return data;
  };

  const preload = (src, tag) => new Promise((resolve, reject) => {
    const el = document.createElement(tag);
    const ok = tag === "img" ? "onload" : "onloadeddata";
    el[ok] = () => resolve(src);
    el.onerror = () => reject(new Error("Impossible d'afficher le résultat."));
    if (tag === "video") el.preload = "auto";
    el.src = src;
  });

  const waitForVideo = async (id) => {
    for (;;) {
      await new Promise((r) => setTimeout(r, 4000));
      const job = await postJSON(`/api/jobs/${id}`);
      if (typeof job.credits === "number" && studio.user) setUser({ ...studio.user, credits: job.credits });
      if (job.status === "done") return job.url;
      if (job.status === "failed") throw new Error(job.error || "La vidéo a échoué. Tes crédits ont été remboursés.");
    }
  };

  const runLive = async () => {
    const isVideo = mode === "video";
    const stop = isVideo ? progress(150000, 0.95, VIDEO_STEPS) : progress(9000, 0.92);
    try {
      const data = await postJSON("/api/generate", {
        mode,
        prompt: $("#prompt").value.trim(),
        style: choice("style").dataset.v,
        morpho: choice("morpho").dataset.v,
        ratio: choice("ratio").textContent,
        duration: choice("duree").textContent.startsWith("10") ? "10" : "5",
        source_id: isVideo && animateSource ? animateSource.id : undefined,
      });
      if (typeof data.remaining === "number") studio.remaining = data.remaining;
      if (typeof data.credits === "number" && studio.user) setUser({ ...studio.user, credits: data.credits });
      else updateStudioInfo();

      let entry;
      if (isVideo) {
        const url = await preload(await waitForVideo(data.id), "video");
        entry = { video: url, badge: `Vidéo · ${choice("duree").textContent} · IA${animateSource ? " · animée" : ""}` };
      } else {
        entry = { img: await preload(data.url, "img"), badge: `${LABEL[mode]} · IA`, id: data.id };
      }
      stop();
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

  /* ---------- Inscription (lien magique) ---------- */
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
      const res = await fetch("/api/auth/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: input.value.trim(), website: form.elements.website.value }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.dev_link) {
        msg.innerHTML = 'Mode développement : <a href="">ouvrir le lien de connexion</a>';
        $("a", msg).href = data.dev_link;
      } else if (res.ok) {
        say(`C'est parti ! Clique sur le lien envoyé à ${input.value.trim()} pour activer tes 50 crédits.`);
        input.value = "";
      } else if (res.status === 422) {
        say("Cette adresse e-mail ne semble pas valide.", true);
      } else {
        say(typeof data.detail === "string" ? data.detail
          : "Les inscriptions ouvrent très bientôt. Écris-nous à contact@regam.ai en attendant.", true);
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
