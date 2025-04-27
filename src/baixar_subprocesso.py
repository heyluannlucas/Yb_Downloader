import os
import platform
import shutil
import tempfile
import requests
import zipfile
from yt_dlp import YoutubeDL

def garantir_ffmpeg_portatil():
    """Garante que o ffmpeg esteja disponível no PATH."""
    if shutil.which("ffmpeg"):
        return

    sistema = platform.system()
    if sistema == "Windows":
        tools_dir = os.path.join(os.getcwd(), "tools")
        os.makedirs(tools_dir, exist_ok=True)
        ffmpeg_exe = os.path.join(tools_dir, "ffmpeg.exe")

        if os.path.exists(ffmpeg_exe):
            os.environ["PATH"] += os.pathsep + tools_dir
            return

        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        temp_zip = os.path.join(tempfile.gettempdir(), "ffmpeg.zip")

        with requests.get(url, stream=True) as r:
            with open(temp_zip, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe"):
                    zip_ref.extract(member, tools_dir)
                    extracted_path = os.path.join(tools_dir, member)
                    shutil.move(extracted_path, ffmpeg_exe)
                    break

        os.environ["PATH"] += os.pathsep + tools_dir

def obter_qualidades(link):
    """Lista TODAS qualidades disponíveis do vídeo."""
    qualidades = {"video": [], "audio": []}
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)

    for f in info.get('formats', []):
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
            # Somente vídeo (sem áudio)
            qualidades["video"].append({
                "format_id": f['format_id'],
                "format": f"{f['ext']} - {f.get('format_note') or f.get('height', '?')}p - {f.get('fps', '?')}fps",
                "resolution": f.get('resolution') or f.get('height'),
            })
        elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
            # Somente áudio
            qualidades["audio"].append({
                "format_id": f['format_id'],
                "format": f"{f['ext']} - {f.get('abr', '??')}kbps",
            })
    return qualidades

def baixar_video_com_progresso(link, tipo_download, format_id):
    """Baixa o vídeo ou áudio mostrando progresso."""
    garantir_ffmpeg_portatil()
    pasta_destino = "downloads"
    os.makedirs(pasta_destino, exist_ok=True)

    output_template = os.path.join(pasta_destino, "%(title)s.%(ext)s")

    progresso_hook = []

    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            downloaded = d.get('downloaded_bytes', 0)
            progresso = downloaded / total * 100
            progresso_hook.append(progresso)
        elif d['status'] == 'finished':
            progresso_hook.append(100.0)

    ydl_opts = {
        'format': format_id,
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [hook],
    }

    if tipo_download == "audio":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    for p in progresso_hook:
        yield p
