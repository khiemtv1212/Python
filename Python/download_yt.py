import yt_dlp
url = input("Enter video url: ")

ydl_otps = {}

with yt_dlp.YoutubeDL(ydl_otps) as ydl:
    ydl.download([url])

print("Video download successfully")