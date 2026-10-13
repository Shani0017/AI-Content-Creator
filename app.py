"""AI Content Creator - local web app. Run `start.bat` (or `python app.py`); the UI opens in your browser."""
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser

if os.name == "nt":                                   # child programs (ffmpeg, PowerShell) must never pop up a black window
    _Popen = subprocess.Popen

    class _NoWindow(_Popen):
        def __init__(self, *a, **k):
            k["creationflags"] = k.get("creationflags", 0) | 0x08000000
            super().__init__(*a, **k)

    subprocess.Popen = _NoWindow

from flask import Flask, Response, jsonify, request, send_from_directory

from forge import ROOT, VERSION, gens, jobs, llm, paths, publisher, settings, speech, updater, youtube

if sys.stdout is None or sys.stderr is None:          # started without a console (pythonw): write the output to a log file
    _log = open(paths.DATA / "app.log", "a", buffering=1, encoding="utf-8")
    sys.stdout = sys.stdout or _log
    sys.stderr = sys.stderr or _log

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
        "version": VERSION, "update": upd, "settings": st, "pid": os.getpid(),
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
    try:
        res = updater.apply()
    except Exception as e:                                   # show the real reason in the app instead of a bare "500 Internal Server Error"
        import traceback
        return jsonify({"error": f"Update failed: {str(e)[:300]}", "detail": traceback.format_exc()[-600:]}), 500
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


@app.post("/api/publish/permanent")
def pub_permanent():
    d = request.get_json(force=True) or {}
    try:
        return jsonify(publisher.make_permanent(d.get("app_id", "").strip(), d.get("app_secret", "").strip(), d.get("user_token", "").strip()))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get("/api/publish/verify")
def pub_verify():
    return jsonify(publisher.verify())


@app.get("/api/publish/vps.zip")
def pub_vps():
    return Response(publisher.vps_package(), mimetype="application/zip", headers={"Content-Disposition": "attachment; filename=vps-poster.zip"})


@app.get("/api/youtube/config")
def yt_config():
    return jsonify(youtube.public())


@app.post("/api/youtube/config")
def yt_save():
    d = request.get_json(force=True) or {}
    return jsonify(youtube.save_client(d.get("client_id", ""), d.get("client_secret", "")))


def _yt_redirect():
    return f"http://127.0.0.1:{PORT}/api/youtube/callback"


@app.get("/api/youtube/auth")
def yt_auth():
    try:
        return jsonify({"url": youtube.auth_url(_yt_redirect())})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get("/api/youtube/callback")
def yt_callback():
    code = request.args.get("code", "")
    try:
        if not code:
            raise RuntimeError(request.args.get("error", "No sign-in received."))
        name = youtube.finish_auth(code, _yt_redirect())
        msg = f"Signed in{' as ' + name if name else ''}. You can close this tab and go back to the app."
    except Exception as e:
        msg = "Sign-in failed: " + str(e)
    return Response(f"<body style='font:600 20px Segoe UI;background:#0a0b14;color:#cfd3f5;display:grid;place-items:center;height:100vh'><div>{msg}</div></body>", mimetype="text/html")


@app.post("/api/youtube/signout")
def yt_signout():
    youtube.sign_out()
    return jsonify(youtube.public())


@app.post("/api/youtube/plan")
def yt_plan():
    d = request.get_json(force=True) or {}
    try:
        return jsonify(youtube.preview(int(d.get("per_day", 8)), d.get("start", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/youtube/run")
def yt_run():
    d = request.get_json(force=True) or {}
    return jsonify(jobs.submit("youtube", {"per_day": d.get("per_day", 8), "start": d.get("start", "")}))


@app.post("/api/restart")
def restart_app():
    threading.Timer(0.5, updater.restart).start()
    return jsonify({"ok": True})


@app.post("/api/quit")
def quit_app():
    threading.Timer(0.6, lambda: os._exit(0)).start()
    return jsonify({"ok": True})


@app.post("/api/shortcut")
def make_shortcut():
    """desktop shortcut that starts the app without the black window"""
    vbs = ROOT / "start_hidden.vbs"
    ps = ("$ws = New-Object -ComObject WScript.Shell;"
          "$l = $ws.CreateShortcut([IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'AI Content Creator.lnk'));"
          f"$l.TargetPath = 'wscript.exe'; $l.Arguments = '\"{vbs}\"'; $l.WorkingDirectory = '{ROOT}'; $l.Save()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    return jsonify({"ok": True})


def _open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{PORT}")


if __name__ == "__main__":
    if os.environ.get("FORGE_WAIT_PORT") == "1":     # restarted by the updater: wait until the old copy let go of the port
        for _ in range(80):
            with socket.socket() as _s:
                if _s.connect_ex(("127.0.0.1", PORT)) != 0:
                    break
            time.sleep(0.25)
    else:
        with socket.socket() as _s:                   # already running? just open it in the browser
            if _s.connect_ex(("127.0.0.1", PORT)) == 0:
                if os.environ.get("FORGE_NO_BROWSER") != "1":
                    webbrowser.open(f"http://127.0.0.1:{PORT}")
                sys.exit(0)
    jobs.start()
    if os.environ.get("FORGE_NO_BROWSER") != "1":
        threading.Thread(target=_open_browser, daemon=True).start()
    print(f"AI Content Creator {VERSION} running at http://127.0.0.1:{PORT}  (close this window to stop)")
    app.run(host="127.0.0.1", port=PORT, threaded=True)
