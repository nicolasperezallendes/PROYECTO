import sys, os, glob
from PIL import Image
for f in glob.glob(os.path.join(sys.argv[1], '*.raw.png')):
    im = Image.open(f).convert('RGB')
    out = f.replace('.raw.png', '.png')
    im.save(out, dpi=(200, 200), optimize=True)
    os.remove(f)
    print(os.path.basename(out), im.size, os.path.getsize(out) // 1024 // 1024, 'MB')
