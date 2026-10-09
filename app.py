"""AI Content Creator - local web app. Run `start.bat` (or `python app.py`); the UI opens in your browser."""
import os
import subprocess
import sys
import threading
import time
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

from forge import ROOT, VERSION, gens, jobs, llm, paths, settings, speech, updater

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


def _open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{PORT}")


if __name__ == "__main__":
    jobs.start()
    if os.environ.get("FORGE_NO_BROWSER") != "1":
        threading.Thread(target=_open_browser, daemon=True).start()
    print(f"AI Content Creator {VERSION} running at http://127.0.0.1:{PORT}  (close this window to stop)")
    app.run(host="127.0.0.1", port=PORT, threaded=True)
