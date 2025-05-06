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


import os
import re
import json
import mimetypes
import requests
from urllib.parse import quote, urlencode

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from pytubefix import Search, YouTube
from pytubefix.helpers import reset_cache
from io import BytesIO

# Optional: clear any stale PoToken cache at startup
# reset_cache()

app = Flask(__name__)
CORS(app)

def sanitize_filename(s: str) -> str:
    """
    Replace illegal filename characters with underscores and collapse whitespace.
    """
    sanitized = re.sub(r'[^a-zA-Z0-9 ]', '_', s)
    sanitized = re.sub(r'\s+', '_', sanitized.strip())
    return sanitized

@app.route('/', methods=['GET'])
def index():
    return 'API is running...'

@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        search_results = Search(query).results
        results = []
        for video in search_results[:10]:
            try:
                vid_id = video.video_id
                results.append({
                    'id': vid_id,
                    'title': video.title,
                    'description': video.description,
                    'thumbnail': f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                    'duration': video.length,
                    'url': f"https://www.youtube.com/watch?v={vid_id}"
                })
            except Exception as e:
                app.logger.warning(f"Error processing search result: {e}")
        return jsonify({'results': results})
    except Exception as e:
        app.logger.error(f'Search error: {e}')
        return jsonify({'error': f'Failed to search videos: {e}'}), 500

@app.route('/api/video', methods=['GET'])
def video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        # Enable PoToken to bypass bot detection
        yt = YouTube(url, use_po_token=True)

        streams = yt.streams
        best_audio = streams.get_audio_only()
        best_video = streams.get_highest_resolution()

        all_formats = []
        for stream in streams.all():
            info = {
                'format_id': str(stream.itag),
                'ext': stream.subtype,
                'format': f"{stream.type} - {stream.subtype} ({stream.resolution or 'audio only'})",
                'url': stream.url,
                'acodec': 'none' if not stream.includes_audio_track else stream.audio_codec,
                'vcodec': 'none' if not stream.includes_video_track else stream.video_codec
            }
            if stream.resolution:
                info.update({
                    'resolution': stream.resolution,
                    'height': int(stream.resolution.rstrip('p'))
                })
            try:
                info['filesize'] = stream.filesize
            except:
                pass
            all_formats.append(info)

        def format_data(stream_obj, is_audio=False):
            data = {
                'format_id': str(stream_obj.itag),
                'ext': stream_obj.subtype,
                'format': f"{'Audio' if is_audio else 'Video'} - {stream_obj.subtype} ({stream_obj.abr if is_audio else stream_obj.resolution})",
                'url': stream_obj.url
            }
            if is_audio:
                data['acodec'] = stream_obj.audio_codec
            else:
                data.update({
                    'vcodec': stream_obj.video_codec,
                    'acodec': 'none' if not stream_obj.includes_audio_track else stream_obj.audio_codec
                })
            try:
                data['filesize'] = stream_obj.filesize
            except:
                pass
            return data

        response_data = {
            'id': yt.video_id,
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'duration': yt.length,
            'description': yt.description,
            'url': url,
            'embed_url': f"https://www.youtube.com/embed/{yt.video_id}",
            'best_audio': format_data(best_audio, is_audio=True) if best_audio else None,
            'best_video': format_data(best_video) if best_video else None,
            'all_formats': all_formats
        }
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f'Video info error: {e}')
        return jsonify({'error': f'Failed to get video information: {e}'}), 500

@app.route('/api/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    format_id = request.args.get('format')
    title = request.args.get('title', 'video')
    ext = request.args.get('ext', 'mp4')
    
    if not url or not format_id:
        return jsonify({'error': 'URL and format are required'}), 400

    try:
        yt = YouTube(url, use_po_token=True)
        stream = yt.streams.get_by_itag(int(format_id))
        if not stream:
            return jsonify({'error': f'Format {format_id} not available'}), 404

        safe_title = sanitize_filename(title)
        filename = f"{safe_title}.{ext}"
        stream_url = stream.url
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        @stream_with_context
        def generate():
            with requests.get(stream_url, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    yield chunk

        response = Response(generate(), content_type=content_type)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        try:
            head = requests.head(stream_url).headers
            if 'content-length' in head:
                response.headers['Content-Length'] = head['content-length']
        except:
            pass

        return response
    except Exception as e:
        app.logger.error(f'Download error: {e}')
        return jsonify({'error': f'Failed to download: {e}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
