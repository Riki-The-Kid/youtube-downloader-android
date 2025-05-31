[app]
title = YouTube Downloader
package.name = youtubedownloader  
package.domain = com.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.1.0,yt-dlp,certifi,charset-normalizer,idna,requests,urllib3,websockets,brotli,mutagen,pycryptodomex

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21 
android.sdk = 31
android.ndk = 23b
android.accept_sdk_license = True
android.gradle_dependencies = 
android.arch = arm64-v8a
