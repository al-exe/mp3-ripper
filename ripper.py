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
    * Optional album artist override
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
    print("===== Interactive Mode =====")
    album = args.album or input("Enter desired album name: ").strip()
    while not album:
        album = input("Album name is required: ").strip()

    # Optional album artist
    album_artist = args.artist
    if album_artist is None:
        album_artist = input("Enter album artist (optional): ").strip() or None

    custom_dir = input(
        f"mp3-ripper will create album ({album}) on your desktop ({default_dir}). "
        f"Press Enter to accept or specify another directory instead: "
    ).strip()
    target_dir = os.path.abspath(os.path.expanduser(custom_dir)) if custom_dir else default_dir

    urls = list(args.url or [])
    if not urls:
        print("Enter video or playlist URLs (blank line to finish):")
        while True:
            line = input().strip()
            if not line:
                break
            urls.append(line)

    return album, target_dir, urls, album_artist

def resolve_home():
    if "SUDO_USER" in os.environ and os.environ["SUDO_USER"] != "root":
        user = os.environ["SUDO_USER"]
        home = os.path.expanduser(f"~{user}")
    else:
        user = getpass.getuser()
        home = os.path.expanduser("~")
    return user, home

def embed_covers(dest, album_artist=None):
    print(f"\n*** Embedding covers / metadata in {dest}")
    SIZE = "480"
    any_found = False

    for root, _, files in os.walk(dest):
        mp3_files = sorted(f for f in files if f.lower().endswith(".mp3"))
        img_files = sorted(
            f for f in files
            if f.lower().endswith(".jpg") or f.lower().endswith(".png")
        )

        if not mp3_files:
            continue

        used_images = set()

        for f in mp3_files:
            any_found = True
            mp3 = os.path.join(root, f)
            base = f[:-4]  # filename without .mp3
            track_title = base

            # 1) Try strict basename match: "<base>.jpg" or "<base>.png"
            exact_candidates = [
                img for img in img_files
                if os.path.splitext(img)[0] == base and img not in used_images
            ]

            art_file = None
            if exact_candidates:
                art_file = exact_candidates[0]
            else:
                # 2) Fallback: any unused image
                remaining = [img for img in img_files if img not in used_images]
                if remaining:
                    art_file = remaining[0]

            tmpmp3 = tempfile.mktemp(dir=root, suffix=".mp3")

            if art_file:
                used_images.add(art_file)
                art = os.path.join(root, art_file)

                tmpimg = tempfile.mktemp(dir=root, suffix=".jpg")

                # Crop + resize artwork
                run([
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", art,
                    "-vf", f"crop='min(iw,ih)':'min(iw,ih)',scale={SIZE}:{SIZE}",
                    "-q:v", "2", tmpimg
                ])

                cmd = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", mp3, "-i", tmpimg,
                    "-map", "0:a", "-map", "1:v:0", "-c", "copy",
                    "-id3v2_version", "3",
                    "-metadata:s:v", "title=Album cover",
                    "-metadata:s:v", "comment=Cover (front)",
                ]
                if album_artist:
                    cmd += ["-metadata", f"artist={album_artist}"]
                # Title metadata matches filename
                cmd += ["-metadata", f"title={track_title}", tmpmp3]

                run(cmd)

                shutil.move(tmpmp3, mp3)
                os.remove(tmpimg)
                print(f"[embed] cover + title/artist updated → {f} (art: {art_file})")

            else:
                # No artwork found for this MP3, but still normalize title/artist
                cmd = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", mp3,
                    "-c", "copy",
                ]
                if album_artist:
                    cmd += ["-metadata", f"artist={album_artist}"]
                cmd += ["-metadata", f"title={track_title}", tmpmp3]

                run(cmd)
                shutil.move(tmpmp3, mp3)
                print(f"[embed] title/artist updated (no art) → {f}")

    if not any_found:
        print("No MP3s found for embedding/metadata updates")
    print("✅ Embedding complete")

def delete_image_files(dest):
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
    p.add_argument("--artist", help="Album artist (override track artists)")
    p.add_argument("--url", action="append", help="URL or playlist (repeatable)")
    p.add_argument("--rate", default="", help="Limit (e.g., 2M)")
    p.add_argument("--stdin", action="store_true", help="Read URLs from stdin")

    args = p.parse_args()

    user, home = resolve_home()
    default_dir = os.path.join(home, "Desktop")

    urls = list(args.url or [])
    if args.stdin and not sys.stdin.isatty():
        urls += read_urls_from_stdin()

    album = args.album
    rate = args.rate
    album_artist = args.artist
    target_dir = default_dir

    if not album or not urls:
        album, target_dir, urls, album_artist = interactive_prompt(args, default_dir)

    dest = os.path.join(target_dir, album)
    os.makedirs(dest, exist_ok=True)

    archive = os.path.join(dest, ".downloaded.txt")
    pathlib.Path(archive).touch()

    print(f"Album: {album}")
    if album_artist:
        print(f"Artist: {album_artist}")
    print(f"Folder: {dest}")
    if rate:
        print(f"Limit: {rate}")

    # yt-dlp: download + metadata
    base = [
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
        "--add-metadata", "--write-thumbnail", "--convert-thumbnails", "jpg",
        "--no-embed-thumbnail", "--ignore-errors",

        # Track numbers from playlist order
        "--parse-metadata", "playlist_index:%(track_number)s",
        "--parse-metadata", "playlist_index:%(track)s",

        # Sanitize filename by stripping quotes and truncating to 128 chars
        "--output",
        f"{dest}/%(title,.|replace:'\"',''|replace:'＂',''|replace:'“',''|replace:'”','').128s",

        "--download-archive", archive,
    ]

    if rate:
        base += ["--limit-rate", rate]

    for u in urls:
        print(f"\n>>> Downloading: {u}")
        run(base + [u])

    print("\n✅ Downloads complete")
    embed_covers(dest, album_artist=album_artist)
    delete_image_files(dest)
    print(f"\n✨ Done → {dest}")

if __name__ == "__main__":
    main()
