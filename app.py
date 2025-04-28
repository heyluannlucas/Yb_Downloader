import os
import streamlit as st
import yt_dlp
import time
from src.baixar_subprocesso import baixar_video_com_progresso, obter_qualidades

@st.cache_data(show_spinner="🎥 Carregando informações...")
def pegar_info_video(link):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            titulo = info.get('title', 'Título desconhecido')
            thumb = info.get('thumbnail', None)
            return thumb, titulo
    except Exception:
        if "v=" in link:
            video_id = link.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in link:
            video_id = link.split("youtu.be/")[-1].split("?")[0]
        else:
            return None, "Título desconhecido"
        thumb = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return thumb, "Título não encontrado"

@st.cache_data(show_spinner="🔎 Buscando qualidades...")
def obter_qualidades_cacheado(link):
    return obter_qualidades(link)

def limpar_downloads():
    for arquivo in os.listdir("downloads"):
        caminho = os.path.join("downloads", arquivo)
        if arquivo.endswith((".mp4", ".mp3")) and os.path.isfile(caminho):
            os.remove(caminho)

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

def main():
    st.set_page_config(page_title="YouTube Downloader", layout="centered", initial_sidebar_state="expanded")

    aplicar_tema()

    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Limpar Downloads"):
        limpar_downloads()
        st.sidebar.success("Arquivos de download limpos!")

    st.title("🔵 YouTube Downloader")

    link = st.text_input("📌 Cole o link do vídeo ou playlist:")

    if link:
        thumb_url, titulo = pegar_info_video(link)

        st.markdown(f"### 🎵 {titulo}")
        if thumb_url:
            st.video(link)

        qualidades = obter_qualidades_cacheado(link)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            tipo_download = st.radio(
                "🎮 Escolha o tipo:",
                ("🎥 Vídeo (MP4)", "🎵 Áudio (MP3)")
            )

        with col2:
            video_id = None
            audio_id = None
            if tipo_download.startswith("🎥") and qualidades["video"]:
                video_opcoes = [f"{q[1]} - {q[2]}" for q in qualidades["video"]]
                video_opcoes_ids = [q[0] for q in qualidades["video"]]
                video_qualidade = st.selectbox("✨ Qualidade de Vídeo:", video_opcoes)
                video_id = video_opcoes_ids[video_opcoes.index(video_qualidade)]
            elif tipo_download.startswith("🎵") and qualidades["audio"]:
                audio_opcoes = [f"{q[1]} - {q[2]}" for q in qualidades["audio"]]
                audio_opcoes_ids = [q[0] for q in qualidades["audio"]]
                audio_qualidade = st.selectbox("🎶 Qualidade de Áudio:", audio_opcoes)
                audio_id = audio_opcoes_ids[audio_opcoes.index(audio_qualidade)]
            else:
                st.warning("⚠️ Qualidade não disponível.")

        st.markdown("---")

        if st.button("🚀 Iniciar Download", use_container_width=True):
            tipo = "video" if tipo_download.startswith("🎥") else "audio"
            barra = st.progress(0)
            status_texto = st.empty()

            with st.spinner("⏳ Baixando..."):
                try:
                    for progresso in baixar_video_com_progresso(link, tipo_download=tipo, video_id=video_id, audio_id=audio_id):
                        barra.progress(int(progresso))
                        status_texto.text(f"Progresso: {progresso:.2f}% 🎵")

                    barra.progress(100)
                    status_texto.text("✅ Download Finalizado!")

                    st.balloons()

                    st.success("✅ Seus arquivos estão prontos:")
                    arquivos = os.listdir("downloads")
                    for arquivo in arquivos:
                        if arquivo.endswith((".mp4", ".mp3")):
                            caminho = os.path.join("downloads", arquivo)
                            with open(caminho, "rb") as file:
                                download = st.download_button(
                                    label=f"🔽️ Baixar {arquivo}",
                                    data=file,
                                    file_name=arquivo,
                                    mime="video/mp4" if arquivo.endswith(".mp4") else "audio/mpeg",
                                    use_container_width=True
                                )
                            if download:
                                st.success(f"✅ '{arquivo}' download iniciado! Limpando arquivo...")
                                time.sleep(5)
                                if os.path.exists(caminho):
                                    os.remove(caminho)
                                    st.info(f"🗑️ '{arquivo}' removido do servidor!")

                except Exception as e:
                    st.error(f"🚫 Erro no download: {e}")

if __name__ == "__main__":
    main()
