/* Bureau du Pasteur — application web (sans dépendance, sans étape de build). */
(() => {
  "use strict";

  // ───────────────────────── Utilitaires ─────────────────────────
  const $ = (sel, root = document) => root.querySelector(sel);
  const el = (tag, attrs = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "html") node.innerHTML = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else if (v !== null && v !== undefined) node.setAttribute(k, v);
    }
    for (const c of children.flat()) if (c !== null && c !== undefined) node.append(c.nodeType ? c : document.createTextNode(String(c)));
    return node;
  };
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtDate = (iso, withTime = true) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "short", ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}) });
  };
  const toLocalInput = (d) => { const p = (n) => String(n).padStart(2, "0"); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`; };
  const toast = (msg, err = false) => { const t = el("div", { class: err ? "err" : "" }, msg); $("#toast").append(t); setTimeout(() => t.remove(), err ? 6000 : 3500); };
  const STATUS_FR = { DRAFT: "Brouillon", READY_FOR_REVIEW: "À valider", BLOCKED: "Bloquée", APPROVED: "Validée", SCHEDULED: "Programmée", SENDING: "Envoi en cours", SENT: "Envoyée", FAILED: "Échec", CANCELLED: "Annulée", EXPIRED: "Expirée" };
  const LEVEL_ICON = { URGENT: "🔴", A_TRAITER: "🟠", A_VALIDER: "🟡", INFORMATION: "🟢" };
  const badge = (s) => el("span", { class: `badge ${s}` }, STATUS_FR[s] || s);

  // ───────────────────────── API ─────────────────────────
  const state = { token: localStorage.getItem("bp_token") || "", user: null, groups: [], route: "dashboard" };
  async function api(path, { method = "GET", body, raw = false } = {}) {
    const headers = { Accept: "application/json" };
    if (state.token) headers.Authorization = "Bearer " + state.token;
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const res = await fetch("/api" + path, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });
    if (res.status === 401 && !path.startsWith("/auth/login")) { logout(); throw new Error("Session expirée, reconnectez-vous."); }
    if (res.status === 204) return null;
    const data = raw ? await res.text() : await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : `Erreur ${res.status}`);
    return data;
  }
  const safe = async (fn) => { try { return await fn(); } catch (e) { toast(e.message, true); throw e; } };

  // ───────────────────────── Auth ─────────────────────────
  function logout() { state.token = ""; state.user = null; localStorage.removeItem("bp_token"); $("#app").classList.add("hidden"); $("#login").classList.remove("hidden"); }
  async function boot() {
    if (state.token) {
      try { state.user = await api("/auth/me"); } catch { state.token = ""; }
    }
    if (!state.user) { $("#login").classList.remove("hidden"); return; }
    $("#login").classList.add("hidden"); $("#app").classList.remove("hidden");
    $("#side-user").innerHTML = `<strong>${esc(state.user.name)}</strong><br><span class="badge">${esc(state.user.role)}</span>`;
    state.groups = await api("/groupes");
    refreshBadges();
    router();
  }
  $("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    try {
      const r = await api("/auth/login", { method: "POST", body: { email: f.get("email"), password: f.get("password") } });
      state.token = r.token; localStorage.setItem("bp_token", r.token); $("#login-error").classList.add("hidden"); boot();
    } catch (err) { $("#login-error").textContent = err.message; $("#login-error").classList.remove("hidden"); }
  });
  $("#btn-logout").addEventListener("click", logout);
  $("#btn-menu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  $("#btn-theme").addEventListener("click", () => { const r = document.documentElement; const next = r.dataset.theme === "dark" ? "light" : "dark"; r.dataset.theme = next; try { localStorage.setItem("bp_theme", next); } catch {} });
  try { const t = localStorage.getItem("bp_theme"); if (t) document.documentElement.dataset.theme = t; } catch {}
  $("#btn-notifs").addEventListener("click", showNotifications);

  async function refreshBadges() {
    try {
      const [p, n] = await Promise.all([api("/campagnes/a-valider"), api("/notifications?unread_only=true")]);
      const b = $("#badge-pending"); b.textContent = p.length; b.classList.toggle("hidden", p.length === 0);
      $("#notif-count").textContent = n.non_lues;
    } catch {}
  }

  // ───────────────────────── Modal ─────────────────────────
  function modal(title, content, { wide = false } = {}) {
    const root = $("#modal-root");
    const box = el("div", { class: "modal", style: wide ? "width:min(1000px,100%)" : "" }, el("header", {}, el("h2", {}, title), el("button", { class: "btn sm ghost", onclick: close }, "✕")), content);
    const back = el("div", { class: "modal-backdrop", onclick: (e) => { if (e.target === back) close(); } }, box);
    function close() { back.remove(); }
    root.append(back);
    return { close, box };
  }
  async function showNotifications() {
    const data = await api("/notifications");
    const list = el("div", { class: "list" }, ...data.notifications.map((n) => el("div", { class: "item" + (n.lien ? " clickable" : ""), onclick: () => { if (n.lien) { m.close(); location.hash = "#" + n.lien.replace("/dashboard", "/dashboard"); } } },
      el("div", {}, LEVEL_ICON[n.niveau] || "🟢"),
      el("div", { class: "body" }, el("div", { class: "title", style: n.lue ? "font-weight:400" : "" }, n.titre), el("div", { class: "meta" }, n.corps), el("div", { class: "meta" }, fmtDate(n.date))))));
    if (!data.notifications.length) list.append(el("p", { class: "muted" }, "Aucune notification."));
    const m = modal("🔔 Centre de notifications", el("div", {}, el("div", { class: "btn-row" }, el("button", { class: "btn sm", onclick: async () => { await api("/notifications/lire", { method: "POST" }); m.close(); refreshBadges(); } }, "Tout marquer comme lu")), list));
  }

  // ───────────────────────── Router ─────────────────────────
  const routes = {};
  const TITLES = { dashboard: "🏠 Dashboard", membres: "👥 Membres", communications: "💬 Communications", evenements: "📅 Événements", suivi: "❤️ Suivi", campagnes: "📨 Campagnes", statistiques: "📊 Statistiques", agents: "🤖 Agents IA", taches: "📋 Tâches", parametres: "⚙️ Paramètres", securite: "🔐 Sécurité" };
  async function router() {
    if (!state.user) return;
    const hash = location.hash.replace(/^#\/?/, "") || "dashboard";
    const [name, arg] = hash.split("/");
    state.route = routes[name] ? name : "dashboard";
    $("#page-title").textContent = TITLES[state.route];
    document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === state.route));
    $("#sidebar").classList.remove("open");
    const view = $("#view"); view.innerHTML = '<p class="muted">Chargement…</p>';
    try { view.replaceChildren(await routes[state.route](arg)); } catch (e) { view.replaceChildren(el("div", { class: "alert danger" }, e.message)); }
    refreshBadges();
  }
  window.addEventListener("hashchange", router);

  // ───────────────────────── Console du Directeur IA ─────────────────────────
  const EXAMPLES = ["Prépare une invitation pour dimanche.", "Rappelle aux responsables la réunion de mercredi", "Prépare la communication pour notre retraite de prière du mois prochain.", "Prépare une campagne pour les personnes qui n'ont pas encore confirmé leur présence", "Quels sont les événements des deux prochaines semaines ?", "Quelles campagnes attendent ma validation ?", "Qui dois-je recontacter ?", "Briefing du jour", "Prépare la communication pour dimanche", "Rappelle-moi d'appeler le pasteur invité"];
  function directorConsole() {
    const input = el("input", { type: "text", placeholder: "Dites au Directeur IA ce que vous souhaitez préparer…", "aria-label": "Commande" });
    const out = el("div");
    const send = async (text) => {
      if (!text.trim()) return;
      input.value = text; out.replaceChildren(el("p", { class: "muted" }, "Le Directeur IA travaille…"));
      try {
        const r = await api("/agents/commande", { method: "POST", body: { text } });
        const reply = el("div", { class: "reply" }, r.summary);
        const extras = el("div", { class: "btn-row" });
        for (const ref of r.campaign_refs || []) extras.append(el("a", { class: "btn sm", href: `#/campagnes/${ref}` }, `📨 ${ref}`));
        if (r.missing_info?.length) extras.append(el("span", { class: "badge A_TRAITER" }, "À compléter : " + r.missing_info.join(", ")));
        if (r.task_ids?.length) extras.append(el("a", { class: "btn sm", href: "#/taches" }, "📋 Voir les tâches"));
        out.replaceChildren(reply, extras); refreshBadges();
      } catch (e) { out.replaceChildren(el("div", { class: "alert danger" }, e.message)); }
    };
    const form = el("form", { class: "console", onsubmit: (e) => { e.preventDefault(); send(input.value); } }, input, el("button", { class: "btn primary", type: "submit" }, "Envoyer"));
    const chips = el("div", { class: "chips" }, ...EXAMPLES.map((x) => el("span", { class: "chip", onclick: () => send(x) }, x)));
    return el("div", { class: "card" }, el("h2", {}, "🤖 Directeur IA"), el("p", { class: "muted small" }, "Il comprend, prépare, présente… et attend votre validation. Il n'envoie jamais seul."), form, chips, out);
  }

  // ───────────────────────── Dashboard ─────────────────────────
  routes.dashboard = async () => {
    const [d, b] = await Promise.all([api("/dashboard"), api("/briefing")]);
    const tiles = el("div", { class: "grid cols-4" },
      tile("👥 Membres", d.membres.total, `${d.membres.actifs} actifs · ${d.membres.nouveaux} nouveaux`, "info", "#/membres"),
      tile("📨 À valider", d.communication.a_valider, d.communication.bloquees ? `${d.communication.bloquees} bloquée(s)` : "campagnes en attente", "validate", "#/campagnes/pending"),
      tile("📅 Événements à venir", d.evenements.a_venir, `${d.evenements.inscriptions} inscription(s)`, "ok", "#/evenements"),
      tile("🔔 Suivis à effectuer", d.membres.a_recontacter, "absences, nouveaux, anniversaires", "warn", "#/suivi"));
    const prio = el("div", { class: "card" }, el("h2", {}, `🌅 Briefing du ${b.date_texte}`),
      el("h3", {}, "🔥 Priorités"), b.priorites.length ? el("ul", {}, ...b.priorites.map((p) => el("li", {}, p))) : el("p", { class: "muted" }, "Journée calme."),
      el("h3", {}, "📅 Aujourd'hui"), b.aujourdhui.evenements.length ? el("ul", {}, ...b.aujourdhui.evenements.map((e) => el("li", {}, `${e.heure} — ${e.nom}${e.lieu ? " (" + e.lieu + ")" : ""}`))) : el("p", { class: "muted" }, "Aucun événement."),
      el("h3", {}, "📢 Communications à préparer"), b.communications.campagnes_a_preparer.length ? el("ul", {}, ...b.communications.campagnes_a_preparer.map((t) => el("li", {}, t))) : el("p", { class: "muted" }, "Rien dans les 48 h."),
      el("h3", {}, "🙏 À ne pas oublier"), b.a_ne_pas_oublier.length ? el("ul", {}, ...b.a_ne_pas_oublier.map((t) => el("li", {}, `${LEVEL_ICON[t.priorite] || ""} ${t.titre}${t.echeance ? " — " + t.echeance : ""}`))) : el("p", { class: "muted" }, "Rien d'enregistré."));
    const pending = el("div", { class: "card" }, el("h2", {}, "⏳ Validations en attente"),
      b.validations.campagnes_en_attente.length ? el("div", { class: "list" }, ...b.validations.campagnes_en_attente.map((c) => el("a", { class: "item clickable", href: `#/campagnes/${c.ref}` }, el("div", { class: "body" }, el("div", { class: "title" }, `${c.ref} — ${c.nom}`), el("div", { class: "meta" }, `${c.canal} · ${c.destinataires} destinataire(s) · envoi ${fmtDate(c.envoi)}`))))) : el("p", { class: "muted" }, "Aucune campagne n'attend votre validation. 🟢"),
      el("h3", { style: "margin-top:12px" }, "👥 Suivi"), b.suivi.personnes_a_recontacter.length ? el("ul", {}, ...b.suivi.personnes_a_recontacter.slice(0, 6).map((s) => el("li", {}, `${s.name} — ${s.fact}`))) : el("p", { class: "muted" }, "Personne à recontacter."));
    return el("div", {}, tiles, el("div", { style: "height:14px" }), directorConsole(), el("div", { class: "grid cols-2" }, prio, pending));
  };
  function tile(label, value, sub, cls, href) { const t = el("div", { class: `tile ${cls}` }, el("div", { class: "label" }, label), el("div", { class: "value" }, value ?? "—"), el("div", { class: "sub" }, sub)); if (href) { t.style.cursor = "pointer"; t.onclick = () => (location.hash = href); } return t; }

  // ───────────────────────── Campagnes ─────────────────────────
  routes.campagnes = async (arg) => {
    if (arg && arg !== "pending") return campaignDetail(arg);
    const filter = arg === "pending" ? "READY_FOR_REVIEW" : "";
    const list = await api("/campagnes" + (filter ? "?status=" + filter : ""));
    const tabs = el("div", { class: "tabs" }, el("a", { class: "btn sm" + (!filter ? " active" : ""), href: "#/campagnes" }, "Toutes"), el("a", { class: "btn sm" + (filter ? " active" : ""), href: "#/campagnes/pending" }, "🟡 À valider"), el("a", { class: "btn sm", href: "#/communications" }, "➕ Nouvelle campagne"));
    const rows = list.map((c) => el("tr", { class: "clickable", onclick: () => (location.hash = `#/campagnes/${c.ref}`) }, el("td", { class: "mono" }, c.ref), el("td", {}, c.nom, c.double_validation ? el("span", { class: "badge A_TRAITER", style: "margin-left:6px" }, "double validation") : ""), el("td", {}, badge(c.statut)), el("td", {}, c.canal), el("td", {}, c.nombre_destinataires), el("td", {}, fmtDate(c.date_envoi)), el("td", { class: "muted small" }, c.cree_par)));
    return el("div", {}, tabs, el("div", { class: "card table-wrap" }, list.length ? el("table", {}, el("thead", {}, el("tr", {}, ...["Réf.", "Campagne", "Statut", "Canal", "Dest.", "Envoi", "Créée par"].map((h) => el("th", {}, h)))), el("tbody", {}, ...rows)) : el("p", { class: "muted" }, "Aucune campagne.")));
  };

  async function campaignDetail(ref) {
    const c = await api(`/campagnes/${ref}`);
    const isPastor = state.user.role === "PASTEUR";
    const canAct = ["READY_FOR_REVIEW", "BLOCKED", "DRAFT"].includes(c.statut);
    const checks = el("ul", { class: "check-list" }, ...(c.anomalies.length ? c.anomalies : []).map((a) => el("li", { class: a.level === "BLOCK" ? "block" : "warn" }, `${a.label}${a.detail ? " — " + a.detail : ""}`)));
    if (!c.anomalies.length) checks.append(el("li", { class: "ok" }, "Tous les contrôles sont passés (destinataires, consentement, doublons, numéros, variables, groupe, date, heure, message)."));
    const preview = el("div", { class: "card" },
      el("div", { style: "display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px" }, el("h2", {}, "APERÇU DE LA CAMPAGNE"), badge(c.statut)),
      el("dl", { class: "kv" },
        el("dt", {}, "Nom"), el("dd", {}, `${c.nom} (${c.ref})`),
        el("dt", {}, "Objectif"), el("dd", {}, c.objectif || "—"),
        el("dt", {}, "Date et heure d'envoi"), el("dd", {}, c.date_envoi_texte),
        el("dt", {}, "Canal"), el("dd", {}, `${c.canal} · style ${c.style}`),
        el("dt", {}, "Nombre de destinataires"), el("dd", {}, el("strong", {}, c.nombre_destinataires)),
        el("dt", {}, "Groupes concernés"), el("dd", {}, c.groupes.join(", ") || (c.membres_cibles ? `${c.membres_cibles} membre(s) ciblé(s) individuellement` : "—")),
        el("dt", {}, "Événement"), el("dd", {}, c.evenement || "—"),
        el("dt", {}, "Variables utilisées"), el("dd", {}, c.variables.join(" ") || "aucune"),
        el("dt", {}, "Personnes exclues"), el("dd", {}, c.exclus.length ? el("details", {}, el("summary", {}, `${c.exclus.length} — voir le détail`), el("ul", {}, ...c.exclus.map((x) => el("li", {}, `${x.name} : ${x.reason}`)))) : "aucune"),
        el("dt", {}, "Coût estimé"), el("dd", {}, c.canal === "EMAIL" ? "—" : `${c.cout_estime_eur.toFixed(2)} €${c.segments_sms ? ` (${c.segments_sms} segment(s) SMS)` : ""}`),
        el("dt", {}, "Créée / modifiée par"), el("dd", {}, `${c.cree_par} / ${c.modifie_par}`),
        el("dt", {}, "Validée par"), el("dd", {}, c.valide_par ? `${c.valide_par} le ${fmtDate(c.valide_le)}` : "— (en attente)")),
      el("h3", { style: "margin-top:12px" }, "Message complet" + (c.objet ? ` — objet : ${c.objet}` : "")), el("pre", { class: "msg" }, c.message),
      el("div", { class: "muted small" }, "Aperçu pour un destinataire fictif :"), el("pre", { class: "msg" }, c.apercu_rendu),
      el("h3", {}, "Risques ou anomalies détectés"), checks,
      c.double_validation ? el("div", { class: "alert warn" }, `⚠️ Cette campagne concerne ${c.nombre_destinataires} personnes${c.bloquee ? "" : " : une double validation est requise (réponse exacte « CONFIRMER L'ENVOI »)."}`) : "");
    const actions = el("div", { class: "btn-row" });
    if (canAct) {
      if (isPastor && c.statut === "READY_FOR_REVIEW") actions.append(el("button", { class: "btn validate", onclick: () => approve(c) }, "🟢 VALIDER ET ENVOYER"));
      else if (c.statut === "READY_FOR_REVIEW") actions.append(el("span", { class: "alert info", style: "margin:0" }, "🟡 En attente de validation du pasteur"));
      actions.append(el("button", { class: "btn modify", onclick: () => editCampaign(c) }, "🟡 MODIFIER"));
      actions.append(el("button", { class: "btn danger", onclick: () => cancelCampaign(c) }, "🔴 ANNULER"));
      actions.append(el("button", { class: "btn", onclick: () => safe(async () => { await api(`/campagnes/${ref}/controler`, { method: "POST" }); toast("Contrôles relancés."); router(); }) }, "🔍 Relancer les contrôles"));
      if (c.statut === "READY_FOR_REVIEW") actions.append(el("button", { class: "btn", onclick: () => safe(async () => { const r = await api(`/campagnes/${ref}/envoyer-lien-validation`, { method: "POST" }); modal("📱 Lien de validation mobile", el("div", {}, el("p", {}, "Le lien a été envoyé au téléphone du pasteur (si un canal est configuré). Vous pouvez aussi l'ouvrir directement :"), el("p", {}, el("a", { href: r.link, target: "_blank" }, r.link)), el("p", { class: "muted small" }, "Usage unique · lié au contenu exact de cette campagne · exige le mot de passe du pasteur."))); }) }, "📱 Envoyer le lien de validation"));
    }
    if (["APPROVED", "SCHEDULED"].includes(c.statut)) actions.append(el("button", { class: "btn danger", onclick: () => cancelCampaign(c) }, "🔴 ANNULER la programmation"));
    if (c.confirmation_en_attente && isPastor) actions.replaceChildren(confirmBox(c));
    if (c.statut === "SENT" || c.statut === "FAILED") {
      const rep = await api(`/campagnes/${ref}/rapport`);
      preview.append(el("h3", {}, "📊 Rapport d'envoi"), el("dl", { class: "kv" }, el("dt", {}, "Envoyé le"), el("dd", {}, fmtDate(rep.envoye_le)), el("dt", {}, "Envoyés / livrés / échecs"), el("dd", {}, `${rep.envois.envoyes} / ${rep.envois.livres} / ${rep.envois.echecs}`), el("dt", {}, "Fournisseur"), el("dd", {}, rep.resultat?.provider || "—")), rep.erreurs.length ? el("ul", {}, ...rep.erreurs.map((e) => el("li", { class: "small" }, e))) : "");
    }
    const audit = await api(`/audit?entity_ref=${ref}`);
    const hist = el("div", { class: "card" }, el("h2", {}, "📋 Historique"), el("ul", { class: "timeline" }, ...audit.map((a) => el("li", {}, el("span", { class: "muted" }, fmtDate(a.date)), el("span", {}, `${a.acteur} · ${a.action}${a.details ? " · " + summarize(a.details) : ""}`)))));
    return el("div", {}, el("a", { href: "#/campagnes", class: "btn sm ghost" }, "← Campagnes"), preview, actions, hist);
  }
  const summarize = (d) => Object.entries(d).filter(([k]) => !["fields"].includes(k) || true).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(",") : typeof v === "object" && v ? JSON.stringify(v).slice(0, 60) : v}`).join(" · ").slice(0, 140);

  async function approve(c) {
    if (!confirm(`Valider et envoyer « ${c.nom} » à ${c.nombre_destinataires} destinataire(s) le ${c.date_envoi_texte} ?`)) return;
    await safe(async () => {
      const r = await api(`/campagnes/${c.ref}/valider`, { method: "POST", body: { content_hash: null } });
      if (r.double_validation) { toast("Double validation requise."); router(); } else { toast(r.preview.statut === "SENT" ? `Envoyée : ${r.resultat.sent} message(s).` : `Campagne ${STATUS_FR[r.preview.statut].toLowerCase()}.`); router(); }
    });
  }
  function confirmBox(c) {
    const input = el("input", { type: "text", placeholder: "CONFIRMER L'ENVOI", style: "max-width:320px" });
    return el("div", { class: "alert warn", style: "width:100%" }, el("strong", {}, `⚠️ Cette campagne concerne ${c.nombre_destinataires} personnes.`), el("p", {}, `Date : ${c.date_envoi_texte} · Canal : ${c.canal}. Confirmez-vous l'envoi ? Tapez exactement « CONFIRMER L'ENVOI ».`), el("div", { class: "btn-row" }, input, el("button", { class: "btn validate", onclick: () => safe(async () => { const r = await api(`/campagnes/${c.ref}/confirmer`, { method: "POST", body: { phrase: input.value } }); toast(r.preview.statut === "SENT" ? `Envoyée : ${r.resultat.sent} message(s).` : "Campagne programmée."); router(); }) }, "Confirmer"), el("button", { class: "btn danger", onclick: () => cancelCampaign(c) }, "🔴 Annuler")));
  }
  async function cancelCampaign(c) {
    const reason = prompt(`Annuler la campagne ${c.ref} ? Motif (facultatif) :`);
    if (reason === null) return;
    await safe(async () => { await api(`/campagnes/${c.ref}/annuler`, { method: "POST", body: { reason } }); toast("Campagne annulée."); router(); });
  }
  function editCampaign(c) {
    const f = campaignForm({ name: c.nom, objective: c.objectif, message: c.message, subject: c.objet, channel: c.canal, style: c.style, send_at: c.date_envoi, group_ids: state.groups.filter((g) => c.groupes.includes(g.nom)).map((g) => g.id) }, async (body) => {
      await safe(async () => { await api(`/campagnes/${c.ref}`, { method: "PATCH", body }); toast("Campagne modifiée : contrôles relancés, validation à refaire."); m.close(); router(); });
    }, "Enregistrer les modifications");
    const m = modal(`🟡 Modifier ${c.ref}`, f, { wide: true });
  }

  function campaignForm(init, onSubmit, label = "Créer la campagne") {
    const g = (name, node) => el("label", { class: "field" + (name === "message" ? " wide" : "") }, name === "message" ? "Message (variables : {PRENOM} {NOM} {DATE} {HEURE} {LIEU} {EVENEMENT})" : name, node);
    const inputs = {
      name: el("input", { type: "text", name: "name", value: init.name || "", required: "" }),
      objective: el("input", { type: "text", name: "objective", value: init.objective || "" }),
      channel: el("select", { name: "channel" }, ...["SMS", "WHATSAPP", "EMAIL"].map((v) => el("option", { value: v, selected: init.channel === v ? "" : null }, v))),
      style: el("select", { name: "style" }, ...["chaleureux", "pastoral", "motivant", "evangelisation", "evenementiel", "administratif", "rappel_urgent"].map((v) => el("option", { value: v, selected: init.style === v ? "" : null }, v))),
      send_at: el("input", { type: "datetime-local", name: "send_at", value: init.send_at ? toLocalInput(new Date(init.send_at)) : toLocalInput(new Date(Date.now() + 3600e3)) }),
      subject: el("input", { type: "text", name: "subject", value: init.subject || "", placeholder: "E-mail uniquement" }),
      message: el("textarea", { name: "message", required: "" }, init.message || ""),
      event_id: el("select", { name: "event_id" }, el("option", { value: "" }, "— aucun —")),
    };
    api("/evenements").then((evs) => evs.forEach((e) => inputs.event_id.append(el("option", { value: e.id, selected: init.event_id === e.id ? "" : null }, `${e.nom} — ${fmtDate(e.date)}`))));
    const groupsBox = el("div", { class: "chips" }, ...state.groups.map((gr) => el("label", { class: "chip" }, el("input", { type: "checkbox", value: gr.id, checked: (init.group_ids || []).includes(gr.id) ? "" : null, style: "margin-right:4px" }), `${gr.nom} (${gr.effectif})`)));
    const form = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); const group_ids = [...groupsBox.querySelectorAll("input:checked")].map((i) => Number(i.value)); onSubmit({ name: inputs.name.value, objective: inputs.objective.value, channel: inputs.channel.value, style: inputs.style.value, send_at: inputs.send_at.value ? new Date(inputs.send_at.value).toISOString().slice(0, 19) : null, subject: inputs.subject.value, message: inputs.message.value, event_id: inputs.event_id.value ? Number(inputs.event_id.value) : null, group_ids }); } },
      g("Nom de la campagne", inputs.name), g("Objectif", inputs.objective), g("Canal", inputs.channel), g("Style", inputs.style), g("Date et heure d'envoi", inputs.send_at), g("Objet", inputs.subject), g("Événement lié", inputs.event_id),
      el("label", { class: "field wide" }, "Groupes concernés", groupsBox), g("message", inputs.message),
      el("div", { class: "btn-row", style: "grid-column:1/-1" }, el("button", { class: "btn primary", type: "submit" }, label), el("span", { class: "muted small" }, "La campagne sera contrôlée puis présentée au pasteur. Rien ne part sans sa validation.")));
    return form;
  }

  // ───────────────────────── Communications ─────────────────────────
  routes.communications = async () => {
    const evs = await api("/evenements");
    const kind = el("select", {}, ...Object.entries({ invitation: "Invitation", rappel: "Rappel", motivation: "Message de motivation", pratique: "Rappel pratique", remerciement: "Remerciement", encouragement: "Encouragement", bienvenue: "Bienvenue", anniversaire: "Anniversaire", mois: "Message du mois", annonce: "Annonce" }).map(([v, l]) => el("option", { value: v }, l)));
    const channel = el("select", {}, ...["SMS", "WHATSAPP", "EMAIL"].map((v) => el("option", { value: v }, v)));
    const event = el("select", {}, el("option", { value: "" }, "— sans événement —"), ...evs.map((e) => el("option", { value: e.id }, `${e.nom} — ${fmtDate(e.date)}`)));
    const out = el("div");
    let chosen = { message: "", style: "chaleureux" };
    const formHolder = el("div", { class: "card" }, el("h2", {}, "➕ Nouvelle campagne"));
    const renderForm = () => { formHolder.replaceChildren(el("h2", {}, "➕ Nouvelle campagne"), campaignForm({ message: chosen.message, style: chosen.style, channel: channel.value, event_id: event.value ? Number(event.value) : null, group_ids: [] }, async (body) => { await safe(async () => { const c = await api("/campagnes", { method: "POST", body }); toast(`Campagne ${c.ref} créée : ${STATUS_FR[c.statut]}.`); location.hash = `#/campagnes/${c.ref}`; }); })); };
    renderForm();
    const gen = async () => {
      out.replaceChildren(el("p", { class: "muted" }, "L'agent COMMUNICATION rédige les 7 styles…"));
      const v = await api(`/campagnes/variantes?kind=${kind.value}&channel=${channel.value}${event.value ? "&event_id=" + event.value : ""}`);
      out.replaceChildren(el("div", { class: "grid cols-2" }, ...Object.entries(v).map(([style, msg]) => el("div", { class: "item clickable", onclick: () => { chosen = { message: msg, style }; renderForm(); toast(`Style « ${style} » sélectionné.`); formHolder.scrollIntoView({ behavior: "smooth" }); } }, el("div", { class: "body" }, el("div", { class: "title" }, style), el("div", {}, msg))))));
    };
    return el("div", {}, el("div", { class: "card" }, el("h2", {}, "📢 Agent COMMUNICATION — propositions de message"), el("p", { class: "muted small" }, "Choisissez le type, le canal et l'événement : l'agent propose les 7 styles (chaleureux, pastoral, motivant, évangélisation, événementiel, administratif, rappel urgent). Cliquez sur une proposition pour la reprendre."),
      el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); gen(); } }, el("label", { class: "field" }, "Type", kind), el("label", { class: "field" }, "Canal", channel), el("label", { class: "field" }, "Événement", event), el("button", { class: "btn primary", type: "submit" }, "Proposer 7 styles")), out), formHolder);
  };

  // ───────────────────────── Membres ─────────────────────────
  routes.membres = async (arg) => {
    if (arg) { openMemberCard(Number(arg)); }
    const q = el("input", { type: "text", placeholder: "Rechercher (nom, téléphone, e-mail)…" });
    const groupSel = el("select", {}, el("option", { value: "" }, "Tous les groupes"), ...state.groups.map((g) => el("option", { value: g.id }, `${g.nom} (${g.effectif})`)));
    const tableWrap = el("div", { class: "card table-wrap" });
    const load = async () => {
      const list = await api(`/membres?q=${encodeURIComponent(q.value)}${groupSel.value ? "&group_id=" + groupSel.value : ""}`);
      tableWrap.replaceChildren(el("div", { class: "muted small", style: "margin-bottom:6px" }, `${list.length} membre(s)`), el("table", {}, el("thead", {}, el("tr", {}, ...["Nom", "Téléphone", "Groupes", "Consentements", "Statut"].map((h) => el("th", {}, h)))), el("tbody", {}, ...list.map((m) => el("tr", { class: "clickable", onclick: () => openMemberCard(m.id) }, el("td", {}, el("strong", {}, `${m.first_name} ${m.last_name}`), m.is_new ? el("span", { class: "badge A_TRAITER", style: "margin-left:6px" }, "nouveau") : "", m.responsibility ? el("div", { class: "muted small" }, m.responsibility) : ""), el("td", { class: "mono" }, m.phone || "—"), el("td", { class: "small" }, m.groups.join(", ")), el("td", { class: "small" }, [m.consent_sms && "SMS", m.consent_whatsapp && "WhatsApp", m.consent_email && "E-mail"].filter(Boolean).join(" + ") || el("span", { class: "muted" }, "aucun")), el("td", {}, m.unsubscribed ? el("span", { class: "badge CANCELLED" }, "désinscrit") : el("span", { class: "badge " + (m.is_active ? "SENT" : "DRAFT") }, m.is_active ? "Actif" : "Inactif")))))));
    };
    q.addEventListener("input", () => load()); groupSel.addEventListener("change", load); load();
    const groupsCard = el("div", { class: "card" }, el("h2", {}, "Groupes"), el("div", { class: "chips" }, ...state.groups.map((g) => el("span", { class: "chip", onclick: () => openGroup(g.id) }, `${g.dynamique ? "⚡ " : ""}${g.nom} · ${g.effectif}`))),
      el("details", { style: "margin-top:10px" }, el("summary", {}, "➕ Créer un groupe"), groupForm()));
    return el("div", {}, el("div", { class: "card" }, el("form", { class: "inline", onsubmit: (e) => e.preventDefault() }, el("label", { class: "field" }, "Recherche", q), el("label", { class: "field" }, "Groupe", groupSel), el("button", { class: "btn primary", type: "button", onclick: () => memberForm() }, "➕ Nouveau membre"), el("button", { class: "btn", type: "button", onclick: () => importMembers() }, "📥 Importer (iPhone, CSV, WhatsApp)"))), tableWrap, groupsCard);
  };
  function importMembers() {
    const file = el("input", { type: "file", accept: ".vcf,.csv,.tsv,.txt,text/vcard,text/csv,text/plain" });
    const groupSel = el("select", {}, el("option", { value: "" }, "Aucun groupe particulier (seulement « Membres »)"), ...state.groups.filter((g) => !g.dynamique && g.nom !== "Membres").map((g) => el("option", { value: g.id }, g.nom)));
    const preview = el("div", {});
    const confirmBtn = el("button", { class: "btn primary", type: "button", disabled: "" }, "Importer");
    const consentBox = el("input", { type: "checkbox" });
    const consentRow = el("label", { class: "check hidden" }, consentBox, "");
    const send = async (dryRun) => {
      if (!file.files[0]) { toast("Choisissez d'abord un fichier.", true); return null; }
      const fd = new FormData();
      fd.append("file", file.files[0]);
      fd.append("dry_run", dryRun ? "true" : "false");
      if (groupSel.value) fd.append("group_id", groupSel.value);
      if (!dryRun) fd.append("skip", [...preview.querySelectorAll("input[data-idx]:not(:checked)")].map((i) => i.dataset.idx).join(","));
      if (!dryRun && consentBox.checked) fd.append("apply_consent", "true");
      const res = await fetch("/api/membres/import", { method: "POST", headers: { Authorization: "Bearer " + state.token }, body: fd });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `Erreur ${res.status}`);
      return data;
    };
    const FORMAT_FR = { vcard: "répertoire (vCard)", csv: "tableur (CSV)", whatsapp: "discussion WhatsApp" };
    const ACTION_FR = { creer: "nouveau membre", ajouter_au_groupe: "déjà membre : ajout au groupe", ignorer: "" };
    const refreshCount = () => {
      const kept = [...preview.querySelectorAll("input[data-idx]")].filter((b) => b.checked).length;
      confirmBtn.disabled = kept === 0;
      confirmBtn.textContent = `Importer ${kept} contact(s)`;
    };
    const setAll = (v) => { preview.querySelectorAll("input[data-idx]").forEach((b) => { b.checked = v; }); refreshCount(); };
    const analyse = () => safe(async () => {
      const r = await send(true);
      if (!r) return;
      const groupName = groupSel.value ? groupSel.options[groupSel.selectedIndex].text : "";
      preview.replaceChildren(
        el("p", { class: "small" }, `Format détecté : ${FORMAT_FR[r.format] || r.format} · ${r.total} contact(s) trouvé(s) · `, el("strong", {}, `${r.nouveaux} nouveau(x)`), ` · ${r.existants} déjà membre(s)`, groupName ? ` (seront ajoutés à « ${groupName} »)` : "", ` · ${r.ignores} ignoré(s)`),
        consentRow,
        el("div", { class: "btn-row", style: "margin-bottom:6px" }, el("button", { class: "btn sm", type: "button", onclick: () => setAll(true) }, "Tout cocher"), el("button", { class: "btn sm", type: "button", onclick: () => setAll(false) }, "Tout décocher"), el("span", { class: "muted small" }, "Décochez les contacts qui ne font pas partie de la communauté.")),
        el("div", { class: "table-wrap" }, el("table", {}, el("thead", {}, el("tr", {}, ...["", "Nom", "Téléphone", "E-mail", "Remarque"].map((h) => el("th", {}, h)))),
          el("tbody", {}, ...r.contacts.map((c, idx) => el("tr", { style: c.importable ? "" : "opacity:.55" },
            el("td", {}, c.importable ? el("input", { type: "checkbox", checked: "", "data-idx": idx, onchange: refreshCount }) : "⏭️"),
            el("td", {}, `${c.prenom} ${c.nom}`.trim() || "—", c.source && c.source !== `${c.prenom} ${c.nom}`.trim() ? el("div", { class: "muted small" }, c.source) : ""),
            el("td", { class: "mono" }, c.telephone || "—"), el("td", { class: "small" }, c.email || "—"),
            el("td", { class: "small" }, c.probleme || ACTION_FR[c.action] || "", c.consentement && c.importable ? " · consentement ✓" : "")))))));
      consentRow.classList.toggle("hidden", !r.avec_consentement);
      consentRow.lastChild.textContent = ` Enregistrer le consentement (SMS, WhatsApp, e-mail) des ${r.avec_consentement} contact(s) ayant répondu « Oui » à la question de consentement du formulaire, avec la date de leur réponse (y compris les membres déjà créés qui n'ont encore aucun consentement)`;
      refreshCount();
    });
    file.addEventListener("change", analyse);
    const m = modal("📥 Importer des membres", el("div", {},
      el("p", { class: "muted small" }, "Fichiers acceptés : répertoire iPhone / Mac / Google exporté en vCard (.vcf), tableau CSV (Prénom, Nom, Téléphone, E-mail), ou discussion de groupe WhatsApp exportée (.txt). Les doublons sont ignorés automatiquement. Aucun consentement n'est déduit d'un import : il se coche ensuite sur chaque fiche."),
      el("details", { class: "small", style: "margin-bottom:10px" }, el("summary", {}, "Comment récupérer le fichier ?"),
        el("ul", {}, el("li", {}, el("strong", {}, "iPhone : "), "Contacts → ouvrez une liste (ou « Tous les contacts ») → maintenez un contact appuyé → « Sélectionner » → cochez tout → « Partager » → enregistrez le .vcf dans Fichiers ou envoyez-le-vous par e-mail/AirDrop."),
          el("li", {}, el("strong", {}, "Mac : "), "app Contacts → sélectionnez les contacts (⌘A pour tout) → Fichier → Exporter → « Exporter la vCard… »."),
          el("li", {}, el("strong", {}, "iCloud : "), "icloud.com/contacts → ⌘A → roue crantée → « Exporter la vCard »."),
          el("li", {}, el("strong", {}, "Groupe WhatsApp : "), "ouvrez le groupe → nom du groupe → tout en bas « Exporter la discussion » → « Sans médias » → enregistrez le .txt. Les participants enregistrés dans votre téléphone arrivent avec leur nom (importez d'abord votre répertoire pour qu'ils soient retrouvés et ajoutés au groupe), les autres avec leur numéro."))),
      el("form", { class: "inline", onsubmit: (e) => e.preventDefault() }, el("label", { class: "field" }, "Fichier", file), el("label", { class: "field" }, "Ajouter aussi au groupe", groupSel)),
      preview,
      el("div", { class: "btn-row" }, confirmBtn, el("button", { class: "btn", type: "button", onclick: () => m.close() }, "Annuler"))), { wide: true });
    groupSel.addEventListener("change", () => { if (file.files[0]) analyse(); });
    confirmBtn.addEventListener("click", () => safe(async () => {
      confirmBtn.disabled = true;
      const r = await send(false);
      if (!r) { confirmBtn.disabled = false; return; }
      state.groups = await api("/groupes");
      toast(`${r.crees} membre(s) créé(s)` + (r.ajoutes_au_groupe ? `, ${r.ajoutes_au_groupe} ajouté(s) au groupe` : "") + (r.completes ? `, ${r.completes} fiche(s) complétée(s)` : "") + `, ${r.ignores} ignoré(s).`);
      m.close(); router();
    }));
  }
  function groupForm() {
    const name = el("input", { type: "text", required: "", placeholder: "Nom du groupe" }), desc = el("input", { type: "text", placeholder: "Description" });
    const dyn = el("select", {}, el("option", { value: "" }, "Groupe classique (membres ajoutés à la main)"), el("option", { value: '{"active_days":90,"consent":"SMS"}' }, "⚡ Actifs 90 jours + consentement SMS"), el("option", { value: '{"joined_within_days":60}' }, "⚡ Arrivés dans les 60 derniers jours"), el("option", { value: '{"absent_since_days":30}' }, "⚡ Absents depuis 30 jours"), el("option", { value: '{"consent":"WHATSAPP"}' }, "⚡ Consentement WhatsApp"));
    return el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => { await api("/groupes", { method: "POST", body: { name: name.value, description: desc.value, dynamic_rule: dyn.value ? JSON.parse(dyn.value) : null } }); state.groups = await api("/groupes"); toast("Groupe créé."); router(); }); } }, el("label", { class: "field" }, "Nom", name), el("label", { class: "field" }, "Description", desc), el("label", { class: "field" }, "Type", dyn), el("button", { class: "btn primary", type: "submit" }, "Créer"));
  }
  async function openGroup(id) {
    const g = await api(`/groupes/${id}`);
    modal(`${g.dynamique ? "⚡ " : ""}${g.nom} · ${g.effectif} membre(s)`, el("div", {}, g.description ? el("p", { class: "muted" }, g.description) : "", g.dynamique ? el("p", { class: "small" }, "Règle dynamique : ", el("code", {}, JSON.stringify(g.dynamique))) : "", el("div", { class: "chips" }, ...g.membres.map((m) => el("span", { class: "chip", onclick: () => openMemberCard(m.id) }, m.nom))), !g.systeme && state.user.role === "PASTEUR" ? el("div", { class: "btn-row" }, el("button", { class: "btn danger sm", onclick: () => safe(async () => { if (!confirm("Supprimer ce groupe ?")) return; await api(`/groupes/${id}`, { method: "DELETE" }); state.groups = await api("/groupes"); router(); }) }, "Supprimer le groupe")) : ""));
  }
  function memberForm(existing) {
    const v = existing || {};
    const f = {};
    const field = (label, name, type = "text", extra = {}) => { f[name] = el("input", { type, name, value: v[name] ?? "", ...extra }); return el("label", { class: "field" }, label, f[name]); };
    const consent = (label, name) => { f[name] = el("input", { type: "checkbox", checked: v[name] ? "" : null }); return el("label", { class: "check" }, f[name], label); };
    const groupsBox = el("div", { class: "chips" }, ...state.groups.filter((g) => !g.dynamique).map((g) => el("label", { class: "chip" }, el("input", { type: "checkbox", value: g.id, checked: (v.groupes || []).some((x) => x.id === g.id) ? "" : null, style: "margin-right:4px" }), g.nom)));
    const form = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => {
      const body = { first_name: f.prenom.value, last_name: f.nom.value, phone: f.telephone.value, email: f.email.value, whatsapp: f.whatsapp.value, responsibility: f.responsabilite.value, birthday: f.anniversaire.value, preferred_channel: f.canal.value, consent_sms: f.consent_sms.checked, consent_whatsapp: f.consent_whatsapp.checked, consent_email: f.consent_email.checked, group_ids: [...groupsBox.querySelectorAll("input:checked")].map((i) => Number(i.value)), admin_notes: f.notes.value, joined_at: f.arrivee.value ? new Date(f.arrivee.value).toISOString().slice(0, 19) : null };
      if (existing) await api(`/membres/${existing.id}`, { method: "PATCH", body }); else await api("/membres", { method: "POST", body });
      state.groups = await api("/groupes"); toast(existing ? "Fiche mise à jour." : "Membre créé."); m.close(); router(); }); } },
      field("Prénom", "prenom", "text", { required: "" }), field("Nom", "nom", "text", { required: "" }), field("Téléphone (+33…)", "telephone"), field("E-mail", "email", "email"), field("WhatsApp (si différent)", "whatsapp"), field("Responsabilité", "responsabilite"), field("Anniversaire (JJ-MM)", "anniversaire", "text", { placeholder: "27-09" }), field("Date d'arrivée", "arrivee", "date"),
      el("label", { class: "field" }, "Canal préféré", (f.canal = el("select", {}, ...["SMS", "WHATSAPP", "EMAIL"].map((c) => el("option", { value: c, selected: v.canal_prefere === c ? "" : null }, c))))),
      el("div", { class: "field wide", style: "flex-direction:row;gap:16px;flex-wrap:wrap" }, el("span", {}, "Consentements (enregistrés avec date) :"), consent("SMS", "consent_sms"), consent("WhatsApp", "consent_whatsapp"), consent("E-mail", "consent_email")),
      el("label", { class: "field wide" }, "Groupes", groupsBox),
      el("label", { class: "field wide" }, "Notes administratives autorisées (jamais d'information spirituelle, émotionnelle ou médicale)", (f.notes = el("textarea", {}, v.notes_administratives || ""))),
      el("div", { class: "btn-row", style: "grid-column:1/-1" }, el("button", { class: "btn primary", type: "submit" }, existing ? "Enregistrer" : "Créer le membre")));
    if (existing) { f.prenom.value = v.prenom; f.nom.value = v.nom; f.telephone.value = v.telephone; f.email.value = v.email; f.whatsapp.value = v.whatsapp === v.telephone ? "" : v.whatsapp; f.responsabilite.value = v.responsabilite; f.anniversaire.value = v.anniversaire; f.consent_sms.checked = v.consentement.sms; f.consent_whatsapp.checked = v.consentement.whatsapp; f.consent_email.checked = v.consentement.email; }
    const m = modal(existing ? "✏️ Modifier la fiche" : "➕ Nouveau membre", form, { wide: true });
  }
  async function openMemberCard(id) {
    const c = await api(`/membres/${id}`);
    const isPastor = state.user.role === "PASTEUR";
    const body = el("div", {},
      el("dl", { class: "kv" }, el("dt", {}, "Groupe(s)"), el("dd", {}, c.groupes.map((g) => g.nom).join(", ") || "—"), el("dt", {}, "Statut"), el("dd", {}, c.statut, c.nouveau ? " · nouveau membre" : "", c.desinscrit ? " · ⛔ désinscrit" : ""), el("dt", {}, "Responsabilité"), el("dd", {}, c.responsabilite || "—"), el("dt", {}, "Dernière participation"), el("dd", {}, c.derniere_participation || "—"), el("dt", {}, "Dernier événement"), el("dd", {}, c.dernier_evenement || "—"), el("dt", {}, "Communication"), el("dd", {}, c.communication), el("dt", {}, "Consentement"), el("dd", {}, c.consentement.sms || c.consentement.whatsapp || c.consentement.email ? `Oui (${c.consentement.enregistre_le ? fmtDate(c.consentement.enregistre_le) : "date inconnue"})` : "Non"), el("dt", {}, "Téléphone / e-mail"), el("dd", { class: "mono" }, `${c.telephone || "—"} · ${c.email || "—"}`), el("dt", {}, "Arrivée / anniversaire"), el("dd", {}, `${c.date_arrivee || "—"} · ${c.anniversaire || "—"}`)),
      el("div", { class: "btn-row" },
        el("button", { class: "btn sm primary", onclick: () => { const kind = prompt("Type de message : encouragement, bienvenue, anniversaire, annonce", "encouragement"); if (!kind) return; safe(async () => { const r = await api(`/membres/${id}/message?kind=${kind}`, { method: "POST" }); toast(r.summary); m.close(); location.hash = `#/campagnes/${r.campaign_refs[0]}`; }); } }, "✉️ Envoyer message"),
        el("button", { class: "btn sm", onclick: () => { const t = prompt("Note administrative :"); if (t) safe(async () => { await api(`/membres/${id}/notes`, { method: "POST", body: { content: t } }); toast("Note ajoutée."); m.close(); openMemberCard(id); }); } }, "📝 Ajouter une note"),
        el("button", { class: "btn sm", onclick: () => { const g = state.groups.filter((x) => !x.dynamique); const choice = prompt("Ajouter au groupe :\n" + g.map((x) => `${x.id} — ${x.nom}`).join("\n")); if (choice) safe(async () => { await api(`/groupes/${Number(choice)}/membres/${id}`, { method: "POST" }); state.groups = await api("/groupes"); toast("Ajouté au groupe."); m.close(); openMemberCard(id); }); } }, "👥 Ajouter à un groupe"),
        el("button", { class: "btn sm", onclick: () => { const t = prompt(`Rappel concernant ${c.prenom} ${c.nom} :`); if (t) safe(async () => { await api("/taches", { method: "POST", body: { title: t, details: `Membre #${id}`, priority: "A_TRAITER" } }); toast("Rappel créé dans les tâches."); }); } }, "⏰ Créer rappel"),
        el("button", { class: "btn sm", onclick: () => memberForm(c) }, "✏️ Modifier"),
        el("button", { class: "btn sm", onclick: () => safe(async () => { const r = await fetch(`/api/membres/${id}/export`, { headers: { Authorization: "Bearer " + state.token } }); const blob = await r.blob(); const a = el("a", { href: URL.createObjectURL(blob), download: `membre-${id}.json` }); a.click(); toast("Export RGPD téléchargé."); }) }, "⬇️ Export RGPD"),
        el("button", { class: "btn sm", onclick: () => safe(async () => { if (!confirm("Retirer tous les consentements (désinscription) ?")) return; await api(`/membres/${id}/desinscription`, { method: "POST" }); m.close(); openMemberCard(id); }) }, "⛔ Désinscrire"),
        isPastor ? el("button", { class: "btn sm danger", onclick: () => safe(async () => { if (!confirm("Effacer définitivement les données personnelles de ce membre (anonymisation irréversible) ?")) return; await api(`/membres/${id}`, { method: "DELETE" }); toast("Données effacées."); m.close(); router(); }) }, "🗑️ Effacer (RGPD)") : ""),
      el("h3", { style: "margin-top:12px" }, "📜 Historique"),
      el("div", { class: "grid cols-2" }, el("div", {}, el("strong", {}, "Participations"), el("ul", { class: "small" }, ...(c.participations.length ? c.participations.map((p) => el("li", {}, `${fmtDate(p.date, false)} — ${p.evenement} : ${p.present === true ? "présent" : p.present === false ? "absent" : p.confirme ? "confirmé" : p.inscrit ? "inscrit" : "—"}`)) : [el("li", { class: "muted" }, "Aucune")]))), el("div", {}, el("strong", {}, "Notes"), el("ul", { class: "small" }, ...(c.notes.length ? c.notes.map((n) => el("li", {}, `${fmtDate(n.date, false)} — ${n.contenu}`)) : [el("li", { class: "muted" }, "Aucune")])), c.notes_administratives ? el("p", { class: "small" }, el("strong", {}, "Notes administratives : "), c.notes_administratives) : "")));
    const m = modal(`👤 ${c.prenom} ${c.nom}`, body, { wide: true });
  }

  // ───────────────────────── Événements ─────────────────────────
  routes.evenements = async (arg) => {
    const evs = await api("/evenements?days=120");
    const rows = evs.map((e) => el("tr", { class: "clickable", onclick: () => openEvent(e.id) }, el("td", {}, fmtDate(e.date)), el("td", {}, el("strong", {}, e.nom), e.informations_manquantes.length ? el("div", { class: "small", style: "color:var(--warn)" }, "À compléter : " + e.informations_manquantes.join(", ")) : ""), el("td", {}, e.lieu || "—"), el("td", {}, e.public), el("td", { class: "small" }, `${e.statistiques.inscrits} inscrits · ${e.statistiques.confirmes} confirmés${e.capacite ? " / " + e.capacite : ""}`), el("td", { class: "small" }, `${e.campagnes.filter((c) => !["CANCELLED", "EXPIRED"].includes(c.status)).length} campagne(s)`)));
    if (arg) openEvent(Number(arg));
    return el("div", {}, el("div", { class: "btn-row", style: "margin:0 0 12px" }, el("button", { class: "btn primary", onclick: () => eventForm() }, "➕ Nouvel événement"), el("a", { class: "btn", href: "#/parametres" }, "⏰ Automatisations")), el("div", { class: "card table-wrap" }, evs.length ? el("table", {}, el("thead", {}, el("tr", {}, ...["Date", "Événement", "Lieu", "Public", "Inscriptions", "Communication"].map((h) => el("th", {}, h)))), el("tbody", {}, ...rows)) : el("p", { class: "muted" }, "Aucun événement à venir.")));
  };
  function eventForm(existing) {
    const v = existing || {};
    const f = {};
    const field = (label, name, type = "text", extra = {}) => { f[name] = el("input", { type, value: v[name] ?? "", ...extra }); return el("label", { class: "field" }, label, f[name]); };
    f.audience = el("select", {}, el("option", { value: "" }, "Tous les membres"), ...state.groups.map((g) => el("option", { value: g.id, selected: v.public === g.nom ? "" : null }, g.nom)));
    f.sunday = el("input", { type: "checkbox", checked: v.is_recurring_sunday ? "" : null }); f.reg = el("input", { type: "checkbox", checked: v.inscription ? "" : null });
    const form = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => {
      const body = { name: f.nom.value, description: f.description.value, starts_at: new Date(f.date.value).toISOString().slice(0, 19), location: f.lieu.value, speaker: f.intervenant.value, audience_group_id: f.audience.value ? Number(f.audience.value) : null, capacity: f.capacite.value ? Number(f.capacite.value) : null, registration_required: f.reg.checked, responsible: f.responsable.value, responsible_welcome: f.accueil.value, responsible_media: f.media.value, responsible_intercession: f.intercession.value, is_recurring_sunday: f.sunday.checked };
      const ev = existing ? await api(`/evenements/${existing.id}`, { method: "PATCH", body }) : await api("/evenements", { method: "POST", body }); toast(existing ? "Événement mis à jour." : "Événement créé."); m.close(); router(); openEvent(ev.id); }); } },
      field("Nom", "nom", "text", { required: "" }), el("label", { class: "field" }, "Date et heure", (f.date = el("input", { type: "datetime-local", required: "", value: v.date ? toLocalInput(new Date(v.date)) : "" }))), field("Lieu", "lieu"), field("Intervenant", "intervenant"), el("label", { class: "field" }, "Public concerné", f.audience), field("Capacité", "capacite", "number"), field("Responsable", "responsable"), field("Responsable accueil", "accueil"), field("Responsable média", "media"), field("Responsable intercession", "intercession"),
      el("div", { class: "field", style: "flex-direction:row;gap:14px;align-items:center" }, el("label", { class: "check" }, f.reg, "Inscription requise"), el("label", { class: "check" }, f.sunday, "Culte du dimanche (récurrent)")),
      el("label", { class: "field wide" }, "Description", (f.description = el("textarea", {}, v.description || ""))),
      el("div", { class: "btn-row", style: "grid-column:1/-1" }, el("button", { class: "btn primary", type: "submit" }, existing ? "Enregistrer" : "Créer l'événement")));
    if (existing) { f.accueil.value = v.responsables.accueil; f.media.value = v.responsables.media; f.intercession.value = v.responsables.intercession; }
    const m = modal(existing ? "✏️ Modifier l'événement" : "➕ Nouvel événement", form, { wide: true });
  }
  async function openEvent(id) {
    const e = await api(`/evenements/${id}`);
    const chan = el("select", {}, ...["SMS", "WHATSAPP", "EMAIL"].map((v) => el("option", { value: v }, v)));
    const style = el("select", {}, ...["chaleureux", "pastoral", "motivant", "evangelisation", "evenementiel", "administratif", "rappel_urgent"].map((v) => el("option", { value: v }, v)));
    const body = el("div", {},
      el("dl", { class: "kv" }, el("dt", {}, "Date"), el("dd", {}, fmtDate(e.date)), el("dt", {}, "Lieu"), el("dd", {}, e.lieu || "⚠️ à préciser"), el("dt", {}, "Intervenant"), el("dd", {}, e.intervenant || "—"), el("dt", {}, "Public"), el("dd", {}, e.public), el("dt", {}, "Capacité / inscription"), el("dd", {}, `${e.capacite ?? "—"} · ${e.inscription ? "inscription requise" : "libre"}`), el("dt", {}, "Responsable"), el("dd", {}, e.responsable || "⚠️ à désigner"), el("dt", {}, "Accueil / média / intercession"), el("dd", {}, `${e.responsables.accueil || "⚠️"} / ${e.responsables.media || "⚠️"} / ${e.responsables.intercession || "⚠️"}`), el("dt", {}, "Statistiques"), el("dd", {}, `${e.statistiques.inscrits} inscrits · ${e.statistiques.confirmes} confirmés · ${e.statistiques.presents} présents · ${e.statistiques.absents} absents`)),
      e.description ? el("p", {}, e.description) : "",
      e.informations_manquantes.length ? el("div", { class: "alert warn" }, "Informations manquantes : " + e.informations_manquantes.join(", ")) : "",
      el("h3", {}, "📢 Calendrier de communication"),
      el("table", {}, el("thead", {}, el("tr", {}, el("th", {}, "Étape"), el("th", {}, "Type"), el("th", {}, "Envoi prévu"), el("th", {}, "Campagne"))), el("tbody", {}, ...e.communications.map((s) => { const c = e.campagnes.find((x) => x.name.startsWith(s.label + " ")); return el("tr", {}, el("td", {}, s.label), el("td", {}, s.kind), el("td", {}, fmtDate(s.send_at), s.future ? "" : el("span", { class: "muted small" }, " (passé)")), el("td", {}, c ? el("a", { href: `#/campagnes/${c.ref}`, onclick: () => m.close() }, c.ref, " ", badge(c.status)) : el("span", { class: "muted" }, "à préparer"))); }))),
      el("form", { class: "inline", style: "margin-top:10px", onsubmit: (ev) => { ev.preventDefault(); safe(async () => { const r = await api(`/evenements/${id}/planifier`, { method: "POST", body: { channel: chan.value, style: style.value } }); toast(r.summary); m.close(); openEvent(id); }); } }, el("label", { class: "field" }, "Canal", chan), el("label", { class: "field" }, "Style", style), el("button", { class: "btn primary", type: "submit" }, "🗓️ Préparer toutes les campagnes (à valider)")),
      el("div", { class: "btn-row" }, el("button", { class: "btn sm", onclick: () => eventForm(e) }, "✏️ Modifier"), el("button", { class: "btn sm", onclick: () => attendanceForm(e) }, "✅ Présences / inscriptions"), el("button", { class: "btn sm", onclick: () => safe(async () => { const r = await api(`/evenements/${id}/compte-rendu`); modal("📝 Trame de compte rendu", el("pre", { class: "msg" }, r.template)); }) }, "📝 Compte rendu"), el("button", { class: "btn sm danger", onclick: () => safe(async () => { if (!confirm("Supprimer cet événement ?")) return; await api(`/evenements/${id}`, { method: "DELETE" }); m.close(); router(); }) }, "🗑️ Supprimer")));
    const m = modal(`📅 ${e.nom}`, body, { wide: true });
  }
  async function attendanceForm(e) {
    const members = await api("/membres");
    const sel = el("select", {}, ...members.map((mm) => el("option", { value: mm.id }, `${mm.first_name} ${mm.last_name}`)));
    const act = el("select", {}, el("option", { value: "registered" }, "Inscrit"), el("option", { value: "confirmed" }, "Confirmé"), el("option", { value: "present" }, "Présent"), el("option", { value: "absent" }, "Absent"));
    modal(`✅ ${e.nom} — présences`, el("form", { class: "inline", onsubmit: (ev) => { ev.preventDefault(); safe(async () => { const b = { member_id: Number(sel.value) }; if (act.value === "absent") b.present = false; else b[act.value] = true; const st = await api(`/evenements/${e.id}/presences`, { method: "POST", body: b }); toast(`Enregistré · ${st.inscrits} inscrits · ${st.confirmes} confirmés · ${st.presents} présents`); }); } }, el("label", { class: "field" }, "Membre", sel), el("label", { class: "field" }, "Action", act), el("button", { class: "btn primary", type: "submit" }, "Enregistrer")));
  }

  // ───────────────────────── Suivi ─────────────────────────
  routes.suivi = async () => {
    const s = await api("/suivi");
    const groups = { absence: [], nouveau: [], anniversaire: [] };
    s.data.suggestions.forEach((x) => (groups[x.reason] || (groups[x.reason] = [])).push(x));
    const section = (title, items, hint) => el("div", { class: "card" }, el("h2", {}, title), items.length ? el("div", { class: "list" }, ...items.map((x) => el("div", { class: "item clickable", onclick: () => openMemberCard(x.member_id) }, el("div", { class: "body" }, el("div", { class: "title" }, x.name), el("div", { class: "meta" }, x.fact), el("div", { class: "meta" }, "→ " + x.suggested_action))))) : el("p", { class: "muted" }, hint));
    return el("div", {}, el("div", { class: "alert info" }, "❤️ L'agent BERGER travaille uniquement à partir des faits enregistrés (présences, dates d'arrivée, anniversaires). Il ne déduit jamais un état spirituel, émotionnel ou médical. Vous décidez qui contacter."),
      el("div", { class: "btn-row", style: "margin-bottom:12px" }, el("button", { class: "btn primary", onclick: () => safe(async () => { const r = await api("/suivi/relance", { method: "POST" }); toast(r.summary); if (r.campaign_refs?.length) location.hash = `#/campagnes/${r.campaign_refs[0]}`; }) }, "✉️ Préparer une relance des absents (à valider)"), el("button", { class: "btn", onclick: () => safe(async () => { const r = await api("/agents/commande", { method: "POST", body: { text: "Prépare un message de bienvenue pour les nouveaux membres" } }); toast(r.summary); if (r.campaign_refs?.length) location.hash = `#/campagnes/${r.campaign_refs[0]}`; }) }, "👋 Message de bienvenue aux nouveaux"), el("button", { class: "btn", onclick: () => safe(async () => { const r = await api("/agents/commande", { method: "POST", body: { text: "Prépare les messages d'anniversaire" } }); toast(r.summary); }) }, "🎂 Messages d'anniversaire")),
      el("div", { class: "grid cols-3" }, section("🕊️ Absences prolongées", groups.absence, "Aucune absence prolongée dans les données."), section("🆕 Nouveaux membres à intégrer", groups.nouveau, "Aucun nouveau membre."), section("🎂 Anniversaires (7 jours)", groups.anniversaire, "Aucun anniversaire prochainement.")));
  };

  // ───────────────────────── Statistiques ─────────────────────────
  routes.statistiques = async () => {
    const d = await api("/dashboard");
    const kv = (obj, skip = []) => el("dl", { class: "kv" }, ...Object.entries(obj).filter(([k, v]) => !skip.includes(k) && typeof v !== "object").flatMap(([k, v]) => [el("dt", {}, k.replaceAll("_", " ")), el("dd", {}, v ?? "—")]));
    return el("div", { class: "grid cols-2" },
      el("div", { class: "card" }, el("h2", {}, "👥 Membres"), kv(d.membres, ["groupes"]), el("h3", { style: "margin-top:10px" }, "Groupes"), el("table", {}, el("tbody", {}, ...d.membres.groupes.map((g) => el("tr", {}, el("td", {}, `${g.dynamique ? "⚡ " : ""}${g.nom}`), el("td", {}, g.effectif)))))),
      el("div", { class: "card" }, el("h2", {}, "💬 Communication"), kv(d.communication), el("p", { class: "muted small" }, "Le taux de participation n'est affiché que lorsque des présences sont enregistrées.")),
      el("div", { class: "card" }, el("h2", {}, "📅 Événements"), kv(d.evenements, ["liste"]), el("table", {}, el("tbody", {}, ...d.evenements.liste.map((e) => el("tr", {}, el("td", {}, fmtDate(e.date)), el("td", {}, e.nom), el("td", { class: "small" }, `${e.inscrits} inscrits · ${e.confirmes} confirmés`)))))),
      el("div", { class: "card" }, el("h2", {}, "📋 Tâches du pasteur"), el("dl", { class: "kv" }, el("dt", {}, "🔴 Urgent"), el("dd", {}, d.taches.urgent.length), el("dt", {}, "Aujourd'hui"), el("dd", {}, d.taches.aujourdhui.length), el("dt", {}, "Cette semaine"), el("dd", {}, d.taches.cette_semaine.length), el("dt", {}, "🟡 En attente de validation"), el("dd", {}, d.taches.en_attente_de_validation))));
  };

  // ───────────────────────── Agents ─────────────────────────
  routes.agents = async () => {
    const a = await api("/agents");
    return el("div", {}, directorConsole(),
      el("div", { class: "card" }, el("h2", {}, "Organigramme"), el("p", { class: "muted small" }, `Fournisseur IA : ${a.fournisseur_ia} · modèle : ${a.modele}. Les données personnelles des membres ne sont jamais transmises au modèle.`), el("div", { class: "grid cols-4" }, ...a.agents.map((x) => el("div", { class: "tile" }, el("div", { class: "value", style: "font-size:1.4rem" }, `${x.icone} ${x.nom}`), el("div", { class: "sub" }, x.role))))),
      el("div", { class: "card" }, el("h2", {}, "Dernières interventions"), el("ul", { class: "timeline" }, ...a.dernieres_actions.map((r) => el("li", {}, el("span", { class: "muted" }, fmtDate(r.date)), el("span", {}, el("strong", {}, r.agent), ` · ${r.intention} · `, el("span", { class: "muted" }, r.commande), r.resume ? el("div", { class: "small" }, r.resume) : ""))))));
  };

  // ───────────────────────── Tâches ─────────────────────────
  routes.taches = async () => {
    const t = await api("/taches");
    const title = el("input", { type: "text", required: "", placeholder: "Nouvelle tâche…" }), prio = el("select", {}, ...Object.entries({ URGENT: "🔴 Urgent", A_TRAITER: "🟠 À traiter", A_VALIDER: "🟡 À valider", INFORMATION: "🟢 Information" }).map(([v, l]) => el("option", { value: v }, l))), due = el("input", { type: "datetime-local" });
    const form = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => { await api("/taches", { method: "POST", body: { title: title.value, priority: prio.value, due_at: due.value ? new Date(due.value).toISOString().slice(0, 19) : null } }); toast("Tâche créée."); router(); }); } }, el("label", { class: "field wide" }, "Tâche", title), el("label", { class: "field" }, "Priorité", prio), el("label", { class: "field" }, "Échéance", due), el("button", { class: "btn primary", type: "submit" }, "Ajouter"));
    const list = el("div", { class: "list" }, ...t.taches.map((x) => el("div", { class: "item" }, el("div", {}, LEVEL_ICON[x.priority] || ""), el("div", { class: "body" }, el("div", { class: "title" }, x.title), el("div", { class: "meta" }, `${x.due_at ? "Échéance " + fmtDate(x.due_at) + " · " : ""}créée par ${x.created_by}${x.campaign_ref ? " · " + x.campaign_ref : ""}`)), el("button", { class: "btn sm", onclick: () => safe(async () => { await api(`/taches/${x.id}/terminer`, { method: "POST" }); router(); }) }, "✓ Terminer"))));
    return el("div", {}, el("div", { class: "grid cols-4" }, tile("🔴 Urgent", t.synthese.urgent.length, "", "warn"), tile("Aujourd'hui", t.synthese.aujourdhui.length, "", "info"), tile("Cette semaine", t.synthese.cette_semaine.length, "", "ok"), tile("🟡 À valider", t.synthese.en_attente_de_validation, "campagnes", "validate", "#/campagnes/pending")), el("div", { class: "card", style: "margin-top:14px" }, form), el("div", { class: "card" }, t.taches.length ? list : el("p", { class: "muted" }, "Aucune tâche ouverte.")));
  };

  // ───────────────────────── Paramètres ─────────────────────────
  routes.parametres = async () => {
    const [p, autos] = await Promise.all([api("/parametres"), api("/automatisations")]);
    const isPastor = state.user.role === "PASTEUR";
    const autoList = el("div", { class: "list" }, ...autos.map((a) => el("div", { class: "item" }, el("div", {}, a.active ? "🟢" : "⚪"), el("div", { class: "body" }, el("div", { class: "title" }, a.nom), el("div", { class: "meta" }, a.description), el("div", { class: "meta" }, `${a.canal} · ${a.style} · validation du pasteur requise${a.derniere_execution ? " · dernière préparation " + fmtDate(a.derniere_execution) : ""}`)), isPastor ? el("div", { class: "btn-row", style: "margin:0" }, el("button", { class: "btn sm", onclick: () => safe(async () => { await api(`/automatisations/${a.id}?is_active=${!a.active}`, { method: "PATCH" }); router(); }) }, a.active ? "Désactiver" : "Activer"), el("button", { class: "btn sm danger", onclick: () => safe(async () => { if (!confirm("Supprimer ?")) return; await api(`/automatisations/${a.id}`, { method: "DELETE" }); router(); }) }, "🗑️")) : "")));
    const f = { name: el("input", { type: "text", required: "", placeholder: "Rappel du culte" }), kind: el("select", {}, ...Object.entries({ WEEKLY: "Chaque semaine", MONTHLY: "Chaque mois", DAILY: "Chaque jour", BEFORE_EVENT: "Avant chaque événement", AFTER_EVENT: "Après chaque événement" }).map(([v, l]) => el("option", { value: v }, l))), weekday: el("select", {}, ...["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"].map((d, i) => el("option", { value: i, selected: i === 6 ? "" : null }, d))), dom: el("input", { type: "number", min: 1, max: 28, value: 1 }), hour: el("input", { type: "number", min: 0, max: 23, value: 8 }), minute: el("input", { type: "number", min: 0, max: 59, value: 30 }), offset: el("input", { type: "number", value: 24 }), group: el("select", {}, el("option", { value: "" }, "Public de l'événement / tous"), ...state.groups.map((g) => el("option", { value: g.id }, g.nom))), channel: el("select", {}, ...["SMS", "WHATSAPP", "EMAIL"].map((v) => el("option", { value: v }, v))), style: el("select", {}, ...["chaleureux", "pastoral", "motivant", "evangelisation", "evenementiel", "administratif", "rappel_urgent"].map((v) => el("option", { value: v }, v))), tpl: el("input", { type: "text", placeholder: "Rappel {EVENEMENT}" }), msg: el("textarea", { placeholder: "Laissez vide pour laisser l'agent COMMUNICATION rédiger" }) };
    const form = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => { await api("/automatisations", { method: "POST", body: { name: f.name.value, kind: f.kind.value, weekday: Number(f.weekday.value), day_of_month: Number(f.dom.value), hour: Number(f.hour.value), minute: Number(f.minute.value), offset_hours: Number(f.offset.value), group_id: f.group.value ? Number(f.group.value) : null, channel: f.channel.value, style: f.style.value, campaign_name_template: f.tpl.value, message_template: f.msg.value } }); toast("Automatisation créée : elle préparera des campagnes à valider."); router(); }); } },
      el("label", { class: "field" }, "Nom", f.name), el("label", { class: "field" }, "Fréquence", f.kind), el("label", { class: "field" }, "Jour (hebdo)", f.weekday), el("label", { class: "field" }, "Jour du mois", f.dom), el("label", { class: "field" }, "Heure", f.hour), el("label", { class: "field" }, "Minute", f.minute), el("label", { class: "field" }, "Décalage (h) avant/après événement", f.offset), el("label", { class: "field" }, "Groupe", f.group), el("label", { class: "field" }, "Canal", f.channel), el("label", { class: "field" }, "Style", f.style), el("label", { class: "field" }, "Nom de campagne", f.tpl), el("label", { class: "field wide" }, "Message (facultatif)", f.msg), el("div", { class: "btn-row", style: "grid-column:1/-1" }, el("button", { class: "btn primary", type: "submit" }, "Créer l'automatisation")));
    return el("div", {},
      el("div", { class: "grid cols-2" },
        el("div", { class: "card" }, el("h2", {}, "⚙️ Configuration"), el("dl", { class: "kv" }, el("dt", {}, "Application"), el("dd", {}, `${p.application} (${p.environnement})`), el("dt", {}, "Fuseau"), el("dd", {}, p.fuseau), el("dt", {}, "IA"), el("dd", {}, p.ia.fournisseur === "template" ? "Gabarits hors-ligne (aucune donnée ne sort du serveur)" : `${p.ia.fournisseur} · ${p.ia.modele}`), el("dt", {}, "Double validation"), el("dd", {}, `au-delà de ${p.validation.seuil_double_validation} destinataires · phrase « ${p.validation.phrase_confirmation} »`), el("dt", {}, "Lien mobile"), el("dd", {}, `valide ${p.validation.duree_lien_heures} h, usage unique`), el("dt", {}, "Planificateur"), el("dd", {}, `${p.planificateur.actif ? "actif" : "inactif"} · toutes les ${p.planificateur.intervalle_s} s · briefing à ${p.planificateur.heure_briefing} h`), el("dt", {}, "Coût SMS estimé"), el("dd", {}, `${p.cout_sms_eur} €`)), el("h3", { style: "margin-top:10px" }, "📲 Canaux"), el("ul", {}, ...p.canaux.map((c) => el("li", {}, el("span", { class: "dot " + (c.live ? "on" : "off") }), `${c.channel} : ${c.provider}${c.live ? "" : " (mode démonstration : aucun message ne quitte le serveur)"}`))), isPastor ? el("div", { class: "btn-row" }, el("button", { class: "btn", onclick: () => safe(async () => { const r = await api("/planificateur/executer", { method: "POST" }); toast(`Cycle exécuté : ${r.prepared.length} préparée(s), ${r.expired.length} expirée(s), ${r.sent.length} envoyée(s).`); refreshBadges(); }) }, "▶️ Exécuter un cycle du planificateur")) : ""),
        el("div", { class: "card" }, el("h2", {}, "⏰ Automatisations"), el("p", { class: "muted small" }, "Une automatisation PRÉPARE une campagne et vous la présente. Elle n'envoie jamais un message collectif sans votre validation, même à 3 h du matin."), autoList, isPastor ? el("details", { style: "margin-top:10px" }, el("summary", {}, "➕ Nouvelle automatisation"), form) : "")));
  };

  // ───────────────────────── Sécurité ─────────────────────────
  routes.securite = async () => {
    const isPastor = state.user.role === "PASTEUR";
    const [audit, p] = await Promise.all([api("/audit?limit=150"), api("/parametres")]);
    const users = isPastor ? await api("/auth/users") : [];
    const uf = { email: el("input", { type: "email", required: "" }), name: el("input", { type: "text", required: "" }), pw: el("input", { type: "password", required: "", minlength: 8 }), role: el("select", {}, ...["SECRETAIRE", "LECTEUR", "PASTEUR"].map((r) => el("option", { value: r }, r))), phone: el("input", { type: "text", placeholder: "+33…" }) };
    const userForm = el("form", { class: "inline", onsubmit: (e) => { e.preventDefault(); safe(async () => { await api("/auth/users", { method: "POST", body: { email: uf.email.value, name: uf.name.value, password: uf.pw.value, role: uf.role.value, phone: uf.phone.value } }); toast("Compte créé."); router(); }); } }, el("label", { class: "field" }, "E-mail", uf.email), el("label", { class: "field" }, "Nom", uf.name), el("label", { class: "field" }, "Mot de passe", uf.pw), el("label", { class: "field" }, "Rôle", uf.role), el("label", { class: "field" }, "Téléphone", uf.phone), el("button", { class: "btn primary", type: "submit" }, "Créer"));
    return el("div", {},
      el("div", { class: "grid cols-2" },
        el("div", { class: "card" }, el("h2", {}, "🛡️ Règles appliquées"), el("ul", {}, el("li", {}, "Aucun envoi collectif sans validation explicite du rôle PASTEUR ; le silence n'est jamais une validation (expiration)."), el("li", {}, "Double validation « CONFIRMER L'ENVOI » au-delà du seuil ou pour les campagnes sensibles."), el("li", {}, "Toute modification après validation annule la validation ; l'empreinte du contenu est vérifiée avant l'envoi."), el("li", {}, "Consentement par canal, désinscription STOP immédiate, export et effacement des données."), el("li", {}, "Séparation des rôles : PASTEUR (valide), SECRÉTAIRE (prépare), LECTEUR (consulte)."), el("li", {}, "Journal d'audit complet ; l'IA ne reçoit jamais la liste des membres ni leurs coordonnées."), el("li", {}, "Les données ne servent à l'entraînement d'aucun modèle externe."))),
        el("div", { class: "card" }, el("h2", {}, "👤 Comptes et rôles"), isPastor ? el("div", {}, el("table", {}, el("tbody", {}, ...users.map((u) => el("tr", {}, el("td", {}, u.name), el("td", { class: "mono small" }, u.email), el("td", {}, el("span", { class: "badge" }, u.role)), el("td", {}, u.id !== state.user.id ? el("button", { class: "btn sm danger", onclick: () => safe(async () => { if (!confirm("Désactiver ce compte ?")) return; await api(`/auth/users/${u.id}`, { method: "DELETE" }); router(); }) }, "Désactiver") : ""))))), el("details", { style: "margin-top:10px" }, el("summary", {}, "➕ Nouveau compte"), userForm)) : el("p", { class: "muted" }, "Gestion des comptes réservée au pasteur."))),
      el("div", { class: "card" }, el("h2", {}, "📋 Journal d'audit"), el("div", { class: "table-wrap" }, el("table", {}, el("thead", {}, el("tr", {}, ...["Date", "Acteur", "Action", "Objet", "Détails"].map((h) => el("th", {}, h)))), el("tbody", {}, ...audit.map((a) => el("tr", {}, el("td", { class: "small" }, fmtDate(a.date)), el("td", {}, a.acteur), el("td", { class: "mono small" }, a.action), el("td", { class: "small" }, `${a.type} ${a.ref}`), el("td", { class: "small muted" }, a.details ? summarize(a.details) : ""))))))));
  };

  boot();
})();
