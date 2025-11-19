# app.py
import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXT = {"mp4", "mov", "webm", "ogg", "mkv"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "no file part 'video'"}), 400
    f = request.files["video"]
    title = request.form.get("title", "")
    description = request.form.get("description", "")
    if f.filename == "":
        return jsonify({"error": "no selected file"}), 400
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        import time, json
        filename = f"{int(time.time())}_{filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(save_path)
        meta = {"filename": filename, "title": title, "description": description}
        with open(save_path + ".json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh)
        return jsonify({"ok": True, "url": f"/uploads/{filename}", "meta": meta}), 201
    return jsonify({"error": "file type not allowed"}), 400

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/videos")
def videos():
    items = []
    import json
    for fname in sorted(os.listdir(app.config["UPLOAD_FOLDER"]), reverse=True):
        if fname.endswith(".json"):
            continue
        fpath = os.path.join(app.config["UPLOAD_FOLDER"], fname)
        meta_path = fpath + ".json"
        meta = {"filename": fname, "title": "", "description": ""}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
            except:
                pass
        url = f"/uploads/{fname}"
        items.append({"url": url, "title": meta.get("title",""), "description": meta.get("description","")})
    return jsonify(items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
