# import os
# import re
# import json
# import mimetypes
# from urllib.parse import quote, urlencode

# from flask import Flask, request, jsonify, send_file, Response
# from flask_cors import CORS
# import yt_dlp

# app = Flask(__name__)
# CORS(app)

# def sanitize_filename(s: str) -> str:
#     """
#     Replace illegal filename characters with underscores and collapse whitespace.
#     """
#     # Replace any character that is not alphanumeric or space with underscore
#     sanitized = re.sub(r'[^a-zA-Z0-9 ]', '_', s)
#     # Collapse spaces to underscores
#     sanitized = re.sub(r'\s+', '_', sanitized.strip())
#     return sanitized

# @app.route('/', methods=['GET'])
# def index():
#     return 'API is running...'

# @app.route('/api/search', methods=['GET'])
# def search_videos():
#     """
#     Search YouTube for query terms and return a list of video metadata.
#     Query param: q (string)
#     """
#     query = request.args.get('q')
#     if not query:
#         return jsonify({'error': 'Search query is required'}), 400

#     try:
#         ydl_opts = {
#             'quiet': True,
#             'no_warnings': True,
#             'extract_flat': 'in_playlist',  # Do not download videos
#             'default_search': 'ytsearch10',  # Search for 10 videos
#             'skip_download': True,  # Skip downloading the video
#             'ignoreerrors': True,  # Skip videos that cause errors
#         }
        
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
#         results = []
#         if search_results and 'entries' in search_results:
#             for entry in search_results['entries']:
#                 if entry is None:
#                     continue
                
#                 # Ensure we have a valid ID
#                 video_id = entry.get('id')
#                 if not video_id:
#                     continue
                
#                 # Build the video URL
#                 video_url = f"https://www.youtube.com/watch?v={video_id}"
                
#                 # Get thumbnail URL (different formats available)
#                 thumbnail = None
#                 if entry.get('thumbnails'):
#                     # Try to get a medium-quality thumbnail
#                     for thumb in entry.get('thumbnails', []):
#                         if thumb.get('url'):
#                             thumbnail = thumb.get('url')
#                             break
                    
#                 # If no thumbnail found in thumbnails list, try the legacy field
#                 if not thumbnail:
#                     thumbnail = entry.get('thumbnail', '')
                
#                 results.append({
#                     'id': video_id,
#                     'title': entry.get('title', ''),
#                     'description': entry.get('description', ''),
#                     'thumbnail': thumbnail,
#                     'duration': entry.get('duration', 0),
#                     'url': video_url
#                 })
        
#         return jsonify({'results': results})
#     except Exception as e:
#         app.logger.error(f'Search error: {str(e)}')
#         return jsonify({'error': f'Failed to search videos: {str(e)}'}), 500

# @app.route('/api/video', methods=['GET'])
# def video_info():
#     """
#     Fetch YouTube video info given a URL, including available formats with direct download URLs.
#     Query param: url (string)
#     """
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'error': 'YouTube URL is required'}), 400

#     try:
#         ydl_opts = {
#             'quiet': True,
#             'no_warnings': True,
#             'skip_download': True,  # Don't download, just get info
#         }
        
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=False)
        
#         if not info:
#             return jsonify({'error': 'Could not fetch video information'}), 404
        
#         # Find best audio and video formats
#         best_audio = None
#         best_video = None
#         all_formats = []
        
#         for fmt in info.get('formats', []):
#             format_info = {
#                 'format_id': fmt.get('format_id', ''),
#                 'ext': fmt.get('ext', ''),
#                 'format': fmt.get('format', ''),
#                 'format_note': fmt.get('format_note', ''),
#                 'url': fmt.get('url', '')  # Include the direct URL
#             }
            
#             # Add filesize if available
#             if fmt.get('filesize') is not None:
#                 format_info['filesize'] = fmt.get('filesize')
                
#             # Add codec info if available
#             format_info['acodec'] = fmt.get('acodec', 'none')
#             format_info['vcodec'] = fmt.get('vcodec', 'none')
            
