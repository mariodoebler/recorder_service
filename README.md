# Recorder Service
## Setup
Change arguments inside `recorder/Dockerfile`. You can change the root directory, the video file path, and the number of frames to save.

```docker compose build```

Place video file inside the created docker volume `storage`.
## Run
```docker compose up -d```
### Send HTTP Post via command line (Windows)
```curl -X POST -H "Content-Type: application/json" -d "{\"product\":\"apple\", \"weight\":200}" http://localhost:8000/save_frames```
