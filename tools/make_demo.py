"""Scripted real-Qt-widget demo with benign example links; never a desktop recording.

Run from the repository: python tools/make_demo.py --ffmpeg path/to/ffmpeg
DLC opening needs internet. The video is silent and uses only original artwork.
"""
import argparse
from dataclasses import dataclass
import io
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtTest import QTest
import qt_app

WIDTH, HEIGHT, FPS = 1600, 1080, 12
APP_X, APP_Y = 80, 96


def font(size, bold=False):
    directory = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    path = directory / ('segoeuib.ttf' if bold else 'segoeui.ttf')
    if path.is_file():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype('DejaVuSans.ttf', size)


def widget_image(widget):
    from PySide6.QtCore import QBuffer, QIODevice
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    widget.grab().save(buffer, 'PNG')
    return Image.open(io.BytesIO(bytes(buffer.data()))).convert('RGB')


def capture(window, popup=None):
    QApplication.processEvents()
    image = widget_image(window)
    if popup is not None:
        position = window.mapFromGlobal(popup.mapToGlobal(QPoint(0, 0)))
        image.paste(widget_image(popup), (position.x(), position.y()))
    return image


def wait_worker(window, timeout=80):
    deadline = time.monotonic() + timeout
    while window.is_busy() and time.monotonic() < deadline:
        QApplication.processEvents()
        QTest.qWait(25)
    QApplication.processEvents()
    if window.is_busy():
        raise RuntimeError('The DLC key service did not finish in time.')


@dataclass
class Shot:
    title: str
    image: Image.Image
    seconds: float
    focus: tuple | None = None


