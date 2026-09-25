(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const PLAN_NAMES = { decouverte: "Découverte", createur: "Créateur", pro: "Pro" };
  const nf = new Intl.NumberFormat("fr-FR");
  const eur = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
  const usd = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
  const dayLabel = (iso, opts = { day: "numeric", month: "short" }) =>
    new Date(`${iso}T12:00:00Z`).toLocaleDateString("fr-FR", opts);

  const view = (name) => ["Loading", "Denied", "Admin"].forEach((v) => { $(`#view${v}`).hidden = v !== name; });
  const text = (sel, value) => { $(sel).textContent = value; };

  const api = async (path, body) => {
    const res = await fetch(path, body === undefined ? {} : {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(typeof data.detail === "string" ? data.detail : "Une erreur est survenue.");
      err.status = res.status;
      throw err;
    }
    return data;
  };

  /* ---------- Graphique : barres verticales, une seule série ---------- */
  // Couleur des barres : teinte du vert Regam validée pour un graphique sur fond sombre
  // (luminosité et contraste contrôlés) ; le vert vif de la marque sert au survol.
  const BAR = "#7E9E16";
  const BAR_HOVER = "#D4FF3A";

  const niceMax = (v) => {
    if (v <= 4) return 4;
    const pow = 10 ** Math.floor(Math.log10(v));
    const step = [1, 2, 2.5, 5, 10].find((m) => m * pow * 4 >= v) * pow;
    return step * 4;
  };

  const renderChart = (daily) => {
    const el = $("#chart");
    const tip = $("#chartTip");
    const W = el.clientWidth || 800;
    const H = 240;
    const pad = { top: 12, right: 8, bottom: 28, left: 40 };
    const innerW = W - pad.left - pad.right;
    const innerH = H - pad.top - pad.bottom;
    const max = niceMax(Math.max(...daily.map((d) => d.generations), 0));
    const band = innerW / daily.length;
    const barW = Math.max(2, Math.min(24, band - 2)); // ≤ 24 px, 2 px d'air minimum entre barres
    const y = (v) => pad.top + innerH - (v / max) * innerH;
    const labelStep = Math.max(1, Math.ceil(daily.length / Math.max(2, Math.floor(innerW / 70))));
    const last = daily.length - 1;
    const lastTooClose = last % labelStep !== 0 && last % labelStep < labelStep / 2;
    const showLabel = (i) => i === last || (i % labelStep === 0 && !(lastTooClose && i === last - (last % labelStep)));

    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("width", W);
    svg.setAttribute("height", H);
    const add = (tag, attrs, parent = svg) => {
      const n = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
      parent.append(n);
      return n;
    };

    // Grille horizontale (hairline) + graduations rondes.
    for (let i = 0; i <= 4; i += 1) {
      const v = (max / 4) * i;
      add("line", { x1: pad.left, x2: W - pad.right, y1: y(v), y2: y(v), class: "chart__grid" });
      add("text", { x: pad.left - 8, y: y(v) + 4, "text-anchor": "end", class: "chart__tick" }).textContent = nf.format(v);
    }

    daily.forEach((d, i) => {
      const cx = pad.left + band * i + band / 2;
      const x = cx - barW / 2;
      const top = y(d.generations);
      const h = pad.top + innerH - top;
      // Barre : extrémité arrondie (4 px), base carrée.
      if (d.generations > 0) {
        const r = Math.min(4, barW / 2, h);
        const base = pad.top + innerH;
        add("path", {
          d: `M${x},${base} V${top + r} Q${x},${top} ${x + r},${top} H${x + barW - r} Q${x + barW},${top} ${x + barW},${top + r} V${base} Z`,
          fill: BAR,
          class: "chart__bar",
          "data-i": i,
        });
      }
      // Libellés de dates : autant que la largeur le permet (~70 px chacun) ; le dernier
      // jour remplace le libellé précédent s'il en est trop proche.
      if (showLabel(i)) {
        add("text", { x: i === 0 ? pad.left + band * i : i === last ? pad.left + band * (i + 1) : cx, y: H - 8, "text-anchor": i === 0 ? "start" : i === last ? "end" : "middle", class: "chart__tick" }).textContent = dayLabel(d.date);
      }
      // Zone de survol : toute la colonne, plus large que la barre.
      add("rect", { x: pad.left + band * i, y: pad.top, width: band, height: innerH, fill: "transparent", "data-i": i, class: "chart__hit" });
    });

    el.textContent = "";
    el.append(svg);
    el.setAttribute("aria-label", `Générations par jour sur 30 jours, total ${nf.format(daily.reduce((s, d) => s + d.generations, 0))}`);

    const bars = [...svg.querySelectorAll(".chart__bar")];
    const highlight = (i) => bars.forEach((b) => b.setAttribute("fill", Number(b.dataset.i) === i ? BAR_HOVER : BAR));
    svg.addEventListener("pointermove", (e) => {
      const hit = e.target.closest(".chart__hit");
      if (!hit) return;
      const i = Number(hit.dataset.i);
      const d = daily[i];
      highlight(i);
      tip.innerHTML = `<b></b><span></span><span></span>`;
      tip.children[0].textContent = dayLabel(d.date, { weekday: "short", day: "numeric", month: "long" });
      tip.children[1].textContent = `${nf.format(d.generations)} génération${d.generations > 1 ? "s" : ""}`;
      tip.children[2].textContent = `${nf.format(d.new_users)} nouveau${d.new_users > 1 ? "x" : ""} compte${d.new_users > 1 ? "s" : ""}`;
      tip.hidden = false;
      const box = el.getBoundingClientRect();
      const cx = (pad.left + band * i + band / 2) * (box.width / W);
      const left = Math.min(Math.max(cx, tip.offsetWidth / 2), box.width - tip.offsetWidth / 2);
      tip.style.left = `${left}px`;
      tip.style.top = `${el.offsetTop + y(d.generations) * (box.height / H) - 12}px`;
    });
    svg.addEventListener("pointerleave", () => { tip.hidden = true; highlight(-1); });
  };

  /* ---------- Rendu ---------- */
  let lastStats = null;

  const render = (s) => {
    lastStats = s;
    const paying = s.users.by_plan.createur + s.users.by_plan.pro;
    text("#kMrr", eur.format(s.mrr_eur));
    text("#kMrrNote", "au prix mensuel affiché");
    text("#kUsers", nf.format(s.users.total));
    text("#kUsersNote", `+${nf.format(s.users.new_7d)} cette semaine · ${nf.format(s.users.waitlist)} non activés`);
    text("#kPaying", nf.format(paying));
    text("#kPayingNote", `${s.users.by_plan.createur} Créateur · ${s.users.by_plan.pro} Pro`);
    text("#kCost", usd.format(s.ai_cost_usd_30d));
    text("#kCostNote", "estimation à partir de vos tarifs fal.ai");

    const g = s.generations_30d;
    const total = s.daily.reduce((sum, d) => sum + d.generations, 0);
    text("#chartTotal", `${nf.format(total)} au total`);
    renderChart(s.daily);

    const rows = $("#dailyRows");
    rows.textContent = "";
    [...s.daily].reverse().forEach((d) => {
      const tr = rows.insertRow();
      tr.insertCell().textContent = dayLabel(d.date, { day: "numeric", month: "long", year: "numeric" });
      tr.insertCell().textContent = nf.format(d.generations);
      tr.insertCell().textContent = nf.format(d.new_users);
    });

    const users = $("#usersRows");
    users.textContent = "";
    s.recent_users.forEach((u) => {
      const tr = users.insertRow();
      const email = tr.insertCell();
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "link-btn";
      btn.textContent = u.email;
      btn.title = "Ajuster les crédits de ce compte";
      btn.addEventListener("click", () => { $("#cEmail").value = u.email; $("#cAmount").focus(); });
      email.append(btn);
      tr.insertCell().textContent = PLAN_NAMES[u.plan] || u.plan;
      const c = tr.insertCell(); c.className = "num"; c.textContent = nf.format(u.credits);
      const n = tr.insertCell(); n.className = "num"; n.textContent = nf.format(u.generations);
      tr.insertCell().textContent = dayLabel(u.created_at.slice(0, 10), { day: "numeric", month: "short", year: "numeric" });
    });

    const mini = $("#miniStats");
    mini.textContent = "";
    [
      ["Images", g.image], ["Avatars", g.avatar], ["Vidéos 5 s", g.video_5s], ["Vidéos 10 s", g.video_10s],
      ["Essais visiteurs", g.anonymous], ["Échecs (remboursés)", g.failed],
      ["Crédits distribués", s.credits_30d.granted], ["Crédits consommés", s.credits_30d.spent],
    ].forEach(([label, value]) => {
      const div = document.createElement("div");
      div.innerHTML = "<span></span><b></b>";
      div.children[0].textContent = label;
      div.children[1].textContent = nf.format(value);
      mini.append(div);
    });
    const cap = document.createElement("p");
    cap.className = "muted small";
    cap.textContent = "Sur les 30 derniers jours.";
    mini.prepend(cap);
  };

  const load = async () => {
    try {
      const stats = await api("/api/admin/stats");
      view("Admin"); // d'abord visible : le graphique se dessine à la largeur réelle
      render(stats);
    } catch (err) {
      if (err.status === 403) text("#deniedMsg", "Ton compte n'a pas les droits d'administration (variable REGAM_ADMIN_EMAILS).");
      view("Denied");
    }
  };

  $("#refreshBtn").addEventListener("click", load);
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => lastStats && renderChart(lastStats.daily), 150);
  });

  $("#creditForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = $("#creditMsg");
    const amount = Number($("#cAmount").value);
    msg.classList.remove("is-error");
    if (!$("#cEmail").checkValidity() || !$("#cEmail").value || !Number.isInteger(amount) || amount === 0) {
      msg.textContent = "Indique une adresse valide et un nombre entier non nul.";
      msg.classList.add("is-error");
      return;
    }
    try {
      const r = await api("/api/admin/credits", { email: $("#cEmail").value.trim(), amount, note: $("#cNote").value.trim() });
      msg.textContent = `C'est fait : ${r.email} a maintenant ${nf.format(r.credits)} crédits.`;
      e.target.reset();
      load();
    } catch (err) {
      msg.textContent = err.message;
      msg.classList.add("is-error");
    }
  });

  load();
})();
