# mp3-ripper

Lightning fast MP3 ripping from YouTube with automatic metadata tagging and cover embedding.

## 🎧 What This Does

- Downloads audio (MP3) from YouTube or other yt-dlp supported sites
- Crops/embeds cover art and writes ID3 metadata (title/album/artist)
- Saves to `~/Desktop/<ALBUM>/` with a download archive to avoid duplicates
- Can drive downloads from a `library.json` file (`--all` or `--albums ...`)

Perfect for building local playlists and clean, metadata-tagged music libraries.

---

## ✅ Requirements

Install tools:

**macOS:**
```bash
brew install yt-dlp ffmpeg
```

**Linux (Ubuntu / Debian):**
```bash
sudo apt install yt-dlp ffmpeg
```

Requires Python **3.8+**

---

## 🛠️ Usage

From the repo root:
```bash
python3 ripper.py [flags...]
```

Outputs to `~/Desktop/<album>/`.

### Interactive (prompts)
```bash
python3 ripper.py
```
Prompts for album name, optional album artist, URLs, and target directory.

### Single album (explicit args)
```bash
python3 ripper.py --album "Chill Beats" --url "https://youtube.com/watch?v=VIDEO_ID"
```
Add more URLs with repeated `--url`. Optional flags: `--artist "Override Artist"`, `--rate 2M`, `--stdin` to read URLs from stdin.

### From library.json
- Download everything:  
  ```bash
  python3 ripper.py --all
  ```
- Download selected albums:  
  ```bash
  python3 ripper.py --albums album-one album-two
  ```
- Custom library path: add `--library /path/to/library.json`
- Global artist override: add `--artist "Some Artist"`

`library.json` maps album names to objects:
```json
{
  "album-slug": { "url": "https://playlist-or-video", "artist": "Optional Artist" }
}
```

---

## 🏁 Done!

Music downloads → cleaned → tagged → artwork embedded.  
Run & enjoy your organized local MP3 library 🎶