def title_card(title, subtitle):
    image = Image.new('RGB', (WIDTH, HEIGHT), '#0b1019')
    draw = ImageDraw.Draw(image)
    logo = Image.open(ROOT / 'logo.png').convert('RGBA').resize((152, 152))
    image.paste(logo, ((WIDTH - 152) // 2, 280), logo)
    draw.text((WIDTH // 2, 505), title, font=font(57, True), fill='#eef4fc', anchor='mm')
    draw.text((WIDTH // 2, 585), subtitle, font=font(27), fill='#94a8c5', anchor='mm')
    draw.text((WIDTH // 2, 940), 'WINDOWS DESKTOP  /  LINKFORGE STUDIO 2.1.2', font=font(17, True), fill='#77dfb9', anchor='mm')
    return image


def frame_for(shot, cursor=None):
    if shot.image.size == (WIDTH, HEIGHT):
        return shot.image.copy()
    image = Image.new('RGB', (WIDTH, HEIGHT), '#0b1019')
    image.paste(shot.image, (APP_X, APP_Y))
    draw = ImageDraw.Draw(image)
    draw.text((APP_X, 35), 'LINKFORGE STUDIO', font=font(19, True), fill='#78dfbb')
    draw.text((WIDTH - APP_X, 35), 'PRODUCT DEMO', font=font(16), fill='#8094af', anchor='ra')
    draw.text((APP_X, 1002), shot.title, font=font(29, True), fill='#eff5fc')
    draw.text((WIDTH - APP_X, 1048), 'Illustrative sample links • no hosted files downloaded', font=font(16), fill='#8a9db7', anchor='ra')
    if cursor:
        x, y = cursor
        draw.ellipse((x - 16, y - 16, x + 16, y + 16), outline='#72e0b9', width=2)
        draw.polygon([(x, y), (x + 2, y + 24), (x + 8, y + 17), (x + 15, y + 28),
                      (x + 20, y + 25), (x + 13, y + 14), (x + 23, y + 13)], fill='#f0f5fc', outline='#101722')
    return image


def make_shots(window, media, working):
    from PySide6.QtCore import QTimer
    shots = [Shot('', title_card('LinkForge Studio', 'Containers in. Clean links out.'), 1.5)]
    capture(window).save(media / 'empty.png')
    shots.append(Shot('Start with a clean collection', capture(window), 2.0, (APP_X + 900, APP_Y + 250)))
    window.import_paths([str(ROOT / 'examples' / 'sample-links.txt')])
    shots.append(Shot('Import TXT / CSV—or paste your links', capture(window), 3.5, (APP_X + 1030, APP_Y + 250)))
    window.search.setText('update')
    window.model.setData(window.model.index(2, 0), 'Sample update v2 [Reviewed].zip')
    capture(window).save(media / 'search.png')
    shots.append(Shot('Find a link. Give it a recognizable name.', capture(window), 3.0, (APP_X + 420, APP_Y + 250)))
    window.search.clear()
    QApplication.processEvents()
    index = window.proxy.index(0, 3)
    point = window.table.visualRect(index).center()
    holder = []
    def grab_context():
        menu = QApplication.activePopupWidget()
        if menu:
            position = window.mapFromGlobal(window.table.viewport().mapToGlobal(point))
            position.setX(min(position.x(), window.width() - menu.width() - 12))
            menu.move(window.mapToGlobal(position))
            holder.append(capture(window, menu))
            menu.close()
    QTimer.singleShot(80, grab_context)
    window.link_menu(point)
    if holder:
        holder[0].save(media / 'link-actions.png')
        shots.append(Shot('Click to open. Right-click to copy the original URL.', holder[0], 3.0,
                          (APP_X + window.table.x() + point.x(), APP_Y + 350)))
    window.model.replace([])
    window.import_paths([str(ROOT / 'examples' / 'demo.dlc')])
    wait_worker(window)
    if len(window.model.entries) != 3 or set(window.model.package_names) != {'Demo collection'}:
        raise RuntimeError('The example DLC failed to import correctly.')
    capture(window).save(media / 'overview.png')
    shots.append(Shot('Open a DLC. Recover filenames and package names.', capture(window), 4.0,
                      (APP_X + 570, APP_Y + 355)))
    menu = window.export_button.menu()
    location = window.export_button.mapToGlobal(QPoint(0, -menu.sizeHint().height()))
    menu.popup(location)
    menu.move(location)
    QTest.qWait(60)
    export_image = capture(window, menu)
    export_image.save(media / 'export.png')
    menu.hide()
    shots.append(Shot('Export your collection as CSV or plain TXT', export_image, 3.5,
                      (APP_X + 1300, APP_Y + 720)))
    for kind in ('csv', 'txt'):
        destination = working / ('extracted-links.' + kind)
        with patch.object(window, 'choose_output', return_value=str(destination)):
            menu.actions()[0 if kind == 'csv' else 1].trigger()
        if not destination.is_file():
            raise RuntimeError('Export action did not create its output.')
    assert qt_app.core.read_entries(working / 'extracted-links.csv') == window.selected_entries()
    assert (working / 'extracted-links.txt').read_text(encoding='utf-8').splitlines() == [u for u, _ in window.selected_entries()]
    shots.append(Shot('Names in CSV. One URL per line in TXT.', capture(window), 2.5,
                      (APP_X + 1300, APP_Y + 750)))
    shots.append(Shot('', title_card('Import. Organize. Export.', 'LinkForge Studio 2.1.2 • Windows'), 1.5))
    return shots


def render(shots, media, working, ffmpeg):
    frames = working / 'frames'
    frames.mkdir()
    previous = None
    frame_number = 0
    cursor = (WIDTH * 0.65, HEIGHT * 0.5)
    for shot in shots:
        count = round(shot.seconds * FPS)
        start = cursor
        for n in range(count):
            if shot.focus:
                fraction = min(1.0, n / (FPS * 0.7))
                eased = 0.5 - 0.5 * math.cos(math.pi * fraction)
                cursor = (round(start[0] + (shot.focus[0] - start[0]) * eased),
                          round(start[1] + (shot.focus[1] - start[1]) * eased))
            frame = frame_for(shot, cursor if shot.focus else None)
            if previous is not None and n < 3:
                frame = Image.blend(previous, frame, (n + 1) / 3)
            frame.save(frames / f'frame{frame_number:05d}.png')
            frame_number += 1
        previous = frame
    subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(frames / 'frame%05d.png'),
                    '-vf', 'fps=30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-metadata', 'title=LinkForge Studio product demo',
                    str(media / 'demo.mp4')], check=True)
    subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', str(media / 'demo.mp4'),
                    '-filter_complex', 'fps=8,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer',
                    '-loop', '0', str(media / 'demo.gif')], check=True)
    subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', str(media / 'demo.mp4'),
                    '-vf', "select='not(mod(n,120))',scale=480:-1", '-vsync', 'vfr', str(working / 'contact-%02d.png')], check=True)
    thumbs = sorted(working.glob('contact-*.png'))
    sheet = Image.new('RGB', (480 * 3, 350 * math.ceil(len(thumbs) / 3)), '#0b1019')
    draw = ImageDraw.Draw(sheet)
    for number, path in enumerate(thumbs):
        image = Image.open(path).convert('RGB')
        x, y = (number % 3) * 480, (number // 3) * 350
        sheet.paste(image, (x, y))
        draw.text((x + 12, y + 324), f'{number * 4:02d}s', font=font(17), fill='#d9e5f3')
    sheet.save(media / 'contact-sheet.png')
    import json
    (media / 'demo.json').write_text(json.dumps({'duration_seconds': frame_number / FPS,
        'size': [WIDTH, HEIGHT], 'silent': True, 'capture': 'Scripted real Qt widgets, not a desktop recording',
        'data': 'Benign placeholder example.com/org/net URLs only', 'cursor': 'Presentation overlay',
        'stages': [shot.title for shot in shots if shot.title]}, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default=shutil.which('ffmpeg'))
    arguments = parser.parse_args()
    if not arguments.ffmpeg:
        parser.error('Install ffmpeg locally or pass --ffmpeg with its executable path.')
    app = QApplication.instance() or QApplication([])
    app.setStyle('Fusion')
    directory = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    for name in ('segoeui.ttf', 'segoeuib.ttf'):
        if (directory / name).is_file():
            QFontDatabase.addApplicationFont(str(directory / name))
    app.setStyleSheet(qt_app.STYLE.replace('CHECK_PATH', (ROOT / 'check.png').as_posix()).replace('CHEVRON_PATH', (ROOT / 'chevron.png').as_posix()))
    media = ROOT / 'media'
    media.mkdir(exist_ok=True)
    window = qt_app.MainWindow()
    window.resize(1440, 850)
    window.show()
    QApplication.processEvents()
    with tempfile.TemporaryDirectory(prefix='linkforge-demo-') as folder:
        working = Path(folder)
        shots = make_shots(window, media, working)
        render(shots, media, working, arguments.ffmpeg)
    window.close()
    print('Created media/demo.mp4, demo.gif, screenshots, and contact-sheet.png', flush=True)


if __name__ == '__main__':
    main()