#             # Add resolution if present
#             if fmt.get('width') and fmt.get('height'):
#                 format_info['resolution'] = f"{fmt.get('width')}x{fmt.get('height')}"
#                 format_info['height'] = fmt.get('height')  # Store for comparison
            
#             # Check if this is a video+audio format
#             if fmt.get('acodec') != 'none' and fmt.get('vcodec') != 'none':
#                 if not best_video:
#                     best_video = fmt
#                 elif fmt.get('height') and best_video.get('height'):
#                     if fmt.get('height', 0) > best_video.get('height', 0):
#                         best_video = fmt
            
#             # Add aspect ratio if available
#             if fmt.get('aspect_ratio'):
#                 format_info['aspect_ratio'] = fmt.get('aspect_ratio')
#             # Check if this is audio only
#             if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
#                 if not best_audio:
#                     best_audio = fmt
#                 elif fmt.get('tbr') and best_audio.get('tbr'):
#                     if fmt.get('tbr', 0) > best_audio.get('tbr', 0):
#                         best_audio = fmt
            
#             all_formats.append(format_info)
        
#         # Format the best_audio and best_video to include only relevant info
#         best_audio_data = None
#         if best_audio:
#             best_audio_data = {
#                 'format_id': best_audio.get('format_id', ''),
#                 'ext': best_audio.get('ext', ''),
#                 'format': best_audio.get('format', ''),
#                 'acodec': best_audio.get('acodec', 'none'),
#                 'url': best_audio.get('url', '')  # Include direct URL
#             }
#             if best_audio.get('filesize') is not None:
#                 best_audio_data['filesize'] = best_audio.get('filesize')
        
#         best_video_data = None
#         if best_video:
#             best_video_data = {
#                 'format_id': best_video.get('format_id', ''),
#                 'ext': best_video.get('ext', ''),
#                 'format': best_video.get('format', ''),
#                 'vcodec': best_video.get('vcodec', ''),
#                 'acodec': best_video.get('acodec', ''),
#                 'url': best_video.get('url', '')  # Include direct URL
#             }
#             if best_video.get('width') and best_video.get('height'):
#                 best_video_data['resolution'] = f"{best_video.get('width')}x{best_video.get('height')}"
#             if best_video.get('filesize') is not None:
#                 best_video_data['filesize'] = best_video.get('filesize')
        
#         # Get thumbnail URL (multiple formats may be available)
#         thumbnail = None
#         if info.get('thumbnails'):
#             for thumb in info.get('thumbnails', []):
#                 if thumb.get('url'):
#                     thumbnail = thumb.get('url')
#                     break
        
#         # If no thumbnail in thumbnails list, fall back to legacy field
#         if not thumbnail:
#             thumbnail = info.get('thumbnail', '')
        
#         # Prepare response data
#         data = {
#             'id': info.get('id', ''),
#             'title': info.get('title', ''),
#             'thumbnail': thumbnail,
#             'duration': info.get('duration', 0),
#             'description': info.get('description', ''),
#             'url': info.get('webpage_url', url),  # Return the original URL if webpage_url not available
#             'embed_url': f"https://www.youtube.com/embed/{info.get('id', '')}",
#             'best_audio': best_audio_data,
#             'best_video': best_video_data,
#             'all_formats': all_formats
#         }
        
#         return jsonify(data)
#     except Exception as e:
#         app.logger.error(f'Video info error: {str(e)}')
#         return jsonify({'error': f'Failed to get video information: {str(e)}'}), 500

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 4000))
#     print(f"Starting server on port {port}...")
#     app.run(host='0.0.0.0', port=port, debug=True)



#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import yt_dlp
import os
import configparser
import subprocess  # Für die Überprüfung von ffmpeg
import ctypes  # Für die Überprüfung von Systembibliotheken
import re  # Für die URL-Validierung

