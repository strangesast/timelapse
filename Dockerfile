from python:slim
run apt-get update && \
    apt-get install -y ffmpeg imagemagick && \
    rm -rf /var/lib/apt/lists/*
workdir /usr/src/app
copy timelapse.py .
cmd ["python3", "timelapse.py"]
