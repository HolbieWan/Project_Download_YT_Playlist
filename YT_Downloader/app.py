from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import yt_dlp
from urllib.parse import urlparse
import shutil
import tempfile
import re
import ssl
import subprocess
import zipfile

app = Flask(__name__)

# Constants
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
COOKIES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies')
COOKIES_FILE = os.path.join(COOKIES_FOLDER, 'cookies.txt')

# Create necessary directories
for directory in [DOWNLOAD_FOLDER, COOKIES_FOLDER]:
    if not os.path.exists(directory):
        os.makedirs(directory)

def transform_url(url):
    # Remove 'music.' from YouTube Music URLs
    url = url.replace('music.youtube.com', 'youtube.com')
    
    # Extract the playlist ID
    if 'list=' in url:
        playlist_id = url.split('list=')[1].split('&')[0]
        # Return a clean YouTube playlist URL
        return f'https://youtube.com/playlist?list={playlist_id}'
    return url

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})|'
        r'(https?://)?(www\.)?youtube\.(com|be)/playlist\?list=([^&=%\?]+)'
    )
    return bool(re.match(youtube_regex, url))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-cookies', methods=['GET'])
def check_cookies():
    try:
        if os.path.exists(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
            with open(COOKIES_FILE, 'r') as f:
                content = f.read()
                if '.youtube.com' in content:
                    print("Valid YouTube cookies found")
                    return jsonify({'hasCookies': True})
                else:
                    print("Cookies file exists but no YouTube cookies found")
        else:
            print("No cookies file found or file is empty")
        return jsonify({'hasCookies': False})
    except Exception as e:
        print(f"Error checking cookies: {str(e)}")
        return jsonify({'hasCookies': False, 'error': str(e)})

@app.route('/save-cookies', methods=['POST'])
def save_cookies():
    try:
        data = request.get_json()
        cookies = data.get('cookies', '').strip()
        
        if not cookies:
            return jsonify({'error': 'No cookie content provided'}), 400

        # Validate cookie content
        if '.youtube.com' not in cookies:
            return jsonify({'error': 'Invalid cookie content. Must contain YouTube cookies.'}), 400

        # Create cookies directory if it doesn't exist
        os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
        
        # Save cookies to file
        with open(COOKIES_FILE, 'w') as f:
            f.write(cookies)
        
        # Verify the file was written correctly
        if not os.path.exists(COOKIES_FILE) or os.path.getsize(COOKIES_FILE) == 0:
            return jsonify({'error': 'Failed to save cookies'}), 500
            
        print(f"Cookies saved successfully to {COOKIES_FILE}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error saving cookies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-playlist', methods=['POST'])
def download_playlist():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please provide a playlist URL'}), 400
            
        # Transform the URL
        url = transform_url(url)
        
        if not is_valid_youtube_url(url):
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        print(f"Downloading from URL: {url}")

        # Check if cookies file exists and has content
        if not os.path.exists(COOKIES_FILE):
            return jsonify({'error': 'No cookies found. Please save your cookies first.'}), 400
        
        # Verify cookies file has content
        if os.path.getsize(COOKIES_FILE) == 0:
            return jsonify({'error': 'Cookies file is empty. Please save your cookies again.'}), 400

        # Create a unique folder for this download
        download_dir = os.path.join(DOWNLOAD_FOLDER, tempfile.mkdtemp(dir=DOWNLOAD_FOLDER).split('/')[-1])
        os.makedirs(download_dir, exist_ok=True)
        print(f"Download directory created: {download_dir}")

        # Use the working download command with subprocess and additional options
        command = [
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--output", os.path.join(download_dir, "%(title)s.%(ext)s"),
            "--no-check-certificates",  # Skip HTTPS certificate validation
            "--force-ipv4",            # Force IPv4 to avoid some connection issues
            "--ignore-errors",         # Continue on download errors
            "--no-playlist-reverse",   # Download playlist in the original order
            "--no-warnings",           # Suppress warnings
            "--extractor-args", "youtube:player_client=web",  # Use web client
            "--no-cache-dir",          # Disable cache
            url
        ]
        
        print("Starting download with yt-dlp...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.stderr:
            print("Download stderr:", result.stderr)
        
        print("Download stdout:", result.stdout)

        # Check if any MP3 files were downloaded
        mp3_files = [f for f in os.listdir(download_dir) if f.endswith('.mp3')]
        if not mp3_files:
            return jsonify({'error': 'No songs could be downloaded. Please check the playlist URL and try again.'}), 500

        # Create a zip file containing only MP3 files
        zip_filename = os.path.join(download_dir, "playlist_songs.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for mp3_file in mp3_files:
                file_path = os.path.join(download_dir, mp3_file)
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)

        return jsonify({
            'success': True,
            'message': f'Successfully downloaded {len(mp3_files)} songs',
            'download_path': os.path.basename(download_dir)
        })

    except Exception as e:
        print(f"Error during download: {str(e)}")
        # Clean up the download directory if it exists
        if 'download_dir' in locals() and os.path.exists(download_dir):
            try:
                shutil.rmtree(download_dir)
            except Exception as cleanup_error:
                print(f"Error cleaning up directory: {str(cleanup_error)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-download/<filename>')
def get_download(filename):
    try:
        download_dir = os.path.join(DOWNLOAD_FOLDER, filename)
        zip_file = os.path.join(download_dir, "playlist_songs.zip")
        
        if not os.path.exists(zip_file):
            return jsonify({'error': 'Download file not found'}), 404

        return send_file(
            zip_file,
            as_attachment=True,
            download_name="playlist_songs.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
