# import yt_dlp

# def download_audio_as_mp4(video_url, output_dir):
#     # Options pour yt-dlp
#     ydl_opts = {
#         'format': 'bestaudio[ext=mp4]',  # Télécharger le meilleur audio en MP4
#         'outtmpl': f'{output_dir}/%(title)s.%(ext)s',  # Chemin et nom de fichier
#         'noplaylist': True,  # Assurer que seule la vidéo spécifiée est téléchargée
#     }

#     try:
#         # Initialiser et exécuter yt-dlp
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             print(f"Téléchargement de l'audio de : {video_url}")
#             ydl.download([video_url])
#             print("Téléchargement terminé.")
#     except Exception as e:
#         print(f"Erreur lors du téléchargement : {e}")

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # URL de la vidéo YouTube
#     video_url = "https://www.youtube.com/watch?v=hBpw0lh-QJM&list=LM&index=1"  # Remplacez VIDEO_ID par l'ID réel
#     # Dossier de téléchargement
#     output_dir = "/Users/mjx/Music/DL_YT_Playlist"  # Assurez-vous que ce dossier existe ou remplacez-le par un chemin valide
#     download_audio_as_mp4(video_url, output_dir)


# import yt_dlp

# def download_playlist(playlist_url, output_dir):
#     ydl_opts = {
#         'format': 'bestaudio[ext=mp4]',  # Download audio-only in MP4 format
#         'outtmpl': f'{output_dir}/%(playlist_title)s/%(title)s.%(ext)s',  # Save videos in a folder named after the playlist
#         'noplaylist': False,  # Allow downloading the entire playlist
#         'verbose': True,  # Show detailed debugging output
#         'postprocessors': [
#             {'key': 'EmbedThumbnail'},  # Embed thumbnails (if available)
#             {'key': 'FFmpegMetadata'},  # Embed metadata (requires ffmpeg)
#         ],
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             print(f"Starting playlist download: {playlist_url}")
#             ydl.download([playlist_url])
#             print("Playlist download completed.")
#     except Exception as e:
#         print(f"Error during playlist download: {e}")

# if __name__ == "__main__":
#     playlist_url = "https://www.youtube.com/watch?v=l1HvVR4Hxm8&list=RDl1HvVR4Hxm8&start_radio=1"  # Use correct playlist URL
#     output_dir = "/Users/mjx/Music/DL_YT_Playlist"  # Make sure this directory exists
#     download_playlist(playlist_url, output_dir)

# import yt_dlp
# import os

# def download_playlist_as_mp3(playlist_url, output_dir, cookies_file):
#     """
#     Downloads the entire YouTube playlist as MP3 files.

#     Args:
#         playlist_url (str): URL of the YouTube playlist.
#         output_dir (str): Directory where files will be saved.
#         cookies_file (str): Path to the cookies.txt file for authentication.
#     """
#     # Validate the cookies file path
#     if not os.path.exists(cookies_file):
#         print(f"Error: Cookies file not found at {cookies_file}")
#         return

#     ydl_opts = {
#         'format': 'bestaudio',
#         'extractaudio': True,
#         'audioformat': 'mp3',
#         'audioquality': '0',
#         'outtmpl': os.path.join(output_dir, '%(playlist_title)s/%(track_number)s - %(title)s.%(ext)s'),
#         'cookies': cookies_file,
#         'verbose': True,
#     }

#     try:
#         print(f"Using options: {ydl_opts}")
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             print(f"Starting download of playlist: {playlist_url}")
#             ydl.download([playlist_url])
#             print("Playlist download completed.")
#     except Exception as e:
#         print(f"Error during download: {e}")

# if __name__ == "__main__":
#     # Replace with your playlist URL
#     playlist_url = "https://youtube.com/playlist?list=LM"
#     # Directory to save downloads
#     output_dir = "./downloads_2"
#     # Path to cookies file
#     cookies_file = "/Users/mjx/Documents/Developper_Web/Projet_DL_Playlist/cookies.txt"

#     download_playlist_as_mp3(playlist_url, output_dir, cookies_file)

import os
import subprocess

def download_playlist_via_cli():
    command = [
        "yt-dlp",
        "--cookies", "/Users/mjx/Documents/Developper_Web/Project_Download_YT_Playlist/cookies.txt",
        "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0",
        "--output", "./downloads_2/%(playlist_title)s/%(title)s.%(ext)s",
        "https://www.youtube.com/playlist?list=LM"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    download_playlist_via_cli()