import os
import streamlit as st
from src.baixar_subprocesso import baixar_video_com_progresso, obter_qualidades, garantir_ffmpeg_portatil
import time

# Criar pastas necessárias
DOWNLOAD_DIR = "downloads"
TOOLS_DIR = "tools"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TOOLS_DIR, exist_ok=True)

# Tema bonito
def aplicar_tema():
    st.markdown("""
    <style>
    body, .stApp {
        font-family: 'Helvetica Neue', sans-serif;
    }
    div[data-baseweb="select"] * {
        color: white !important;
    }
    div[data-baseweb="menu"] * {
        color: white !important;
    }
    div[data-baseweb="option"] * {
        color: white !important;
    }
    .stButton>button {
        background-color: #0078D4;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #005A9E;
    }
    .stProgress > div > div > div > div {
        background-color: #0078D4;
        transition: width 0.5s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# Baixar info do vídeo
@st.cache_data(show_spinner="Carregando informações...")
def pegar_info_video(link):
    from yt_dlp import YoutubeDL
    try:
        ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get("title", "Título desconhecido"), info.get("thumbnail")
    except:
        return "Título desconhecido", None

# Limpar pasta downloads
def limpar_downloads():
    for arquivo in os.listdir(DOWNLOAD_DIR):
        caminho = os.path.join(DOWNLOAD_DIR, arquivo)
        if arquivo.endswith((".mp4", ".mp3")):
            os.remove(caminho)

# App principal
def main():
    st.set_page_config(page_title="YouTube Downloader", layout="centered")

    aplicar_tema()

    st.sidebar.header("Opções")
    if st.sidebar.button("🗑️ Limpar Downloads"):
        limpar_downloads()
        st.sidebar.success("Downloads limpos!")

    st.title("🔵 YouTube Downloader")

    link = st.text_input("📎 Link do vídeo ou playlist:")

    if link:
        titulo, thumb_url = pegar_info_video(link)

        st.subheader(f"🎵 {titulo}")
        if thumb_url:
            st.image(thumb_url)
        else:
            st.video(link)

        qualidades = obter_qualidades(link)

        tipo_download = st.radio("Tipo de Download:", ["🎥 Vídeo (MP4)", "🎵 Áudio (MP3)"])

        if tipo_download.startswith("🎥"):
            opcoes = [f"{q['format']} - {q['resolution']}" for q in qualidades['video']]
            escolha = st.selectbox("Qualidade do Vídeo:", opcoes)
            escolha_id = qualidades['video'][opcoes.index(escolha)]['format_id']
        else:
            opcoes = [f"{q['format']}" for q in qualidades['audio']]
            escolha = st.selectbox("Qualidade do Áudio:", opcoes)
            escolha_id = qualidades['audio'][opcoes.index(escolha)]['format_id']

        if st.button("🚀 Iniciar Download"):
            garantir_ffmpeg_portatil()
            barra = st.progress(0)
            status_texto = st.empty()

            tipo = "video" if tipo_download.startswith("🎥") else "audio"

            with st.spinner("Baixando..."):
                try:
                    for progresso in baixar_video_com_progresso(link, tipo, escolha_id):
                        barra.progress(int(progresso))
                        status_texto.text(f"Progresso: {progresso:.2f}% 🎵")

                    barra.progress(100)
                    st.balloons()
                    st.success("✅ Download completo!")

                    for arquivo in os.listdir(DOWNLOAD_DIR):
                        caminho = os.path.join(DOWNLOAD_DIR, arquivo)
                        if arquivo.endswith((".mp4", ".mp3")):
                            with open(caminho, "rb") as f:
                                st.download_button(f"🔽 Baixar {arquivo}", f, arquivo)
                except Exception as e:
                    st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()