class YTDLP_GUI:
    CONFIG_FILE = "settings.ini"

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube-Downloader GUI © 2025 by TK")  # Fenstertitel angepasst
        self.root.geometry("500x600")  # Fenstergröße vergrößert

        # Überprüfe Abhängigkeiten
        self.check_dependencies()

        self.config = configparser.ConfigParser()
        self.load_settings()

        # Plattformauswahl nach oben verschoben
        tk.Label(root, text="Plattform auswählen:").pack(pady=5)
        self.platform_combo = ttk.Combobox(root, values=["YouTube", "Vimeo", "Dailymotion", "SoundCloud", "TikTok", "Twitter"])
        self.platform_combo.current(self.platform_index)  # Geladene Einstellung
        self.platform_combo.pack(pady=5)

        # URL-Eingabe als nächstes
        tk.Label(root, text="URL eingeben:").pack(pady=10)  # Beschriftung angepasst
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        tk.Label(root, text="").pack(pady=5)  # Freie Zeile

        # Kontextmenü für die URL-Eingabe
        self.url_entry_menu = tk.Menu(self.url_entry, tearoff=0)
        self.url_entry_menu.add_command(label="Einfügen", command=self.paste_url)
        self.url_entry.bind("<Button-3>", self.show_url_entry_menu)

        tk.Button(root, text="Zielordner auswählen", command=self.select_download_folder).pack(pady=5)
        self.download_folder_label = tk.Label(root, text=f"Zielordner: {self.download_folder}", wraplength=480, anchor="w", justify="left")
        self.download_folder_label.pack(pady=5)

        tk.Label(root, text="").pack(pady=5)  # Freie Zeile

        tk.Button(root, text="Video als MP4 herunterladen", command=self.download_video).pack(pady=5)
        tk.Label(root, text="Video-Qualität auswählen:").pack(pady=5)
        self.quality_combo_video = ttk.Combobox(root, values=["Beste Qualität", "Mittlere Qualität", "Niedrigste Qualität"])
        self.quality_combo_video.current(self.video_quality_index)  # Geladene Einstellung
        self.quality_combo_video.pack(pady=5)

        tk.Label(root, text="").pack(pady=5)  # Leerzeile

        tk.Button(root, text="Audio als MP3 herunterladen", command=self.download_audio).pack(pady=5)
        tk.Label(root, text="Audio-Qualität auswählen:").pack(pady=5)
        self.quality_combo_audio = ttk.Combobox(
            root,
            values=["320 kbps", "256 kbps", "192 kbps", "128 kbps", "64 kbps", "32 kbps"]
        )
        self.quality_combo_audio.current(self.audio_quality_index)  # Geladene Einstellung
        self.quality_combo_audio.pack(pady=5)

        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_dependencies(self):
        missing_dependencies = []

        # Überprüfe ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except FileNotFoundError:
            missing_dependencies.append("ffmpeg (Installiere es mit: sudo apt install ffmpeg)")

        # Überprüfe tkinter
        try:
            import tkinter
        except ImportError:
            missing_dependencies.append("tkinter (Installiere es mit: sudo apt install python3-tk)")

        # Überprüfe Systembibliotheken (libx11, libxext, libxrender)
        for lib in ["libX11.so.6", "libXext.so.6", "libXrender.so.1"]:
            if not self.check_library(lib):
                missing_dependencies.append(f"{lib} (Installiere es mit: sudo apt install libx11-6 libxext6 libxrender1)")

        # Zeige Fehlermeldung, falls Abhängigkeiten fehlen
        if missing_dependencies:
            messagebox.showerror(
                "Fehlende Abhängigkeiten",
                "Die folgenden Abhängigkeiten fehlen:\n\n" + "\n".join(missing_dependencies)
            )
            self.root.destroy()  # Beende das Programm, wenn Abhängigkeiten fehlen

    def check_library(self, library_name):
        try:
            ctypes.CDLL(library_name)
            return True
        except OSError:
            return False

    def load_settings(self):
        if os.path.exists(self.CONFIG_FILE):
            self.config.read(self.CONFIG_FILE)
            self.video_quality_index = int(self.config.get("Settings", "video_quality", fallback="0"))
            self.audio_quality_index = int(self.config.get("Settings", "audio_quality", fallback="0"))
            self.platform_index = int(self.config.get("Settings", "platform", fallback="0"))
            self.download_folder = self.config.get("Settings", "download_folder", fallback=os.getcwd())
        else:
            self.video_quality_index = 0  # Standard: Beste Qualität
            self.audio_quality_index = 0  # Standard: 192 kbps
            self.platform_index = 0  # Standard: YouTube
            self.download_folder = os.getcwd()

    def save_settings(self):
        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")
        self.config.set("Settings", "video_quality", str(self.quality_combo_video.current()))
        self.config.set("Settings", "audio_quality", str(self.quality_combo_audio.current()))
        self.config.set("Settings", "platform", str(self.platform_combo.current()))
        self.config.set("Settings", "download_folder", self.download_folder)
        with open(self.CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def select_download_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_folder, title="Zielordner auswählen")
        if folder:
            self.download_folder = folder
            self.download_folder_label.config(text=f"Zielordner: {self.download_folder}")
            messagebox.showinfo("Zielordner", f"Zielordner gesetzt auf: {self.download_folder}")

    def on_close(self):
        self.save_settings()
        self.root.destroy()

    def is_valid_url(self, url):
        regex = re.compile(
            r'^(https?://)?(www\.)?([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}(/.*)?$'
        )
        return re.match(regex, url) is not None

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url or not self.is_valid_url(url):
            messagebox.showerror("Fehler", "Bitte eine gültige URL eingeben.")
            return
        quality = self.quality_combo_video.get()
        self.download_media(url, 'mp4', quality)

    def download_audio(self):
        url = self.url_entry.get().strip()
        if not url or not self.is_valid_url(url):
            messagebox.showerror("Fehler", "Bitte eine gültige URL eingeben.")
            return
        quality = self.quality_combo_audio.get()
        self.download_media(url, 'mp3', quality)

    def download_media(self, url, format_type, quality):
        platform = self.platform_combo.get()
        ydl_opts = {
            'outtmpl': os.path.join(self.download_folder, '%(playlist_index)s - %(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
            'no_color': True
        }

        if format_type == 'mp3':
            audio_quality = '192'  # Standardwert
            if quality == "320 kbps":
                audio_quality = '320'
            elif quality == "256 kbps":
                audio_quality = '256'
            elif quality == "128 kbps":
                audio_quality = '128'
            elif quality == "64 kbps":
                audio_quality = '64'
            elif quality == "32 kbps":
                audio_quality = '32'

            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality,
                }]
            })
        elif format_type == 'mp4':
            if quality == "Beste Qualität":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif quality == "Mittlere Qualität":
                ydl_opts['format'] = 'best[height<=480]+bestaudio/best'
            elif quality == "Niedrigste Qualität":
                ydl_opts['format'] = 'worstvideo+worstaudio/worst'

        # Plattform-spezifische Verarbeitung
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if platform in ["YouTube", "Vimeo", "Dailymotion", "SoundCloud", "TikTok", "Twitter"]:
                    info = ydl.extract_info(url, download=False)  # Playlist-Info abrufen
                    if 'entries' in info:  # Playlist erkannt
                        for entry in info['entries']:
                            video_url = entry['webpage_url']
                            ydl.download([video_url])
                    else:  # Einzelnes Video
                        ydl.download([url])
                else:
                    messagebox.showerror("Fehler", f"Plattform '{platform}' wird nicht unterstützt.")
            messagebox.showinfo("Erfolg", f"Download als {format_type.upper()} abgeschlossen!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Download fehlgeschlagen: {e}")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes > 0:
                    percent = (downloaded_bytes / total_bytes) * 100
                    if int(percent) % 5 == 0:  # Fortschritt nur alle 5% aktualisieren
                        self.progress['value'] = percent
                        self.progress.update_idletasks()
            except Exception:
                pass

    def paste_url(self):
        try:
            self.url_entry.insert(tk.INSERT, self.root.clipboard_get())
        except tk.TclError:
            pass  # Falls die Zwischenablage leer ist, nichts tun

    def show_url_entry_menu(self, event):
        self.url_entry_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    root = tk.Tk()
    app = YTDLP_GUI(root)
    root.mainloop()

