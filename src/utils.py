_progress = 0

def update_hook_progress(d):
    global _progress
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', 1)
        _progress = int(downloaded * 100 / total)

def get_download_progress():
    return _progress
