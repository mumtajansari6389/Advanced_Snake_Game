import urllib.request
import os

sounds_dir = os.path.join("assets", "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Wikimedia commons OGG files
files = {
    "background.ogg": "https://upload.wikimedia.org/wikipedia/commons/e/e4/A_chiptune_song_I_made_in_Famitracker.ogg",
    "eat.ogg": "https://upload.wikimedia.org/wikipedia/commons/0/06/Pop_sound.ogg",
    "gameover.ogg": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Siren_noise.ogg"
}

for filename, url in files.items():
    path = os.path.join(sounds_dir, filename)
    try:
        print(f"Downloading {filename}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Saved to {path}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
