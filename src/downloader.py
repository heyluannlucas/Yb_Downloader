import yt_dlp
import os
from src.ffmpeg_helper import ffmpeg_disponivel
from src.settings import DOWNLOAD_DIR
from src.utils import update_hook_progress, get_download_progress

def extrair_info(link):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(link, download=False)

def baixar_video(link, qualidade, tipo_download="video", playlist=False):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': not playlist,
        'progress_hooks': [update_hook_progress],
        'quiet': True,
    }

    if tipo_download == "video":
        if ffmpeg_disponivel():
            ydl_opts['format'] = f'bestvideo[height<={qualidade}]+bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        else:
            ydl_opts['format'] = f'best[ext=mp4][height<={qualidade}]'
    elif tipo_download == "audio":
        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'mp3', 
            'preferredquality': '192'
        }]

    caminhos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        infos = ydl.extract_info(link, download=True)
        if playlist and 'entries' in infos:
            for video in infos['entries']:
                caminhos.append(ydl.prepare_filename(video))
        else:
            caminhos.append(ydl.prepare_filename(infos))

    return caminhos

def get_progress():
    return get_download_progress()
