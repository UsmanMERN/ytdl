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
from urllib.parse import quote, urlencode
import requests

from flask import Flask, request, jsonify, send_file, Response, redirect
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

def sanitize_filename(s: str) -> str:
    """
    Replace illegal filename characters with underscores and collapse whitespace.
    """
    # Replace any character that is not alphanumeric or space with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9 ]', '_', s)
    # Collapse spaces to underscores
    sanitized = re.sub(r'\s+', '_', sanitized.strip())
    return sanitized

@app.route('/', methods=['GET'])
def index():
    return 'API is running...'

@app.route('/api/search', methods=['GET'])
def search_videos():
    """
    Search YouTube for query terms and return a list of video metadata.
    Query param: q (string)
    """
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # Do not download videos
            'default_search': 'ytsearch10',  # Search for 10 videos
            'skip_download': True,  # Skip downloading the video
            'ignoreerrors': True,  # Skip videos that cause errors
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
        results = []
        if search_results and 'entries' in search_results:
            for entry in search_results['entries']:
                if entry is None:
                    continue
                
                # Ensure we have a valid ID
                video_id = entry.get('id')
                if not video_id:
                    continue
                
                # Build the video URL
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Get thumbnail URL (different formats available)
                thumbnail = None
                if entry.get('thumbnails'):
                    # Try to get a medium-quality thumbnail
                    for thumb in entry.get('thumbnails', []):
                        if thumb.get('url'):
                            thumbnail = thumb.get('url')
                            break
                    
                # If no thumbnail found in thumbnails list, try the legacy field
                if not thumbnail:
                    thumbnail = entry.get('thumbnail', '')
                
                results.append({
                    'id': video_id,
                    'title': entry.get('title', ''),
                    'description': entry.get('description', ''),
                    'thumbnail': thumbnail,
                    'duration': entry.get('duration', 0),
                    'url': video_url
                })
        
        return jsonify({'results': results})
    except Exception as e:
        app.logger.error(f'Search error: {str(e)}')
        return jsonify({'error': f'Failed to search videos: {str(e)}'}), 500

