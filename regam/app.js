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

  /* ---------- Studio demo ---------- */
  const COST = { avatar: 2, image: 1, video: 8 };
  const LABEL = { avatar: "Avatar", image: "Image", video: "Vidéo" };
  const PALETTES = ["", "portrait--2", "portrait--3", "portrait--4", "portrait--5"];
  const STEPS = ["Analyse du prompt…", "Composition de la scène…", "Rendu des détails…", "Upscale 4K…"];
  let mode = "avatar";
  let busy = false;

  const tabs = $$(".tabs [role=tab]");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
    mode = tab.dataset.mode;
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    $$("[data-only]").forEach((el) => { el.hidden = el.dataset.only !== mode; });
    $("#cost").textContent = `· ${COST[mode]} crédit${COST[mode] > 1 ? "s" : ""}`;
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

  $("#generate").addEventListener("click", () => {
    if (busy) return;
    busy = true;
    show("loading");
    const bar = $("#loadingBar");
    const txt = $("#loadingText");
    const total = mode === "video" ? 3200 : 2200;
    const start = performance.now();

    const frame = (now) => {
      const t = Math.min(1, (now - start) / total);
      bar.style.width = `${Math.round(t * 100)}%`;
      txt.textContent = STEPS[Math.min(STEPS.length - 1, Math.floor(t * STEPS.length))];
      if (t < 1) return requestAnimationFrame(frame);

      const palette = PALETTES[Math.floor(Math.random() * PALETTES.length)];
      const res = out.result;
      res.className = `output__result portrait ${palette}`.trim();
      $("#resultBadge").textContent = `${LABEL[mode]} · ${mode === "video" ? $(".choices[data-group=duree] .is-on").textContent : "4K"}`;
      $("#resultPlay").hidden = mode !== "video";
      show("result");

      const thumb = document.createElement("div");
      thumb.className = `portrait ${palette}`.trim();
      thumb.innerHTML = '<svg viewBox="0 0 200 240" preserveAspectRatio="xMidYMax meet"><use href="#silhouette"/></svg>';
      $("#history").prepend(thumb);
      busy = false;
    };
    requestAnimationFrame(frame);
  });

  /* ---------- Pricing toggle ---------- */
  const billingBtns = $$(".billing button");
  billingBtns.forEach((btn) => btn.addEventListener("click", () => {
    billingBtns.forEach((b) => b.classList.toggle("is-on", b === btn));
    const key = btn.dataset.billing === "year" ? "y" : "m";
    $$(".plan__price span").forEach((s) => { s.textContent = s.dataset[key]; });
  }));

  /* ---------- Signup form ---------- */
  $("#signup").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = $("#email");
    const msg = $("#signupMsg");
    if (!input.checkValidity() || !input.value) {
      msg.textContent = "Entre une adresse e-mail valide.";
      input.focus();
      return;
    }
    msg.textContent = "C'est noté ! Tes 50 crédits t'attendent dans ta boîte mail.";
    input.value = "";
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
