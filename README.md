# TikTok Export Video Downloader

A simple interactive Python tool for downloading your own public TikTok videos from your TikTok data export.

No TikTok login required. No complicated configuration.

## Features

- Reads your TikTok data-export ZIP file.
- Finds posts marked as public (`Everyone`).
- Identifies public MP4 videos.
- Displays a numbered list of available videos.
- Download all videos or select specific ones.
- Organizes downloads into a folder named after your username.
- Checks downloaded files to reject empty or invalid responses.
- Generates a CSV download report.
- Retries temporary network errors.

## How It Works

1. Request your TikTok data export.
2. Download the ZIP file from TikTok.
3. Run this program.
4. Enter your TikTok username.
5. Provide the location of your ZIP file.
6. Choose which videos to download.
7. Find your downloaded videos in the output folder.

**Important:** This program does not download videos by searching a TikTok username. Your username is only used to name the output folder. You must provide your own TikTok data-export ZIP.

## Requirements

- Python 3.10 or newer
- Internet connection
- Your TikTok data-export ZIP file

## Installation

### Windows / Linux / macOS

Install Python first.

Open a terminal and run:

```bash
git clone https://github.com/Ximicode-tech/tiktok-export-video-downloader.git
cd tiktok-export-video-downloader
python -m pip install -r requirements.txt
```

### Android (Termux)

Install Termux, then run:

```bash
pkg update
pkg install python git
termux-setup-storage
```

Clone the repository:

```bash
git clone https://github.com/Ximicode-tech/tiktok-export-video-downloader.git
cd tiktok-export-video-downloader
```

Install the dependency:

```bash
python -m pip install -r requirements.txt
```

### Getting Your TikTok Data

- Open TikTok.
- Go to Settings and privacy.
- Open Account.
- Select Download your data.
- Request your data export.
- Wait until TikTok makes the export available.
- Download the ZIP file.

Keep this ZIP private because it may contain personal account information.

### Usage

Start the program:

```bash
python main.py
```

The program will ask for your TikTok username:

```text
TikTok username (with or without @):
```

Enter your username.

Next, provide the path to your TikTok ZIP file.

Example on Android:

```text
~/storage/shared/Download/tiktok-data.zip
```

The program will inspect the export and display a summary.

Example:

```text
Export summary
Posts in export:       109
Public posts:          8
Public MP4 videos:     7
Other public posts:    1
Private posts:         not included
```

The numbers above are an example and depend on your export.

### Choosing Videos

You will see a numbered list of public videos.

Choose one of these options:

- `A` — Download all public videos.
- `S` — Select specific videos.
- `Q` — Quit.

Example:

```text
Your choice [A/S/Q]: S

Enter video numbers separated by commas: 1,3,5
```

This downloads videos 1, 3, and 5.

### Download Location

Downloaded videos are saved automatically in:

```text
downloads/
    your_username/
        001_2026-01-01.mp4
        002_2026-01-02.mp4
        003_2026-01-03.mp4
        download_report.csv
```

The actual filenames depend on the dates in your export.

The CSV report contains download status and information about each selected video.

### Troubleshooting

#### HTTP 403

TikTok may reject an old or expired download link.

Try requesting a fresh TikTok data export and running the program again.

#### No public videos found

Check that:

- You downloaded your TikTok data export.
- The ZIP file is valid.
- Your export contains posts marked as `Everyone`.
- The export includes video download links.

#### File not found

Check the ZIP file path you entered.

On Android, make sure you ran:

```bash
termux-setup-storage
```

#### Missing Python dependency

Run:

```bash
python -m pip install -r requirements.txt
```

### Privacy and Limitations

- The program does not request your TikTok password.
- It does not log in to TikTok.
- It does not scrape TikTok profiles by username.
- It does not bypass account privacy.
- It downloads only videos marked as public in your export.
- Your ZIP file is read locally and is not uploaded to a server.
- It does not automatically publish videos to Instagram.
- TikTok may change its export format or download links.

Use this tool only with data and videos you are authorized to access.

### Dependencies

- Python
- Requests

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

This is the main documentation page that visitors see when they open the repository.
