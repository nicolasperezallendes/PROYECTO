import math, os, io, time, requests
from PIL import Image
H={'User-Agent':'mapa-establecimientos-coquimbo/1.0 (perez.allendes.sociologo)'}
def ll2px(lat,lon,z,ts=256):
    n=2**z*ts
    x=(lon+180)/360*n
    s=math.sin(math.radians(lat))
    y=(0.5-math.log((1+s)/(1-s))/(4*math.pi))*n
    return x,y
def tile(z,x,y,style='osm'):
    p=f'osmtiles/{style}_{z}_{x}_{y}.png'
    if not os.path.exists(p):
        for t in range(5):
            try:
                r=requests.get(f'https://tile.openstreetmap.org/{z}/{x}/{y}.png',headers=H,timeout=30)
                if r.ok: open(p,'wb').write(r.content); break
            except Exception as e: pass
            time.sleep(2*(t+1))
        time.sleep(0.15)
    return Image.open(p).convert('RGB')
def mosaic(lat_c,lon_c,z,W,H_,style='osm'):
    """Return image W x H_ (pixels at 512 tile size), centered; and a projector fn."""
    ts=256
    cx,cy=ll2px(lat_c,lon_c,z,ts)
    x0,y0=cx-W/2,cy-H_/2
    img=Image.new('RGB',(int(W),int(H_)))
    for tx in range(int(x0//ts),int((x0+W)//ts)+1):
        for ty in range(int(y0//ts),int((y0+H_)//ts)+1):
            img.paste(tile(z,tx,ty,style),(int(tx*ts-x0),int(ty*ts-y0)))
    def proj(lat,lon):
        x,y=ll2px(lat,lon,z,ts); return x-x0,y-y0
    return img,proj
