"""AI Content Creator - local web app. Run `start.bat` (or `python app.py`); the UI opens in your browser."""
import os
import subprocess
import sys
import threading
import time
import webbrowser

from flask import Flask, Response, jsonify, request, send_from_directory

from forge import ROOT, VERSION, gens, jobs, llm, paths, publisher, settings, speech, updater

PORT = int(os.environ.get("FORGE_PORT", "8765"))
app = Flask(__name__, static_folder=str(ROOT / "ui"), static_url_path="/ui")


@app.get("/")
def index():
    return send_from_directory(ROOT / "ui", "index.html")


@app.get("/api/status")
def status():
    st = settings.load()
    ol = llm.status()
    upd = updater.check() if st.get("auto_update_check") else {"available": False, "current": VERSION}
    return jsonify({
        "version": VERSION, "update": upd, "settings": st,
        "tools": {"ffmpeg": os.path.exists(paths.FFMPEG) or bool(paths.FFMPEG), "voice": speech.models_ready()["tts"], "ollama": ol},
    })


@app.get("/api/catalog")
def catalog():
    return jsonify(gens.catalog())


@app.post("/api/settings")
def save_settings():
    return jsonify(settings.save(request.get_json(force=True) or {}))


@app.post("/api/jobs")
def submit():
    d = request.get_json(force=True)
    return jsonify(jobs.submit(d["kind"], d.get("params") or {}))


@app.get("/api/jobs")
def list_jobs():
    return jsonify(jobs.listing())


@app.get("/api/jobs/<jid>")
def one_job(jid):
    j = jobs.JOBS.get(jid)
    return (jsonify(j), 200) if j else (jsonify({"error": "not found"}), 404)


@app.get("/api/library")
def library():
    return jsonify(jobs.library())


@app.get("/media/<path:rel>")
def media(rel):
    return send_from_directory(paths.OUTPUT, rel, conditional=True)


@app.post("/api/open-folder")
def open_folder():
    if sys.platform.startswith("win"):
        os.startfile(str(paths.OUTPUT))
    return jsonify({"ok": True})


@app.post("/api/update/check")
def update_check():
    return jsonify(updater.check(force=True))


@app.post("/api/update/apply")
def update_apply():
    res = updater.apply()
    threading.Timer(0.8, updater.restart).start()
    return jsonify(res)


@app.get("/api/publish/config")
def pub_config():
    return jsonify(publisher.public())


@app.post("/api/publish/config")
def pub_save():
    return jsonify(publisher.save(request.get_json(force=True) or {}))


@app.post("/api/publish/plan")
def pub_plan():
    d = request.get_json(force=True) or {}
    plan = publisher.build_plan(int(d.get("per_day", 8)), int(d.get("days", 3)), d.get("start", ""))
    return jsonify([{k: r[k] for k in ("n", "time", "type", "name", "caption")} for r in plan])


@app.post("/api/publish/run")
def pub_run():
    d = request.get_json(force=True) or {}
    return jsonify(jobs.submit("publish", {"per_day": d.get("per_day", 8), "days": d.get("days", 3), "start": d.get("start", "")}))


@app.get("/api/publish/verify")
def pub_verify():
    return jsonify(publisher.verify())


@app.get("/api/publish/vps.zip")
def pub_vps():
    return Response(publisher.vps_package(), mimetype="application/zip", headers={"Content-Disposition": "attachment; filename=vps-poster.zip"})


def _open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{PORT}")


if __name__ == "__main__":
    jobs.start()
    if os.environ.get("FORGE_NO_BROWSER") != "1":
        threading.Thread(target=_open_browser, daemon=True).start()
    print(f"AI Content Creator {VERSION} running at http://127.0.0.1:{PORT}  (close this window to stop)")
    app.run(host="127.0.0.1", port=PORT, threaded=True)
