from pathlib import Path
from datetime import datetime
from asyncio.subprocess import PIPE
import subprocess
import threading
import asyncio
import os


async def capture_img(imgs_path: Path):
    try:
        roi = [0, 0.4, 1, 1]
        img_path = imgs_path / 'last.jpg'

        dt = datetime.now()
        args = ['/opt/vc/bin/raspistill', '-roi', ','.join(map(str, roi)), '-o', str(img_path)]
        process = await asyncio.create_subprocess_exec(*args, stdout=PIPE, stderr=PIPE)
        ret = await process.wait()

        target_path = imgs_path / 'img{:%Y-%m-%d_%H:%M:%S}.jpg'.format(dt)
        img_path.rename(target_path)

        imgs = list(imgs_path.glob('*.jpg'))
        if len(imgs) % 5 == 0:
            args = ['ffmpeg', '-y', '-pattern_type', 'glob', '-i', '*.jpg', '-vf', 'scale=480:320', 'timelapse.mp4']
            process = await asyncio.create_subprocess_exec(*args, cwd=imgs_path, stdout=PIPE, stderr=PIPE)
            stdout, stderr = await process.communicate()
            ret = process.returncode
            if ret != 0:
                print('stderr', stderr)
                print('stdout', stdout)

    except asyncio.CancelledError:
        process.terminate()
        await process.wait()


async def main(imgs_path: Path, interval: int):
    if not imgs_path.is_dir():
        imgs_path.mkdir()

    while True:
        task = await asyncio.gather(capture_img(imgs_path), asyncio.sleep(interval))


if __name__ == '__main__':
    s = os.environ.get('IMGS_PATH')
    imgs_path = Path(s).resolve() if s else (Path.cwd() / 'imgs')

    s = os.environ.get('INTERVAL')
    interval = int(s) if s else 60

    try:
        asyncio.run(main(imgs_path, interval))
    except KeyboardInterrupt:
        pass

