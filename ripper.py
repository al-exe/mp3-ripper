#!/usr/bin/env python3
"""
Audio downloader + cover embedder utility.

- Downloads audio (MP3) from URLs/playlists
- Saves to ~/Desktop/<ALBUM>/
- Crops album art to 480x480 and embeds it
- Deletes artwork after embedding
- Supports:
    * CLI args
    * Interactive prompt if args missing
"""

import argparse, subprocess, os, sys, tempfile, shutil, getpass, pathlib

def eprint(*a, **k): print(*a, file=sys.stderr, **k)

def run(cmd):
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=False)

def need(cmd):
    if shutil.which(cmd) is None:
        eprint(f"❌ Missing required tool: {cmd}")
        sys.exit(1)

def read_urls_from_stdin():
    if sys.stdin.isatty():
        return []
    return [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]

def interactive_prompt(args, default_dir):
    print("*** Interactive Mode ***")
    album = args.album or input("Album folder name (on Desktop): ").strip()
    while not album:
        album = input("Album name is required: ").strip()

    custom_dir = input(
        f"Ripper will create ({album}) on Desktop ({default_dir}). Press Enter to accept or specify another directory: "
    ).strip()
    target_dir = os.path.abspath(os.path.expanduser(custom_dir)) if custom_dir else default_dir

    urls = list(args.url or [])
    if not urls:
        print("Enter video or playlist URLs (blank line to finish):")
        while True:
            line = input().strip()
            if not line: break
            urls.append(line)

    rate = args.rate or input("Rate limit (optional, e.g., 2M): ").strip()
    return album, target_dir, urls, rate

def resolve_home():
    if "SUDO_USER" in os.environ and os.environ["SUDO_USER"] != "root":
        user = os.environ["SUDO_USER"]
        home = os.path.expanduser(f"~{user}")
    else:
        user = getpass.getuser()
        home = os.path.expanduser("~")
    return user, home

def embed_covers(dest):
    print(f"\n*** Embedding covers in {dest}")
    SIZE = "480"
    any_found = False

    for root, _, files in os.walk(dest):
        for f in files:
            if not f.lower().endswith(".mp3"): continue

            mp3 = os.path.join(root, f)
            base = f[:-4]
            arts = [f"{base}.jpg", f"{base}.png", "cover.jpg", "cover.png"]
            art = next((os.path.join(root,a) for a in arts if os.path.exists(os.path.join(root,a))), None)

            if not art:
                print(f"[embed] no artwork → {f}")
                continue

            any_found = True
            tmpimg = tempfile.mktemp(dir=root, suffix=".jpg")
            tmpmp3 = tempfile.mktemp(dir=root, suffix=".mp3")

            # Crop and resize artwork
            run([
                "ffmpeg","-hide_banner","-loglevel","error","-y",
                "-i", art,
                "-vf", f"crop='min(iw,ih)':'min(iw,ih)',scale={SIZE}:{SIZE}",
                "-q:v","2", tmpimg
            ])

            # Embed image
            run([
                "ffmpeg","-hide_banner","-loglevel","error","-y",
                "-i", mp3,"-i", tmpimg,
                "-map","0:a","-map","1:v:0","-c","copy",
                "-id3v2_version","3",
                "-metadata:s:v","title=Album cover",
                "-metadata:s:v","comment=Cover (front)",
                tmpmp3
            ])

            shutil.move(tmpmp3, mp3)
            os.remove(tmpimg)
            os.remove(art)
            print(f"[embed] cover added → {f}")

    if not any_found:
        print("No MP3s found for embedding")
    print("✅ Embedding complete")

def delete_jpg_files(dest):
    print(f"\n*** Removing JPG files in {dest}")
    removed = 0
    for root, _, files in os.walk(dest):
        for f in files:
            if f.lower().endswith(".jpg"):
                os.remove(os.path.join(root, f))
                removed += 1
    print(f"🗑️ Removed {removed} JPG file(s)")

def main():
    need("yt-dlp"); need("ffmpeg")

    p = argparse.ArgumentParser(description="Download audio + embed artwork")
    p.add_argument("--album", help="Folder name (Desktop)")
    p.add_argument("--url", action="append", help="URL or playlist (repeatable)")
    p.add_argument("--rate", default="", help="Limit (e.g., 2M)")
    p.add_argument("--stdin", action="store_true", help="Read URLs from stdin")

    args = p.parse_args()

    user, home = resolve_home()
    default_dir = os.path.join(home,"Desktop")

    urls = list(args.url or [])
    if args.stdin and not sys.stdin.isatty():
        urls += read_urls_from_stdin()

    album = args.album
    rate = args.rate
    target_dir = default_dir

    # Interactive if album/urls missing
    if not album or not urls:
        album, target_dir, urls, rate = interactive_prompt(args, default_dir)

    dest = os.path.join(target_dir, album)
    os.makedirs(dest, exist_ok=True)

    archive = os.path.join(dest,".downloaded.txt")
    pathlib.Path(archive).touch()

    print(f"Album: {album}")
    print(f"Folder: {dest}")
    if rate: print(f"Limit: {rate}")

    # Downloader
    base = [
        "yt-dlp", "-x","--audio-format","mp3","--audio-quality","0",
        "--add-metadata","--write-thumbnail","--convert-thumbnails","jpg",
        "--no-embed-thumbnail","--ignore-errors",
        "--output",f"{dest}/%(title)s",
        "--download-archive",archive,
    ]
    if rate: base += ["--limit-rate",rate]

    for u in urls:
        print(f"\n>>> Downloading: {u}")
        run(base + [u])

    print("\n✅ Downloads complete")
    embed_covers(dest)
    delete_jpg_files(dest)
    print(f"\n✨ Done → {dest}")

if __name__ == "__main__":
    main()
