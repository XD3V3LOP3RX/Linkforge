"""Generate an original interlocking-link / download logo and Windows icon."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).parent
im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((8, 8, 248, 248), radius=58, fill='#192235')
d.rounded_rectangle((52, 65, 147, 139), radius=32, outline='#67e8c2', width=17)
d.rounded_rectangle((109, 108, 204, 182), radius=32, outline='#77a8ff', width=17)
d.line((106, 127, 151, 127), fill='#eef3ff', width=13)
d.line((139, 115, 153, 127, 139, 139), fill='#eef3ff', width=10, joint='curve')
im.save(root / 'logo.png')
im.save(root / 'logo.ico', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