@app.route('/api/video', methods=['GET'])
def video_info():
    """
    Fetch YouTube video info given a URL, including available formats with direct download URLs.
    Query param: url (string)
    """
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # Don't download, just get info
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            return jsonify({'error': 'Could not fetch video information'}), 404
        
        # Find best audio and video formats
        best_audio = None
        best_video = None
        all_formats = []
        
        for fmt in info.get('formats', []):
            format_info = {
                'format_id': fmt.get('format_id', ''),
                'ext': fmt.get('ext', ''),
                'format': fmt.get('format', ''),
                'format_note': fmt.get('format_note', ''),
                'url': fmt.get('url', '')  # Include the direct URL
            }
            
            # Add filesize if available
            if fmt.get('filesize') is not None:
                format_info['filesize'] = fmt.get('filesize')
                
            # Add codec info if available
            format_info['acodec'] = fmt.get('acodec', 'none')
            format_info['vcodec'] = fmt.get('vcodec', 'none')
            
            # Add resolution if present
            if fmt.get('width') and fmt.get('height'):
                format_info['resolution'] = f"{fmt.get('width')}x{fmt.get('height')}"
                format_info['height'] = fmt.get('height')  # Store for comparison
            
            # Check if this is a video+audio format
            if fmt.get('acodec') != 'none' and fmt.get('vcodec') != 'none':
                if not best_video:
                    best_video = fmt
                elif fmt.get('height') and best_video.get('height'):
                    if fmt.get('height', 0) > best_video.get('height', 0):
                        best_video = fmt
            
            # Add aspect ratio if available
            if fmt.get('aspect_ratio'):
                format_info['aspect_ratio'] = fmt.get('aspect_ratio')
            # Check if this is audio only
            if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                if not best_audio:
                    best_audio = fmt
                elif fmt.get('tbr') and best_audio.get('tbr'):
                    if fmt.get('tbr', 0) > best_audio.get('tbr', 0):
                        best_audio = fmt
            
            all_formats.append(format_info)
        
        # Format the best_audio and best_video to include only relevant info
        best_audio_data = None
        if best_audio:
            best_audio_data = {
                'format_id': best_audio.get('format_id', ''),
                'ext': best_audio.get('ext', ''),
                'format': best_audio.get('format', ''),
                'acodec': best_audio.get('acodec', 'none'),
                'url': best_audio.get('url', '')  # Include direct URL
            }
            if best_audio.get('filesize') is not None:
                best_audio_data['filesize'] = best_audio.get('filesize')
        
        best_video_data = None
        if best_video:
            best_video_data = {
                'format_id': best_video.get('format_id', ''),
                'ext': best_video.get('ext', ''),
                'format': best_video.get('format', ''),
                'vcodec': best_video.get('vcodec', ''),
                'acodec': best_video.get('acodec', ''),
                'url': best_video.get('url', '')  # Include direct URL
            }
            if best_video.get('width') and best_video.get('height'):
                best_video_data['resolution'] = f"{best_video.get('width')}x{best_video.get('height')}"
            if best_video.get('filesize') is not None:
                best_video_data['filesize'] = best_video.get('filesize')
        
        # Get thumbnail URL (multiple formats may be available)
        thumbnail = None
        if info.get('thumbnails'):
            for thumb in info.get('thumbnails', []):
                if thumb.get('url'):
                    thumbnail = thumb.get('url')
                    break
        
        # If no thumbnail in thumbnails list, fall back to legacy field
        if not thumbnail:
            thumbnail = info.get('thumbnail', '')
        
        # Create download URLs for frontend
        safe_title = sanitize_filename(info.get('title', 'video'))
        
        # Add download endpoints to response
        if best_audio_data:
            best_audio_data['download_url'] = f"/api/download?url={quote(url)}&format_id={best_audio_data['format_id']}&title={quote(safe_title)}"
        
        if best_video_data:
            best_video_data['download_url'] = f"/api/download?url={quote(url)}&format_id={best_video_data['format_id']}&title={quote(safe_title)}"
        
        # Add download endpoints to all formats
        for fmt in all_formats:
            fmt['download_url'] = f"/api/download?url={quote(url)}&format_id={fmt['format_id']}&title={quote(safe_title)}"
        
        # Prepare response data
        data = {
            'id': info.get('id', ''),
            'title': info.get('title', ''),
            'thumbnail': thumbnail,
            'duration': info.get('duration', 0),
            'description': info.get('description', ''),
            'url': info.get('webpage_url', url),  # Return the original URL if webpage_url not available
            'embed_url': f"https://www.youtube.com/embed/{info.get('id', '')}",
            'best_audio': best_audio_data,
            'best_video': best_video_data,
            'all_formats': all_formats
        }
        
        return jsonify(data)
    except Exception as e:
        app.logger.error(f'Video info error: {str(e)}')
        return jsonify({'error': f'Failed to get video information: {str(e)}'}), 500

@app.route('/api/download', methods=['GET'])
def download_video():
    """
    Download a YouTube video in the specified format directly to the user's browser.
    Query params:
    - url: YouTube URL
    - format_id: The format ID to download
    - title: Optional video title for the filename
    """
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    title = request.args.get('title', 'video')
    
    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400
    
    if not format_id:
        return jsonify({'error': 'Format ID is required'}), 400
    
    try:
        # Get info about the format to determine the filename extension
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # Don't download, just get info
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Find the requested format
            selected_format = None
            for fmt in info.get('formats', []):
                if fmt.get('format_id') == format_id:
                    selected_format = fmt
                    break
            
            if not selected_format:
                return jsonify({'error': 'Requested format not found'}), 404
            
            # Get the direct URL for the format
            direct_url = selected_format.get('url')
            if not direct_url:
                return jsonify({'error': 'No direct URL found for this format'}), 404
            
            # Get file extension
            ext = selected_format.get('ext', 'mp4')
            
            # Create a filename based on title and extension
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}.{ext}"
            
            # For MP4 and WebM videos, we need to use a different approach
            # to force download instead of playing in browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Referer': url
            }
            
            # Fetch the file in chunks from the direct URL and stream it to the client
            # This approach bypasses the browser's default handling of media files
            def generate():
                import requests
                r = requests.get(direct_url, headers=headers, stream=True)
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    yield chunk
            
            response = Response(generate(), mimetype='application/octet-stream')
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    except Exception as e:
        app.logger.error(f'Download error: {str(e)}')
        return jsonify({'error': f'Failed to download video: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)