#!/usr/bin/env python3
"""Interactive downloader for videos in your own TikTok data-export ZIP."""

from __future__ import annotations

import csv
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json

import requests

APP_NAME = "TikTok Export Video Downloader"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Referer": "https://www.tiktok.com/",
}

def safe_name(value: str, limit: int = 60) -> str:
    value = re.sub(r'[\\/:*?"<>|]+', "_", str(value or ""))
    value = re.sub(r"\s+", " ", value).strip(" ._")
    return (value[:limit].rstrip(" ._") or "TikTok_User")

def is_mp4_link(url: str) -> bool:
    try:
        query = parse_qs(urlparse(url).query)
        return query.get("mime_type", [""])[0] == "video_mp4"
    except (TypeError, ValueError):
        return False

def load_posts(zip_path: Path) -> list[dict]:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            json_files = [
                name for name in archive.namelist()
                if name.lower().endswith(".json")
            ]
            if not json_files:
                raise ValueError("No JSON file was found inside this ZIP.")

            selected = next(
                (name for name in json_files if "user_data_tiktok" in name.lower()),
                json_files[0],
            )
            data = json.loads(archive.read(selected).decode("utf-8-sig"))
    except zipfile.BadZipFile as exc:
        raise ValueError("That file is not a valid ZIP archive.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("Could not decode the TikTok JSON export.") from exc

    posts = (
        data.get("Post", {})
            .get("Posts", {})
            .get("VideoList", [])
    )
    if not isinstance(posts, list):
        raise ValueError("This export does not contain the expected TikTok VideoList.")
    return posts

def download_video(session: requests.Session, url: str, destination: Path) -> tuple[bool, str]:
    temp_path = destination.with_name(destination.name + ".part")
    last_error = "Unknown download error"

    for attempt in range(1, 4):
        try:
            with session.get(
                url, headers=HEADERS, stream=True, timeout=(20, 90)
            ) as response:
                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code}"
                    if response.status_code in (400, 401, 403, 404, 410):
                        return False, last_error
                    response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                total = 0
                first_bytes = b""

                with temp_path.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=256 * 1024):
                        if not chunk:
                            continue
                        if not first_bytes:
                            first_bytes = chunk[:128]
                        output.write(chunk)
                        total += len(chunk)

                if total < 1024:
                    raise ValueError(f"Response was only {total} bytes.")
                if b"ftyp" not in first_bytes:
                    raise ValueError(
                        "Response did not look like an MP4 file "
                        f"(Content-Type: {content_type or 'unknown'})."
                    )

                temp_path.replace(destination)
                return True, f"{total:,} bytes"

        except requests.RequestException as exc:
            last_error = f"Network error: {exc}"
        except (OSError, ValueError) as exc:
            last_error = str(exc)

        temp_path.unlink(missing_ok=True)
        if attempt < 3:
            time.sleep(attempt * 2)

    return False, last_error

def show_videos(videos: list[dict]) -> None:
    print("\nPublic videos found in this export:")
    print("-" * 78)
    for number, post in enumerate(videos, 1):
        date = post.get("Date", "Unknown date")
        likes = post.get("Likes", "?")
        title = post.get("Title", "")
        if not title or title == "N/A":
            title = "(no title in export)"
        print(f"{number:>3}. {date} | Likes: {likes} | {title[:35]}")
    print("-" * 78)

def choose_videos(videos: list[dict]) -> list[tuple[int, dict]]:
    while True:
        print("\nWhat would you like to download?")
        print("  A  - All public videos")
        print("  S  - Select videos by number (example: 1,3,5)")
        print("  Q  - Quit")
        choice = input("Your choice [A/S/Q]: ").strip().lower()

        if choice == "a":
            return list(enumerate(videos, 1))
        if choice == "q":
            return []
        if choice == "s":
            raw = input("Enter video numbers separated by commas: ").strip()
            try:
                numbers = sorted({int(part.strip()) for part in raw.split(",") if part.strip()})
                if not numbers:
                    print("No numbers entered.")
                    continue
                if any(number < 1 or number > len(videos) for number in numbers):
                    print(f"Choose numbers from 1 to {len(videos)}.")
                    continue
                return [(number, videos[number - 1]) for number in numbers]
            except ValueError:
                print("Please enter numbers separated by commas, for example: 1,3,5.")
                continue
        print("Please choose A, S, or Q.")

def main() -> int:
    print(f"\n=== {APP_NAME} ===")
    print("This tool reads your own TikTok data-export ZIP.")
    print("It does not log in to TikTok, scrape profiles, or publish to Instagram.\n")

    username = input("TikTok username (with or without @): ").strip().lstrip("@")
    if not username:
        print("A username is required.")
        return 1
    username_folder = safe_name(username)

    zip_input = input("Path to your TikTok data-export ZIP: ").strip().strip('"').strip("'")
    zip_path = Path(zip_input).expanduser()
    if not zip_path.is_file():
        print(f"File not found: {zip_path}")
        return 1

    try:
        posts = load_posts(zip_path)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Could not read export: {exc}")
        return 1

    public_posts = [post for post in posts if post.get("WhoCanView") == "Everyone"]
    public_videos = [
        post for post in public_posts
        if is_mp4_link(post.get("Link", ""))
    ]
    photo_or_other = len(public_posts) - len(public_videos)

    print("\nExport summary")
    print(f"  Posts in export:       {len(posts)}")
    print(f"  Public posts:          {len(public_posts)}")
    print(f"  Public MP4 videos:     {len(public_videos)}")
    print(f"  Other public posts:    {photo_or_other}")
    print("  Private posts:         not included")

    if not public_videos:
        print("\nNo public MP4 videos were found in this export.")
        return 0

    show_videos(public_videos)
    selected = choose_videos(public_videos)
    if not selected:
        print("Nothing selected. Exiting.")
        return 0

    output_dir = Path.cwd() / "downloads" / username_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nSaving selected videos to: {output_dir.resolve()}\n")

    results = []
    saved = skipped = failed = 0
    session = requests.Session()

    for position, (original_number, post) in enumerate(selected, 1):
        date = safe_name(post.get("Date", "unknown-date"), 30).replace(":", "-")
        filename = f"{original_number:03d}_{date}.mp4"
        destination = output_dir / filename

        if destination.exists() and destination.stat().st_size >= 1024:
            status = "SKIPPED_EXISTING"
            detail = f"{destination.stat().st_size:,} bytes already present"
            skipped += 1
            print(f"[{position}/{len(selected)}] SKIP  {filename}")
        else:
            print(f"[{position}/{len(selected)}] GET   {filename}", flush=True)
            ok, detail = download_video(session, post.get("Link", ""), destination)
            if ok:
                status = "DOWNLOADED"
                saved += 1
                print(f"    OK: {detail}")
            else:
                status = "FAILED"
                failed += 1
                print(f"    FAILED: {detail}")

        results.append({
            "export_video_number": original_number,
            "date": post.get("Date", ""),
            "title": post.get("Title", ""),
            "likes": post.get("Likes", ""),
            "visibility": post.get("WhoCanView", ""),
            "status": status,
            "details": detail,
            "filename": filename if status != "FAILED" else "",
        })

    manifest_path = output_dir / "download_report.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print("\nCompleted.")
    print(f"  Downloaded: {saved}")
    print(f"  Already existed: {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Report: {manifest_path.resolve()}")
    if failed:
        print(
            "\nSome TikTok links were rejected. A 403 usually means TikTok "
            "refused that export link; retrying the same link may not help. "
            "Request a fresh data export and try again."
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
