import shutil
import os
import requests
import zipfile
import tempfile

def ffmpeg_disponivel():
    return shutil.which("ffmpeg") is not None

def instalar_ffmpeg_temporario():
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "ffmpeg.zip")

    with requests.get(url, stream=True) as r:
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file == "ffmpeg.exe":
                os.environ["PATH"] += os.pathsep + root
                return True
    return False
