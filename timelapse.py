from pathlib import Path
from datetime import datetime
from PIL import Image, ImageStat
from asyncio.subprocess import PIPE
import subprocess
import threading
import asyncio
import os

THRESHOLD = 78


def brightness(image_file):
   im = Image.open(image_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.mean[0]


async def run_command(args, **kwargs):
    process = await asyncio.create_subprocess_exec(*args, **kwargs, stdout=PIPE, stderr=PIPE)
    await process.wait()


async def capture_img(imgs_path: Path):
    try:
        roi = [0, 0.4, 1, 1]
        jpg_path = imgs_path / 'last.jpg'

        dt = datetime.now()
        args = ['/opt/vc/bin/raspistill', '-roi', ','.join(map(str, roi)), '-o', str(jpg_path)]
        await run_command(args, cwd=imgs_path)

        b = brightness(jpg_path)
        if b < THRESHOLD:
            jpg_path.unlink()
            return

        webp_path = imgs_path / (jpg_path.stem + '.webp')
        args = ['cwebp', str(jpg_path), '-o', str(webp_path)]
        await run_command(args, cwd=imgs_path)

        # annotation
        #args = ['convert', str(webp_path), '-gravity', 'SouthEast', '-fill', 'white', '-pointsize', '100', '-annotate', '0', dt.strftime('%Y/%m/%d %H:%M:%S'), str(webp_path)]
        #await run_command(args)

        target_path = imgs_path / 'img{:%Y-%m-%d_%H:%M:%S}.webp'.format(dt)
        webp_path.rename(target_path)

        frame_path = imgs_path / (target_path.stem + '_frame.webp')
        args = ['cwebp', '-resize', '480', '0', str(target_path), '-o', str(frame_path)]
        await run_command(args, cwd=imgs_path)

        imgs = list(imgs_path.glob('*_frame.webp'))
        timelapse_path = imgs_path / 'timelapse.mp4'
        if not timelapse_path.is_file() or len(imgs) % 5 == 0:
            next_timelapse_path = imgs_path / 'next_timelapse.mp4'
            args = ['ffmpeg', '-y', '-pattern_type', 'glob', '-i', '*_frame.webp', str(next_timelapse_path.resolve())]
            await run_command(args, cwd=imgs_path)

            if next_timelapse_path.is_file():
                next_timelapse_path.rename(timelapse_path)

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

