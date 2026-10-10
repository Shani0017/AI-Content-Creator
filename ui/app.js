"use strict";
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const api = async (url, body) => {
  const r = await fetch(url, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error((await r.text()).slice(0, 200));
  return r.json();
};
const toast = (msg, kind = "") => {
  const t = document.createElement("div");
  t.className = "toast " + kind; t.textContent = msg;
  $("#toasts").appendChild(t); setTimeout(() => t.remove(), 4800);
};
const mediaUrl = rel => "/media/" + rel.split("/").map(encodeURIComponent).join("/");
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let S = { status: null, catalog: null, type: null, form: {}, recipe: null, jobs: [] };

/* ---------------- navigation ---------------- */
$$("nav a").forEach(a => a.onclick = () => {
  $$("nav a").forEach(x => x.classList.toggle("on", x === a));
  $$(".page").forEach(p => p.classList.toggle("on", p.id === "page-" + a.dataset.page));
  if (a.dataset.page === "library") loadLibrary();
  if (a.dataset.page === "settings") renderSettings();
  if (a.dataset.page === "publish") loadPublish();
  window.scrollTo(0, 0);
});

/* ---------------- composer ---------------- */
const COMPOSERS = {
  math: () => `
    <h3>Math &amp; Puzzles</h3><p class="muted">Word problems with the working-out shown step by step.</p>
    <label>Where do the problems come from?</label>
    ${seg("source", [["templates", "Built-in (always correct)"], ["ai", "Written by my AI model"], ["mixed", "Half and half"]], "templates")}
    <label>Topic hint <span class="muted" style="text-transform:none;letter-spacing:0">(AI only, optional)</span></label>
    <input id="f_topic" placeholder="e.g. money, speed, ages, probability">
    <label>How many videos?</label>${stepper("count", 3, 1, 50)}
    <label>Colour theme</label>${seg("theme", [["midnight", "Midnight"], ["ocean", "Ocean"], ["sunset", "Sunset"], ["forest", "Forest"]], "midnight")}`,
  balls: () => `
    <h3>Satisfying Balls</h3><p class="muted">Every video is physics-checked: real collisions, nothing fake, ends when everything is done.</p>
    <label>Which simulations?</label>
    <div class="chips" id="simChips">${S.catalog.balls.map(b => `<button data-id="${esc(b.id)}">${esc(b.name)}</button>`).join("")}</div>
    <p class="muted" style="margin-top:8px">Leave all unselected to get a random mix.</p>
    <label>How many videos?</label>${stepper("count", 3, 1, 50)}`,
  music: () => `
    <h3>Music Balls</h3><p class="muted">Public-domain songs only, so they are safe to post.</p>
    <label>Look</label>
    <div class="chips" id="sceneChips">${S.catalog.scenes.map(s => `<button data-id="${esc(s.id)}">${esc(s.name)}</button>`).join("")}</div>
    <label>Songs</label>
    <div class="chips" id="songChips">${S.catalog.songs.map(s => `<button data-id="${esc(s)}">${esc(s)}</button>`).join("")}</div>
    <p class="muted" style="margin-top:8px">Nothing selected = random mix. Every video also gets its own colours and ball shape.</p>
    <label>How many videos?</label>${stepper("count", 3, 1, 50)}`,
  story: () => `
    <h3>Story &amp; Facts</h3><p class="muted">Your AI model writes an original script, a voice reads it, keywords pop on screen.</p>
    <label>Topics <span class="muted" style="text-transform:none;letter-spacing:0">(one per line)</span></label>
    <textarea id="f_topics" placeholder="Why the sky is blue&#10;3 habits of calm people&#10;The history of chess"></textarea>
    <label>How many videos?</label>${stepper("count", 1, 1, 20)}
    <label>Colour theme</label>${seg("theme", [["midnight", "Midnight"], ["ocean", "Ocean"], ["sunset", "Sunset"], ["forest", "Forest"]], "midnight")}`,
  reference: () => `
    <h3>From a reference link</h3>
    <p class="muted">Paste a link to a video you like (YouTube, Instagram, TikTok and more). The app studies <b>how</b> it is made — pacing, colours, topic, tone — and makes a new original video in that style. Only use links you have the right to study.</p>
    <label>Video link</label>
    <input id="f_url" placeholder="https://...">
    <div class="row"><button class="btn primary" id="analyze">Analyze this video</button></div>
    <div id="recipeBox"></div>`,
};
const seg = (key, opts, def) => { S.form[key] = def; return `<div class="seg" data-key="${key}">${opts.map(([v, t]) => `<button data-v="${v}" class="${v === def ? "on" : ""}">${t}</button>`).join("")}</div>`; };
const stepper = (key, def, min, max) => { S.form[key] = def; return `<div class="stepper" data-key="${key}" data-min="${min}" data-max="${max}"><button data-d="-1">−</button><b>${def}</b><button data-d="1">+</button></div>`; };

function openComposer(type) {
  S.type = type; S.form = {}; S.recipe = null;
  $$(".type").forEach(t => t.classList.toggle("on", t.dataset.type === type));
  const box = $("#composer");
  box.hidden = false;
  box.innerHTML = COMPOSERS[type]() + (type === "reference" ? "" : `<div class="row"><button class="btn primary" id="go">Generate</button><span class="muted" id="goHint"></span></div>`);
  $$(".seg", box).forEach(sg => $$("button", sg).forEach(b => b.onclick = () => { $$("button", sg).forEach(x => x.classList.toggle("on", x === b)); S.form[sg.dataset.key] = b.dataset.v; }));
  $$(".stepper", box).forEach(st => $$("button", st).forEach(b => b.onclick = () => {
    const v = Math.max(+st.dataset.min, Math.min(+st.dataset.max, S.form[st.dataset.key] + (+b.dataset.d)));
    S.form[st.dataset.key] = v; $("b", st).textContent = v;
  }));
  $$(".chips", box).forEach(c => $$("button", c).forEach(b => b.onclick = () => b.classList.toggle("on")));
  if ($("#go")) $("#go").onclick = submitCurrent;
  if ($("#analyze")) $("#analyze").onclick = analyze;
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
$$(".type").forEach(t => t.onclick = () => openComposer(t.dataset.type));

const picked = id => $$("#" + id + " button.on").map(b => b.dataset.id);

async function submitCurrent() {
  const f = S.form, t = S.type;
  let params = { count: f.count };
  if (t === "math") Object.assign(params, { source: f.source, theme: f.theme, topic: $("#f_topic")?.value || "" });
  if (t === "balls") params.sims = picked("simChips");
  if (t === "music") Object.assign(params, { songs: picked("songChips"), scenes: picked("sceneChips") });
  if (t === "story") {
    const topics = ($("#f_topics").value || "").split("\n").map(s => s.trim()).filter(Boolean);
    if (!topics.length) return toast("Add at least one topic", "bad");
    Object.assign(params, { topics, theme: f.theme });
  }
  await enqueue(t, params);
}
async function enqueue(kind, params) {
  try {
    await api("/api/jobs", { kind, params });
    toast("Added to the queue", "good"); poll();
  } catch (e) { toast("Could not start: " + e.message, "bad"); }
}

/* ---------------- reference ---------------- */
async function analyze() {
  const url = $("#f_url").value.trim();
  if (!url) return toast("Paste a link first", "bad");
  $("#analyze").disabled = true;
  try {
    const job = await api("/api/jobs", { kind: "reference", params: { url } });
    poll();
    const t = setInterval(async () => {
      const j = await api("/api/jobs/" + job.id);
      $("#recipeBox").innerHTML = `<div class="job running"><div class="top"><span>Studying the video</span><span class="state">${Math.round(j.progress * 100)}%</span></div><div class="msg">${esc(j.message)}</div><div class="bar"><i style="width:${j.progress * 100}%"></i></div></div>`;
      if (j.state === "done" && j.recipe) { clearInterval(t); $("#analyze").disabled = false; showRecipe(j.recipe); }
      if (j.state === "error") { clearInterval(t); $("#analyze").disabled = false; $("#recipeBox").innerHTML = `<p class="muted" style="color:var(--bad);margin-top:14px">${esc(j.error)}</p>`; }
    }, 1000);
  } catch (e) { $("#analyze").disabled = false; toast(e.message, "bad"); }
}
function darkest(pal) {
  if (!pal || !pal.length) return null;
  const lum = c => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  const c = [...pal].sort((a, b) => lum(a) - lum(b))[0];
  return c.map(v => Math.round(v * 0.35));
}
function refParams(r, n, kind) {
  const st = r.stats || {};
  const ideasOk = (r.new_topic_ideas || []).filter(x => x && x.length > 6);
  const p = { count: n, palette: r.palette, bg: darkest(r.palette), pace: r.pacing || st.pacing, duration: st.duration_s,
    style: { tone: r.tone, pacing: r.pacing, hook: r.hook, title_style: r.title_style },
    hint: [r.topic, r.hook, r.source_title, r.description].filter(Boolean).join(" "),
    topics: ideasOk.length ? ideasOk : [r.topic || r.source_title || "a surprising fact"], topic: r.topic };
  if (kind === "math") p.source = "mixed";
  if (kind === "music" && r.palette?.length) p.hue = hueOf(r.palette);
  return p;
}
function showRecipe(r) {
  S.recipe = r;
  const sw = (r.palette || []).map(c => `<i style="background:rgb(${c.join(",")})"></i>`).join("");
  const ideas = (r.new_topic_ideas || []).map(esc).join("<br>• ");
  const st = r.stats || {};
  const kind0 = ["balls", "music", "math", "story"].includes(r.category) ? r.category : "story";
  $("#recipeBox").innerHTML = `
    <div class="recipe">
      <div><span class="tag">${esc(r.category)}</span><span class="tag">${esc(r.pacing || st.pacing || "")}</span><span class="tag">${esc(r.tone || "")}</span>
        <span class="tag" style="background:rgba(255,255,255,.1);color:#c9d2ff">${r.from === "ai" ? "studied by AI" : "studied by rules (AI gave no usable answer)"}</span></div>
      <div><b>About:</b> ${esc(r.topic || r.source_title)}</div>
      <div><b>Opens with:</b> ${esc(r.hook || "-")}</div>
      <div class="swatches">${sw}</div>
      <div><b>Length:</b> ${st.duration_s || "?"} s &middot; <b>cuts:</b> ${st.cuts ?? "?"} &middot; <b>speech:</b> ${r.has_speech ? "yes" : "no"}</div>
      <div><b>New ideas in this style:</b><br>• ${ideas || "-"}</div>
    </div>
    <div class="note-box"><b>What the new video copies:</b> the colours, the pace, the length and (for spoken videos) the topic and tone.
      <b>What it can't copy:</b> the exact pictures - it is built from the closest style the app has.</div>
    <div class="auto-box" id="autoBox"><b>Making your video now.</b> The app picked the closest style: <b>${esc(kindName(kind0))}</b>.
      Watch the <b>Queue</b> on the right; it shows up in the Library when it finishes.</div>
    <details class="gd mini"><summary>Make more videos or choose a different style</summary><div class="gd-body">
      <label>Style</label>
      ${seg("refkind", [["math", "Math & Puzzles"], ["story", "Story & Facts"], ["balls", "Satisfying Balls"], ["music", "Music Balls"]], kind0)}
      <label>How many videos?</label>${stepper("count", 3, 1, 20)}
      <div class="row"><button class="btn primary" id="makeLike">Make videos like this</button></div>
    </div></details>`;
  const box = $("#recipeBox");
  $$(".seg", box).forEach(sg => $$("button", sg).forEach(b => b.onclick = () => { $$("button", sg).forEach(x => x.classList.toggle("on", x === b)); S.form[sg.dataset.key] = b.dataset.v; }));
  $$(".stepper", box).forEach(stp => $$("button", stp).forEach(b => b.onclick = () => {
    const v = Math.max(+stp.dataset.min, Math.min(+stp.dataset.max, S.form[stp.dataset.key] + (+b.dataset.d)));
    S.form[stp.dataset.key] = v; $("b", stp).textContent = v;
  }));
  $("#makeLike").onclick = async () => { await enqueue(S.form.refkind, refParams(r, S.form.count, S.form.refkind)); };
  if (!r._started) { r._started = true; enqueue(kind0, refParams(r, 1, kind0)); }
}
const kindName = k => ({ math: "Math & Puzzles", story: "Story & Facts", balls: "Satisfying Balls", music: "Music Balls" }[k] || k);
function hueOf(pal) {
  let best = pal[0], bs = -1;
  pal.forEach(([r, g, b]) => { const mx = Math.max(r, g, b), mn = Math.min(r, g, b), s = mx ? (mx - mn) / mx : 0; if (s * mx > bs) { bs = s * mx; best = [r, g, b]; } });
  const [r, g, b] = best.map(v => v / 255), mx = Math.max(r, g, b), d = mx - Math.min(r, g, b);
  let h = d === 0 ? 0 : mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return ((h / 6) + 1) % 1;
}

/* ---------------- queue ---------------- */
let pollTimer = null;
function renderJobs(el, jobs) {
  // keyed in-place update: existing cards are only edited, never rebuilt, so nothing blinks
  if (!jobs.length) { if (!el.querySelector(".empty")) el.innerHTML = `<div class="empty">Your jobs show up here.</div>`; return; }
  const empty = el.querySelector(".empty"); if (empty) empty.remove();
  const want = new Set(jobs.map(j => j.id));
  $$(".job", el).forEach(n => { if (!want.has(n.dataset.id)) n.remove(); });
  let prev = null;
  jobs.forEach(j => {
    let n = el.querySelector(`.job[data-id="${j.id}"]`);
    if (!n) {
      n = document.createElement("div");
      n.className = "job"; n.dataset.id = j.id;
      n.innerHTML = `<div class="top"><span class="jl"></span><span class="state"></span></div><div class="msg"></div><div class="bar"><i></i></div>`;
    }
    n.className = "job " + j.state + (n.dataset.seen ? " seen" : "");
    n.dataset.seen = "1";
    const set = (sel, txt) => { const t = n.querySelector(sel); if (t.textContent !== txt) t.textContent = txt; };
    set(".jl", label(j.kind));
    set(".state", j.state === "running" ? Math.round(j.progress * 100) + "%" : j.state);
    set(".msg", j.state === "error" ? j.error : j.message);
    const w = Math.round(j.progress * 100) + "%";
    const bar = n.querySelector(".bar i"); if (bar.style.width !== w) bar.style.width = w;
    const at = prev ? prev.nextSibling : el.firstChild;                    // keep newest-first order without re-creating nodes
    if (n !== at) el.insertBefore(n, at);
    prev = n;
  });
}
async function poll() {
  try { S.jobs = await api("/api/jobs"); } catch { return; }
  const el = $("#jobs");
  const active = S.jobs.filter(j => ["queued", "running"].includes(j.state)).length;
  $("#queueNote").textContent = active ? `${active} running or waiting` : (S.jobs.length ? "All done" : "Nothing running");
  renderJobs(el, S.jobs);
  clearTimeout(pollTimer);
  pollTimer = setTimeout(poll, active ? 1000 : 4000);
  if (!S.seenDone) S.seenDone = new Set(S.jobs.filter(j => j.state === "done").map(j => j.id));
  S.jobs.filter(j => j.state === "done" && !S.seenDone.has(j.id)).forEach(j => { S.seenDone.add(j.id); if (j.kind !== "reference") { toast("Finished — see Library", "good"); loadLibrary(); } });
}
const label = k => ({ math: "Math & Puzzles", balls: "Satisfying Balls", music: "Music Balls", story: "Story & Facts", reference: "Studying reference", setup: "Downloading voice files", pull: "Downloading AI model", publish: "Publishing to Facebook" }[k] || k);

/* ---------------- library ---------------- */
async function loadLibrary() {
  const lib = await api("/api/library");
  $("#libCount").textContent = lib.length;
  $("#library").innerHTML = lib.length ? lib.map((v, i) => `
    <div class="vid" data-i="${i}"><img loading="lazy" src="${mediaUrl(v.path.replace(/[^/]+$/, v.poster))}" alt="">
      <div class="play"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></div>
      <div class="meta">${esc(v.name)}<small>${(v.size / 1048576).toFixed(1)} MB · ${label(v.kind)}</small></div></div>`).join("")
    : `<div class="empty" style="grid-column:1/-1">No videos yet. Make one from the Create page.</div>`;
  $$(".vid").forEach(el => el.onclick = () => { const v = lib[+el.dataset.i]; $("#player").src = mediaUrl(v.path); $("#modal").hidden = false; $("#player").play(); });
}
$("#closeModal").onclick = $("#modal").onclick = e => { if (e.target.id === "modal" || e.target.id === "closeModal") { $("#modal").hidden = true; $("#player").pause(); } };
$("#openFolder").onclick = () => api("/api/open-folder", {});

/* ---------------- settings / status ---------------- */
async function loadStatus() {
  try { S.status = await api("/api/status"); } catch { return; }
  const st = S.status;
  $("#ver").textContent = "v" + st.version;
  const ol = st.tools.ollama;
  $("#health").innerHTML = [["Video engine", st.tools.ffmpeg], ["Voice", st.tools.voice], ["AI model", ol.up && ol.models.length]]
    .map(([n, ok]) => `<div><i class="${ok ? "ok" : ""}"></i>${n}</div>`).join("");
  const u = st.update || {};
  $("#updateBanner").hidden = !u.available;
  if (typeof paintUpdate === "function") paintUpdate(u);
  if (u.available) { $("#updTitle").textContent = `Version ${u.latest} is available`; $("#updNotes").textContent = (u.notes || "").split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#")).map(l => l.replace(/^[-*]\s*/, "")).slice(0, 2).join("  ·  ") || "New features and fixes."; }
}
function renderSettings() {
  const st = S.status; if (!st) return;
  const ol = st.tools.ollama;
  $("#checks").innerHTML = [
    ["Video engine (ffmpeg)", st.tools.ffmpeg, "built in"],
    ["Voice-over (Kokoro)", st.tools.voice, st.tools.voice ? "ready" : "download needed"],
    ["Word timing (Whisper)", true, "on first use"],
    ["Ollama", ol.up, ol.up ? ol.models.length + " model(s)" : "not running"],
  ].map(([n, ok, note]) => `<li><i class="${ok ? "ok" : ""}">${ok ? "✓" : "!"}</i>${n}<em>${note}</em></li>`).join("");
  $("#dlVoice").disabled = st.tools.voice;
  $("#modelSel").innerHTML = ol.models.length ? ol.models.map(m => `<option ${m === st.settings.ollama_model ? "selected" : ""}>${esc(m)}</option>`).join("") : `<option value="">No models yet</option>`;
  $("#ollamaUrl").value = st.settings.ollama_url;
  $("#updState").textContent = `You have v${st.version}`;
}
$("#saveSettings").onclick = async () => {
  await api("/api/settings", { ollama_model: $("#modelSel").value, ollama_url: $("#ollamaUrl").value });
  toast("Saved", "good"); loadStatus();
};
$("#pullBtn").onclick = async () => { await enqueue("pull", { model: $("#pullName").value.trim() }); };
$("#dlVoice").onclick = async () => { await enqueue("setup", {}); };
$("#mkShortcut").onclick = async () => {
  try { await api("/api/shortcut", {}); toast("Shortcut created on your desktop", "good"); } catch (e) { toast("Could not create it: " + e.message, "bad"); }
};
$("#quitApp").onclick = async () => {
  if (!confirm("Close the app? Any video that is being made will stop.")) return;
  try { await api("/api/quit", {}); } catch { }
  document.body.innerHTML = '<div style="display:grid;place-items:center;height:100vh;font:600 20px Segoe UI;color:#cfd3f5;background:#0a0b14">The app has closed. You can close this tab.</div>';
};
function paintUpdate(r) {
  const st = $("#updState"), btn = $("#updNow");
  if (!st) return;
  if (r.error) { st.textContent = r.error; btn.hidden = true; return; }
  st.textContent = r.available ? `You have v${r.current}. Version ${r.latest} is ready.` : `You have v${r.current}. You are up to date (latest is v${r.latest}).`;
  btn.hidden = !r.available;
}
async function doUpdate(btn) {
  btn.disabled = true; const old = btn.textContent; btn.textContent = "Updating...";
  try {
    await api("/api/update/apply", {});
    toast("Updated. Restarting...", "good");
    const wait = setInterval(async () => { try { await api("/api/status"); clearInterval(wait); location.reload(); } catch { } }, 1500);
  } catch (e) { toast("Update failed: " + e.message, "bad"); btn.disabled = false; btn.textContent = old; }
}
$("#checkUpd").onclick = async () => {
  $("#updState").textContent = "Checking...";
  try { paintUpdate(await api("/api/update/check", {})); } catch (e) { $("#updState").textContent = "Could not check: " + e.message; }
  loadStatus();
};
$("#updNow").onclick = () => doUpdate($("#updNow"));
$("#updBtn").onclick = async () => {
  $("#updBtn").disabled = true; $("#updBtn").textContent = "Updating…";
  try {
    await api("/api/update/apply", {});
    toast("Updated. Restarting…", "good");
    const wait = setInterval(async () => { try { await api("/api/status"); clearInterval(wait); location.reload(); } catch { } }, 1500);
  } catch (e) { toast("Update failed: " + e.message, "bad"); $("#updBtn").disabled = false; $("#updBtn").textContent = "Update now"; }
};

/* ---------------- guide links ---------------- */
function goGuide(id) {
  $('nav a[data-page="guide"]').click();
  const el = document.getElementById(id);
  if (el) { el.open = true; setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 80); }
}
document.addEventListener("click", e => { const a = e.target.closest("[data-goto]"); if (a) { e.preventDefault(); e.stopPropagation(); goGuide(a.dataset.goto); } });
try { if (localStorage.getItem("hintX")) $("#startHint").hidden = true; } catch { }
$("#hintX").onclick = () => { $("#startHint").hidden = true; try { localStorage.setItem("hintX", "1"); } catch { } };

/* ---------------- publish ---------------- */
const PUB = ["brand", "ig_user_id", "ig_token", "fb_page_id", "fb_page_token", "github_repo", "github_token", "slots"];
const pubForm = { per_day: 8, days: 3 };
async function loadPublish() {
  const c = await api("/api/publish/config");
  PUB.forEach(k => { const el = $("#p_" + k); if (el) el.value = c[k] || ""; });
  const r = c.ready;
  $("#pubReady").innerHTML = ["instagram", "facebook", "hosting"].map(k => `<span class="tag" style="${r[k] ? "" : "background:rgba(255,92,138,.18);color:#ff9bb5"}">${k}: ${r[k] ? "ready" : "missing"}</span>`).join("");
}
$$("#page-publish .stepper").forEach(st => $$("button", st).forEach(b => b.onclick = () => {
  const v = Math.max(+st.dataset.min, Math.min(+st.dataset.max, pubForm[st.dataset.key] + (+b.dataset.d)));
  pubForm[st.dataset.key] = v; $("b", st).textContent = v;
}));
$("#pubSave").onclick = async () => {
  const body = {}; PUB.forEach(k => body[k] = $("#p_" + k).value.trim());
  await api("/api/publish/config", body); toast("Saved", "good"); loadPublish();
};
const table = (rows, cols) => rows.length ? `<div style="overflow:auto;max-height:340px;margin-top:14px"><table style="width:100%;border-collapse:collapse;font-size:13px">` +
  `<tr>${cols.map(c => `<th style="text-align:left;padding:6px 8px;color:var(--muted)">${c[1]}</th>`).join("")}</tr>` +
  rows.map(r => `<tr style="border-top:1px solid var(--line)">${cols.map(c => `<td style="padding:6px 8px">${esc(r[c[0]])}</td>`).join("")}</tr>`).join("") + `</table></div>` : `<p class="muted">Nothing to show yet.</p>`;
$("#pmGo").onclick = async () => {
  $("#pmOut").textContent = "Working...";
  try {
    const r = await fetch("/api/publish/permanent", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app_id: $("#pm_app_id").value, app_secret: $("#pm_app_secret").value, user_token: $("#pm_user_token").value }) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error);
    $("#pmOut").textContent = `Done: ${j.page} - token expires ${j.expires}`;
    ["pm_app_secret", "pm_user_token"].forEach(i => $("#" + i).value = "");
    toast("Facebook token saved", "good"); loadPublish();
  } catch (e) { $("#pmOut").textContent = ""; toast(e.message, "bad"); }
};
$("#pubPreview").onclick = async () => {
  try { const plan = await api("/api/publish/plan", pubForm); $("#pubTable").innerHTML = table(plan, [["n", "#"], ["time", "When"], ["type", "Type"], ["name", "Video"]]); }
  catch (e) { toast(e.message, "bad"); }
};
$("#pubRun").onclick = async () => {
  if (!confirm("This schedules public posts on your Facebook Page and uploads the videos for Instagram. Continue?")) return;
  try { await api("/api/publish/run", pubForm); toast("Publishing started - watch the queue on the Create page", "good"); poll(); }
  catch (e) { toast(e.message, "bad"); }
};
$("#pubVerify").onclick = async () => {
  const rows = await api("/api/publish/verify");
  $("#pubVerifyTable").innerHTML = table(rows, [["n", "#"], ["time", "When"], ["name", "Video"], ["facebook", "Facebook"], ["link", "Video link"]]);
};

/* ---------------- boot ---------------- */
(async function () {
  await loadStatus();
  S.catalog = await api("/api/catalog");
  poll(); loadLibrary();
  setInterval(loadStatus, 5 * 60 * 1000);
  // deep links: #library, #settings, #type=math  (used for the README screenshots)
  const h = location.hash.slice(1);
  if (h === "library" || h === "settings" || h === "publish" || h === "guide") $(`nav a[data-page=${h}]`).click();
  if (h.startsWith("type=")) openComposer(h.slice(5));
})();
