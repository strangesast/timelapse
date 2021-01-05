from pathlib import Path
from datetime import datetime
import subprocess
import threading
import asyncio
import os


async def capture_img(imgs_path: Path):
    try:
        roi = [0, 0.4, 1, 1]
        img_path = imgs_path / 'last.png'

        dt = datetime.now()
        args = ['/opt/vc/bin/raspistill', '-roi', ','.join(map(str, roi)), '-o', str(img_path)]
        process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE)
        await process.wait()

        target_path = imgs_path / 'img_{:%Y-%m-%d %H:%M:%S}.png'.format(dt)
        img_path.rename(target_path)
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

