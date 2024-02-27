FROM --platform=$BUILDPLATFORM python:3.10-slim AS builder

WORKDIR /recorder

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt /recorder
RUN pip3 install -r requirements.txt

COPY . /recorder

ENTRYPOINT ["python3"]
CMD ["recorder_service.py", "--root", "/storage", "--video", "/storage/video.mkv", "--num_frames", "5"]
