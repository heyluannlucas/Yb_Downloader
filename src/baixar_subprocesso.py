import subprocess
import re
import os
import requests
import zipfile
import tempfile
import shutil
import glob
import platform

def garantir_ffmpeg_portatil():
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
                    final_path = os.path.join(tools_dir, "ffmpeg.exe")
                    shutil.move(extracted_path, final_path)
                    break

        os.environ["PATH"] += os.pathsep + tools_dir

    else:
        # Linux/Mac -> ffmpeg já deve estar instalado
        pass

    # Se ffmpeg já está disponível, beleza
    if shutil.which("ffmpeg"):
        return

    # Detectar o sistema
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
                    final_path = os.path.join(tools_dir, "ffmpeg.exe")
                    shutil.move(extracted_path, final_path)
                    break

        os.environ["PATH"] += os.pathsep + tools_dir

    else:
        pass
    if shutil.which("ffmpeg"):
        return

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
                final_path = os.path.join(tools_dir, "ffmpeg.exe")
                shutil.move(extracted_path, final_path)
                break

    os.environ["PATH"] += os.pathsep + tools_dir

def obter_qualidades(link):
    comando = ["yt-dlp", "--no-check-certificate", "--force-ipv4", "-F", link]

    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    qualidades = {"video": [], "audio": []}
    capturar = False

    for linha in processo.stdout:
        linha = linha.strip()
        print(f"DEBUG: {linha}")
        if linha.startswith("ID") and "RESOLUTION" in linha:
            capturar = True
            continue
        if capturar:
            if linha == "":
                break
            partes = linha.split()
            if len(partes) >= 3:
                format_id = partes[0]
                extension = partes[1]
                resolution = partes[2]
                if resolution.lower() == "audio" or "audio" in resolution.lower():
                    qualidades["audio"].append((format_id, resolution, extension))
                else:
                    qualidades["video"].append((format_id, resolution, extension))

    processo.wait()
    print(f"DEBUG: Qualidades encontradas: {qualidades}")
    return qualidades

def baixar_video_com_progresso(link, qualidade="720", tipo_download="video", pasta_destino="downloads", video_id=None, audio_id=None):
    garantir_ffmpeg_portatil()
    os.makedirs(pasta_destino, exist_ok=True)

    output_template = os.path.join(pasta_destino, "%(title)s.%(ext)s")
    comando = ["yt-dlp", "--no-check-certificate", "--force-ipv4"]

    if tipo_download == "video" and video_id:
        comando += [
            "-f", f"{video_id}+bestaudio[ext=m4a]/bestaudio",
            "--merge-output-format", "mp4",
            "-o", output_template,
            link
        ]
    elif tipo_download == "audio" and audio_id:
        comando += [
            "-f", f"{audio_id}/bestaudio[ext=m4a]/bestaudio",
            "-o", output_template,
            link,
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K"
        ]
    else:
        comando += [
            "-f",
            f"bestaudio[ext=m4a]/bestaudio" if tipo_download == "audio" else f"bestvideo[height<={qualidade}]+bestaudio[ext=m4a]/bestaudio",
            "--merge-output-format", "mp4" if tipo_download == "video" else "",
            "-o", output_template,
            link
        ]

    comando = [x for x in comando if x != ""]  

    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    progresso_atual = 0

    for linha in processo.stdout:
        match = re.search(r"\[download\]\s+(\d{1,3}\.\d)%", linha)
        if match:
            progresso_atual = float(match.group(1))
            yield progresso_atual

    processo.wait()

    yield 100.0
