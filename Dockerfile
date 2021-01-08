from python:slim
run apt-get update && \
    apt-get install -y \
      build-essential \
      ffmpeg \
      imagemagick \
      wget \
      libjpeg-dev libpng-dev libtiff-dev libgif-dev && \
    python3 -m pip install Pillow && \
    rm -rf /var/lib/apt/lists/*

run cd /tmp && \
  wget -P /tmp https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.1.0.tar.gz && \
  tar xf libwebp-1.1.0.tar.gz && \
  cd libwebp-1.1.0/ && \
  ./configure --enable-everything && \
  make && \
  make install && \
  ldconfig

workdir /usr/src/app
copy timelapse.py .
cmd ["python3", "timelapse.py"]
