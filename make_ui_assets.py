"""Small original high-DPI control glyphs for the desktop theme."""
from pathlib import Path
from PIL import Image, ImageDraw
root = Path(__file__).parent
im = Image.new('RGBA', (48, 48))
d = ImageDraw.Draw(im)
d.line([(10, 24), (20, 34), (38, 13)], fill='#10392b', width=6, joint='curve')
im.resize((18, 18), Image.Resampling.LANCZOS).save(root / 'check.png')
im = Image.new('RGBA', (32, 32))
d = ImageDraw.Draw(im)
d.line([(7, 11), (16, 20), (25, 11)], fill='#a6b7d0', width=3, joint='curve')
im.resize((14, 14), Image.Resampling.LANCZOS).save(root / 'chevron.png')
