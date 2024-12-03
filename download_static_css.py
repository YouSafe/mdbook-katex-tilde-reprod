#!/usr/bin/env python
# Python 3.5 or above required.
import re
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

THEME_PATH = "theme/"
CDN_ROOT = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/"
KATEX_CSS_PATH = "katex.min.css"
COPY_TEX_JS_PATH = "contrib/copy-tex.min.js"

def write_file_bytes(filename, bytes):
    # Create parent directories.
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as file:
        file.write(bytes)

def download_bytes(url):
    request = requests.get(url)
    if request.status_code != 200:
        raise Exception("Failed to download from " + url)
    file_bytes = request.content
    return file_bytes

def font_urls_in_css(css):
    return re.findall(r"url\((fonts\/[^()]+)\)", css)

def download_save(url_base, path, path_base):
    url = url_base + path
    file_path = path_base + path
    print("Downloading from " + url + " to " + file_path)
    file_bytes = download_bytes(url)
    write_file_bytes(file_path, file_bytes)
    return file_bytes

def main():
    css_bytes = download_save(CDN_ROOT, KATEX_CSS_PATH, "")
    css_str = css_bytes.decode(encoding="utf-8")
    font_urls = font_urls_in_css(css_str)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_save, CDN_ROOT, url, THEME_PATH) for url in font_urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error downloading font: {e}")

    download_save(CDN_ROOT, COPY_TEX_JS_PATH, "")

if __name__ == "__main__":
    main()