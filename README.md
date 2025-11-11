# mp3-ripper

Lightning fast MP3 ripping from YouTube with automatic metadata tagging and cover embedding.

## 🎧 What This Does

A lightweight Python tool that:

- Downloads audio (MP3) from YouTube or other yt-dlp supported sites
- Extracts, crops, and tags album art ready thumbnails.

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

## 🚀 Installation

```bash
mv audio_embed.py ~/audio_embed.py
chmod +x ~/audio_embed.py
```

Run it:

```bash
python3 ~/audio_embed.py
```

---

## 🛠️ Usage

### **Interactive Mode (no flags)**  
Script will ask you for album name & URLs:

```bash
python3 audio_embed.py
```

Prompts will ask for:

- Album folder name
- Video / playlist URLs
- Optional rate limit (ex. `2M`)

---

### **One-Shot Download**

```bash
python3 audio_embed.py --album "Chill Beats"   --url "https://youtube.com/watch?v=VIDEO_ID"
```

---

### **Multiple URLs**

```bash
python3 audio_embed.py --album "Focus Session"   --url "https://youtube.com/watch?v=AAA111"   --url "https://youtube.com/watch?v=BBB222"
```

---

### **Pipe URLs from a File**

```bash
cat urls.txt | python3 audio_embed.py --album "Morning Mix" --stdin
```

`urls.txt` example:

```
https://youtube.com/watch?v=ABC123
https://youtube.com/watch?v=DEF456
```

---

### **Rate-Limited Download**

Useful for slower connections or throttled networks:

```bash
python3 audio_embed.py --album "Jazz Collection"   --url "https://youtube.com/watch?v=SOMEVIDEO"   --rate 1.5M
```

---

## 🏁 Done!

Music downloads → cleaned → tagged → artwork embedded.  
Just run & enjoy your organized local MP3 library 🎶

---
