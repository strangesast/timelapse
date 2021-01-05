from python:slim
workdir /usr/src/app
copy timelapse.py .
cmd ["python3", "timelapse.py"]
