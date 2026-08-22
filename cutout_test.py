# -*- coding: utf-8 -*-
import os, io, base64, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from rembg import remove, new_session

FT=os.environ.get("FONT_DIR","fonts")
def F(sz,w="Bold"): return ImageFont.truetype(os.path.join(FT,"Poppins-%s.ttf"%w),int(sz))
W,H=1080,1350
RED=(200,32,38); YEL=(247,193,30); WHITE=(255,255,255)

def cover(im,w,h):
    im=im.convert("RGB"); s=max(w/im.width,h/im.height)
    im=im.resize((int(im.width*s)+1,int(im.height*s)+1))
    x=(im.width-w)//2; y=(im.height-h)//2
    return im.crop((x,y,x+w,y+h))

def fetch(uid):
    url="https://images.unsplash.com/photo-%s?w=1200&q=80"%uid
    d=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
    return Image.open(io.BytesIO(d)).convert("RGB")

def wrap(d,t,f,mw):
    out=[];c=""
    for w in t.split():
        s=(c+" "+w).strip()
        if d.textlength(s,font=f)<=mw:c=s
        else:
            if c:out.append(c)
            c=w
    if c:out.append(c)
    return out

# 1) load product photo
prod=Image.open(io.BytesIO(base64.b64decode(open("assets/wine.b64").read()))).convert("RGB")
# 2) cutout
cut=remove(prod, session=new_session("u2net"))
bb=cut.getbbox(); cut=cut.crop(bb)
print("cutout size", cut.size)

# 3) background (people, lifestyle)
bg=cover(fetch("1682071308594-2aaa701015ef"),W,H)
bg=bg.filter(ImageFilter.GaussianBlur(9))
im=bg.convert("RGBA")
im.alpha_composite(Image.new("RGBA",(W,H),(10,8,10,120)))
# warm red glow bottom
glow=Image.new("L",(W,H),0); gd=ImageDraw.Draw(glow); gd.ellipse([int(W*0.1),int(H*0.55),int(W*0.9),int(H*1.15)],fill=90)
glow=glow.filter(ImageFilter.GaussianBlur(140)); im=Image.composite(Image.new("RGBA",(W,H),RED+(255,)),im,glow)

# 4) place product cutout (shadow + bottle)
th=int(H*0.66); s=th/cut.height; cw=int(cut.width*s)
cutR=cut.resize((cw,th))
px=(W-cw)//2; py=H-th-int(H*0.10)
# soft shadow
sh=Image.new("RGBA",(W,H),(0,0,0,0)); a=cutR.split()[3].point(lambda v:int(v*0.55))
shim=Image.new("RGBA",(cw,th),(0,0,0,255)); shim.putalpha(a)
sh.alpha_composite(shim,(px+18,py+22)); sh=sh.filter(ImageFilter.GaussianBlur(18)); im.alpha_composite(sh)
im.alpha_composite(cutR,(px,py))

d=ImageDraw.Draw(im,"RGBA")
# 5) phrase top
title="Un vinito para hoy?"
ts=int(W*0.088); tl=wrap(d,title,F(ts),int(W*0.86))
y=int(H*0.10)
d.rectangle([int(W*0.07),y-int(W*0.03),int(W*0.07)+int(W*0.12),y-int(W*0.03)+int(W*0.012)],fill=YEL)
for ln in tl:
    d.text((int(W*0.07)+2,y+2),ln,font=F(ts),fill=(0,0,0,120))
    d.text((int(W*0.07),y),ln,font=F(ts),fill=WHITE); y+=int(ts*1.06)
# 6) LH logo pill top-right
txt="LAURITA HNOS."; tf=F(int(W*0.026)); bs=int(W*0.066)
tw=d.textlength(txt,font=tf); padx=int(W*0.022); gap=int(W*0.015)
pw=padx+bs+gap+tw+padx; ph=int(bs*1.3); lx=W-pw-int(W*0.05); ly=int(H*0.045)
d.rounded_rectangle([lx,ly,lx+pw,ly+ph],radius=ph//2,fill=(24,24,28,235))
by=ly+(ph-bs)//2
d.rounded_rectangle([lx+padx,by,lx+padx+bs,by+bs],radius=int(bs*0.28),fill=RED)
lf=F(int(bs*0.5)); lw=d.textlength("LH",font=lf); d.text((lx+padx+(bs-lw)/2,by+int(bs*0.22)),"LH",font=lf,fill=WHITE)
d.text((lx+padx+bs+gap,ly+(ph-tf.size)//2-2),txt,font=tf,fill=WHITE)

os.makedirs("output",exist_ok=True)
im.convert("RGB").save("output/wine_test.jpg","JPEG",quality=90)
print("DONE output/wine_test.jpg")
