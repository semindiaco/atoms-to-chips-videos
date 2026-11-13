from PIL import Image, ImageDraw, ImageFont
import math
F="/usr/share/fonts/opentype/inter/"
BG=(8,14,26); GRID=(16,28,46); CYAN=(56,205,230); AMBER=(255,176,59); WHITE=(238,244,250); MUTED=(140,160,185)
def font(w,s): return ImageFont.truetype(F+f"Inter-{w}.otf",s)
def mark(d,cx,cy,r,lw=None):
    """Atom (left) flowing into chip (right) inside a size-r box."""
    lw=lw or max(2,int(r*0.05))
    # chip: square with pins on right half
    cs=r*0.9; x0=cx+r*0.05; y0=cy-cs/2
    d.rounded_rectangle([x0,y0,x0+cs,y0+cs],radius=cs*0.12,outline=CYAN,width=lw)
    n=4; 
    for i in range(n):
        p=y0+cs*(i+1)/(n+1)
        d.line([(x0+cs,p),(x0+cs+r*0.18,p)],fill=CYAN,width=lw)
        px=x0+cs*(i+1)/(n+1)
        d.line([(px,y0),(px,y0-r*0.18)],fill=CYAN,width=lw)
        d.line([(px,y0+cs),(px,y0+cs+r*0.18)],fill=CYAN,width=lw)
    # inner die
    m=cs*0.3; d.rectangle([x0+m,y0+m,x0+cs-m,y0+cs-m],fill=CYAN)
    # atom on left, overlapping chip's left edge
    ax=cx-r*0.45; ay=cy; R=r*0.62
    for ang in (-35,35):
        pts=[]
        for t in range(0,361,4):
            a=math.radians(t); x=R*math.cos(a); y=R*0.36*math.sin(a)
            th=math.radians(ang); pts.append((ax+x*math.cos(th)-y*math.sin(th), ay+x*math.sin(th)+y*math.cos(th)))
        d.line(pts,fill=AMBER,width=lw)
    d.ellipse([ax-r*0.11,ay-r*0.11,ax+r*0.11,ay+r*0.11],fill=AMBER)
    # electrons on orbits
    for ang,t in ((-35,40),(35,220)):
        a=math.radians(t); x=R*math.cos(a); y=R*0.36*math.sin(a); th=math.radians(ang)
        ex=ax+x*math.cos(th)-y*math.sin(th); ey=ay+x*math.sin(th)+y*math.cos(th)
        d.ellipse([ex-r*0.07,ey-r*0.07,ex+r*0.07,ey+r*0.07],fill=WHITE)
def grid(d,W,H,step):
    for i in range(0,W,step): d.line([(i,0),(i,H)],fill=GRID,width=1)
    for j in range(0,H,step): d.line([(0,j),(W,j)],fill=GRID,width=1)
