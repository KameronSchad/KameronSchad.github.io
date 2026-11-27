#!/usr/bin/env python3
"""Render the rocket showcase from its original film, CAD and solved CFD.

No new flow solution is calculated. Tracers follow projected steady velocities;
time is uniformly slowed. The original v5 construction footage is retained.
"""
from pathlib import Path
import base64, json, math, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'
SRC=A/'rocket-cfd-build-v5.mp4'
OUT=A/'rocket-cfd-build-v6.mp4'
POSTER=A/'rocket-cfd-build-v6-poster.webp'
NAMES=['biconic','hemisphere','blunt']
X0,X1,Z0,Z1=-7.,5.,-2.35,2.35
FPS=30
RNG=np.random.default_rng(20261126)
cap=cv2.VideoCapture(str(SRC))
if not cap.isOpened(): raise RuntimeError('Cannot open original film')
W,H=int(cap.get(3)),int(cap.get(4))
SRC_FPS=cap.get(cv2.CAP_PROP_FPS)
assert W>=1000 and H>=700 and SRC_FPS>0, (W,H,SRC_FPS)
FX=round(W*.045); FW=W-2*FX
S=FW/12; CY=round(H*.47); FH=round(4.7*S); FY=round(CY-FH/2)
TAIL=FX-X0*S
FONTS='/usr/share/fonts/truetype/dejavu/'
def font(n,bold=False):
    return ImageFont.truetype(FONTS+('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),max(12,round(n*W/1408)))
def smooth(t): 
    t=np.clip(t,0,1); return float(t*t*(3-2*t))
def xy(x,z): return np.asarray([FX+(x-X0)*S,CY-z*S])
def source_mask(f):
    # Isolate CAD in the central stage; exclude the fixed caption and film HUD.
    v=f.max(axis=2)
    m=(v>65).astype('uint8')
    m[:round(H*.09)]=0; m[round(H*.87):]=0
    m[:,:round(W*.13)]=0; m[:,round(W*.87):]=0
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,l,stats,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    if n<2: return np.zeros((H,W),np.uint8)
    i=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
    return (l==i).astype('uint8')
def measure(f):
    m=source_mask(f); y,x=np.nonzero(m)
    if len(x)<100: return None
    cov=np.cov(x,y); _,v=np.linalg.eigh(cov); a=v[:,-1]
    angle=math.degrees(math.atan2(abs(a[0]),abs(a[1])))
    return (len(x),x.min(),y.min(),x.max(),y.max(),angle)
def neutral(f):
    # Change filled surfaces only: narrow CAD sketch lines retain their original color.
    m=(f.max(axis=2)>65).astype('uint8')
    m[:round(H*.09)]=0; m[round(H*.87):]=0
    m[:,:round(W*.13)]=0; m[:,round(W*.87):]=0
    interior=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    alpha=cv2.GaussianBlur(interior.astype(np.float32),(5,5),0)[...,None]
    # One silver-blue material; retain the original per-pixel specular shading.
    hi=f.max(axis=2).astype(np.float32)
    material=np.clip(hi[...,None]*np.array([1.,.94,.85]),0,255)
    return np.uint8(np.clip(f*(1-alpha)+material*alpha,0,255))
# Detect the last completed upright pose before the original rotation.
# A later horizontal CFD shot cannot pass the aspect and PCA criteria.
stats=[]
limit=min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),math.ceil(10*SRC_FPS))
for i in range(limit):
    ok,f=cap.read()
    if not ok: break
    if i%2==0:
        q=measure(f)
        if q: stats.append((i,q))
candidates=[(i,q) for i,q in stats if q[0]>.018*W*H and q[4]-q[2]>.48*H and q[3]-q[1]<.42*(q[4]-q[2]) and q[5]<1.7]
if not candidates: raise RuntimeError('No completed upright pose detected; original video left unchanged')
maxarea=max(q[0] for _,q in candidates)
good=[(i,q) for i,q in candidates if q[0]>.90*maxarea]
cut,q=good[-1]
if cut/SRC_FPS<1.5 or cut/SRC_FPS>9.5: raise RuntimeError('Unexpected construction timing')
print('Original upright pose:',cut/SRC_FPS,q,flush=True)
cap.set(cv2.CAP_PROP_POS_FRAMES,cut)
ok,raw=cap.read()
if not ok: raise RuntimeError('Cannot extract upright pose')
last=neutral(raw)
mask=source_mask(raw)
ys,xs=np.nonzero(mask); box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
x0,y0,x1,y1=box
# Reconstruct the subtle original background from pixels outside the CAD and captions.
yy,xx=np.mgrid[:H,:W]; r2=((xx-W/2)/W)**2+((yy-H/2)/H)**2
sample=(mask==0)&(yy<H*.85)&(xx>W*.03)&(xx<W*.97)&(raw.max(2)<60)
fit=np.column_stack([np.ones(sample[::12,::12].sum()),r2[::12,::12][sample[::12,::12]],r2[::12,::12][sample[::12,::12]]**2])
coeff=np.linalg.lstsq(fit,raw[::12,::12][sample[::12,::12]],rcond=None)[0]
bg=np.uint8(np.clip(coeff[0]+r2[...,None]*coeff[1]+r2[...,None]**2*coeff[2],0,255))
# Transparent, premultiplied crop from the original film.
crop_a=mask[y0:y1,x0:x1].astype(np.float32)
crop_a=cv2.GaussianBlur(crop_a,(3,3),.5)
crop=last[y0:y1,x0:x1].astype(np.float32)*crop_a[...,None]
def glb(path):
    b=path.read_bytes(); n=int.from_bytes(b[12:16],'little')
    j=json.loads(b[20:20+n]); start=20+n+8
    def acc(i):
        a=j['accessors'][i]; v=j['bufferViews'][a['bufferView']]
        d={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
        cols=3 if a['type']=='VEC3' else 1
        stride=v.get('byteStride',np.dtype(d).itemsize*cols)
        return np.ndarray((a['count'],cols),dtype=d,buffer=b,offset=start+v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(d).itemsize)).copy()
    for name in ('Rocket body','Nose cone'):
        node=next(v for v in j['nodes'] if v.get('name') in (name,name.replace(' ','_')))
        assert not any(k in node for k in ('matrix','translation','rotation','scale'))
        p=j['meshes'][node['mesh']]['primitives'][0]
        yield acc(p['attributes']['POSITION']),acc(p['attributes']['NORMAL']),acc(p['indices']).ravel()
def raster(name):
    # Exact common orthographic mapping from STEP-derived geometry into CFD pixels.
    # One shared depth buffer and one material for both parts.
    dep=np.full((H,W),-np.inf,np.float32)
    rgb=np.zeros((H,W,3),np.float32)
    for p,n,idx in glb(A/'models'/'rocket'/(name+'.glb')):
        xyz=np.column_stack([TAIL-p[:,1]/.0254*S,CY-p[:,2]/.0254*S,-p[:,0]/.0254])
        for tri in idx.reshape(-1,3):
            a,b,c=xyz[tri]; dx=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(dx)<1e-6: continue
            left=max(0,int(np.floor(min(a[0],b[0],c[0]))));right=min(W-1,int(np.ceil(max(a[0],b[0],c[0]))))
            top=max(0,int(np.floor(min(a[1],b[1],c[1]))));bottom=min(H-1,int(np.ceil(max(a[1],b[1],c[1]))))
            if left>right or top>bottom: continue
            Y,X=np.mgrid[top:bottom+1,left:right+1];X=X+.5;Y=Y+.5
            u=((b[1]-c[1])*(X-c[0])+(c[0]-b[0])*(Y-c[1]))/dx
            v=((c[1]-a[1])*(X-c[0])+(a[0]-c[0])*(Y-c[1]))/dx
            k=1-u-v; z=u*a[2]+v*b[2]+k*c[2]
            d=dep[top:bottom+1,left:right+1]; keep=(u>=-.0001)&(v>=-.0001)&(k>=-.0001)&(z>d)
            if not keep.any(): continue
            nn=u[keep,None]*n[tri[0]]+v[keep,None]*n[tri[1]]+k[keep,None]*n[tri[2]]
            nn/=np.maximum(1e-6,np.linalg.norm(nn,axis=1,keepdims=True))
            lit=np.maximum(0,nn@np.array([-.76,.20,.62])); rim=np.maximum(0,nn@np.array([.26,-.28,.91]));gloss=np.maximum(0,nn@np.array([-.93,.11,.36]))**18
            shade=.48+.60*lit+.13*rim
            rgb[top:bottom+1,left:right+1][keep]=np.minimum(255,shade[:,None]*np.array([220.,207.,187.])+gloss[:,None]*35)
            d[keep]=z[keep]
    m=np.isfinite(dep)
    if m.sum()<.007*W*H: raise RuntimeError('Unexpected CAD projection: '+name)
    return rgb,m
stops=np.array([[0,42,35,177],[400,45,79,238],[850,66,190,250],[1250,112,224,177],[1650,210,195,69],[2112,196,85,31],[2300,126,42,22]],float)
def colors(v): return np.stack([np.interp(v,stops[:,0],stops[:,i]) for i in (1,2,3)],axis=-1)
class Field:
    def __init__(self,name,solid):
        self.name=name; self.solid=solid
        j=json.loads((A/'cfd'/(name+'.json')).read_text());self.nx=j['width'];self.nz=j['height']
        assert j['bounds']==[X0,X1,Z0,Z1]
        self.a=np.frombuffer(base64.b64decode(j['data']),dtype='<i2').reshape(self.nz,self.nx,3).astype(float)
        valid=self.a[:,:,0]!=32767
        self.valid=valid
        val=cv2.resize(np.where(valid,self.a[:,:,0],0),(FW,FH),interpolation=cv2.INTER_LINEAR)
        weight=cv2.resize(valid.astype(np.float32),(FW,FH),interpolation=cv2.INTER_LINEAR)
        col=colors(val/np.maximum(weight,1e-5))
        self.contour=bg.copy()
        b=bg[FY:FY+FH,FX:FX+FW].astype(float)
        a=np.where(weight>.995,.78,0.)[...,None]
        self.contour[FY:FY+FH,FX:FX+FW]=np.uint8(b*(1-a)+col*a)
    def inside(self,p):
        u=np.rint(FX+(p[:,0]-X0)*S).astype(int); v=np.rint(CY-p[:,1]*S).astype(int)
        ok=(u>=0)&(u<W)&(v>=0)&(v<H)
        ret=np.ones(len(p),bool);ret[ok]=self.solid[v[ok],u[ok]]
        return ret
    def velocity(self,p):
        u=(p[:,0]-X0)/12*(self.nx-1);v=(Z1-p[:,1])/4.7*(self.nz-1)
        ok=(u>=0)&(u<self.nx-1)&(v>=0)&(v<self.nz-1)&(~self.inside(p))
        u=np.clip(u,0,self.nx-1.00001);v=np.clip(v,0,self.nz-1.00001)
        i=u.astype(int);j=v.astype(int);a=u-i;b=v-j
        ok &= self.valid[j,i]&self.valid[j,i+1]&self.valid[j+1,i]&self.valid[j+1,i+1]
        vals=(1-b[:,None])*((1-a[:,None])*self.a[j,i]+a[:,None]*self.a[j,i+1])+b[:,None]*((1-a[:,None])*self.a[j+1,i]+a[:,None]*self.a[j+1,i+1])
        return np.column_stack([-vals[:,1],vals[:,2]]),ok
    def seed(self,n,initial=False):
        p=np.column_stack([RNG.uniform(X0+.035,X1-.035 if initial else X0+.25,n),RNG.uniform(Z0+.07,Z1-.07,n)])
        # Denser, still physically advected upstream seeds around the nose centerline.
        near=RNG.random(n)<.24
        p[near,1]=RNG.uniform(-.36,.36,near.sum())
        for _ in range(14):
            _,ok=self.velocity(p)
            if ok.all(): break
            p[~ok,0]=RNG.uniform(X0+.035,X1-.035 if initial else X0+.25,(~ok).sum())
            p[~ok,1]=RNG.uniform(Z0+.07,Z1-.07,(~ok).sum())
        return p
    def streamlines(self):
        canvas=np.zeros((H,W,3),np.uint8)
        seeds=np.unique(np.r_[np.linspace(Z0+.10,Z1-.10,31),np.linspace(-.29,.29,15)])
        for z in seeds:
            p=np.array([[X0+.09,z]]); path=[]
            for _ in range(850):
                v,ok=self.velocity(p); mag=np.linalg.norm(v)
                if not ok[0] or mag<15: break
                path.append(xy(*p[0]))
                mid=p+.018*v/max(mag,1)
                vm,valid=self.velocity(mid)
                if not valid[0]: break
                p=p+.036*vm/max(np.linalg.norm(vm),1)
            if len(path)>2:
                cv2.polylines(canvas,[np.rint(path).astype(np.int32)],False,(47,43,39),1,cv2.LINE_AA)
        canvas[self.solid]=0
        return canvas
def composite(bg,solid,mask,alpha=1):
    out=bg.copy();out[mask]=np.uint8(np.clip(bg[mask]*(1-alpha)+solid[mask]*alpha,0,255));return out
def titles(frame,head,sub,flow=False,name=''):
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(im)
    left=round(W*.029);bottom=round(H*.974)
    d.text((left,bottom-round(H*.048)),head,font=font(24,True),fill=(207,228,233),anchor='la')
    d.text((left,bottom-round(H*.020)),sub,font=font(18),fill=(153,175,188),anchor='la')
    if flow:
        d.text((FX,FY-round(H*.055)),'FREESTREAM  /  120 mph',font=font(19,True),fill=(210,229,237))
        d.text((FX+FW,FY-round(H*.055)),'FLOW  →',font=font(19,True),fill=(153,220,219),anchor='ra')
        ly=FY+FH+round(H*.069);lh=max(8,round(H*.012))
        d.text((FX,ly-round(H*.034)),'VELOCITY MAGNITUDE  /  in/s',font=font(17,True),fill=(210,229,237))
        bar=np.uint8(colors(np.linspace(0,2300,FW))[:,::-1]);bar=np.repeat(bar[None,:,:],lh,axis=0)
        im.paste(Image.fromarray(bar),(FX,ly))
        for v in (0,575,1150,1725,2300):
            x=round(FX+FW*v/2300);d.line((x,ly+lh,x,ly+lh+5),fill=(180,198,210),width=1)
            d.text((x,ly+lh+7),str(v),font=font(15),fill=(180,198,210),anchor='la' if v==0 else 'ra' if v==2300 else 'ma')
    return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)
solids=[raster(n) for n in NAMES]; fields=[Field(n,m) for n,(_,m) in zip(NAMES,solids)]
# The final rotation target uses the exact same bounding box, solid raster, and
# mapping as the CFD phase. No repositioning of the model at the handoff.
s0,m0=solids[0]; y,x=np.nonzero(m0); target=np.array([(x.min()+x.max())/2,(y.min()+y.max())/2]); target_w=x.max()-x.min()+1
start=np.array([(x0+x1-1)/2,(y0+y1-1)/2]); start_len=y1-y0
def rotate(t):
    t=smooth(t); center=start*(1-t)+target*t
    scale=1+(target_w/start_len-1)*t
    M=cv2.getRotationMatrix2D(((crop.shape[1]-1)/2,(crop.shape[0]-1)/2),90*t,scale)
    M[:,2]+=center-np.array([(crop.shape[1]-1)/2,(crop.shape[0]-1)/2])
    a=cv2.warpAffine(crop_a,M,(W,H),flags=cv2.INTER_LINEAR); p=cv2.warpAffine(crop,M,(W,H),flags=cv2.INTER_LINEAR)
    frame=np.uint8(np.clip(bg*(1-a[...,None])+p,0,255))
    # Finish perspective-to-orthographic registration before revealing the field.
    q=smooth((t-.78)/.22); canonical=composite(bg,s0,m0)
    return cv2.addWeighted(frame,1-q,canonical,q,0)
class Tracers:
    def __init__(self,f):
        self.f=f;self.n=420;self.p=f.seed(self.n,True);self.age=RNG.uniform(0,2,self.n);self.history=np.repeat(self.p[None,:,:],12,axis=0)
    def frame(self):
        f=self.f
        # 120 integration steps per displayed second, one common slowdown factor.
        alive=np.ones(self.n,bool)
        for _ in range(4):
            v,ok=f.velocity(self.p);mid=self.p+v*.0027/(FPS*8)
            vm,ok2=f.velocity(mid);nxt=self.p+vm*.0027/(FPS*4)
            _,ok3=f.velocity(nxt);good=ok&ok2&ok3
            self.p[good]=nxt[good];alive&=good
        self.age+=1/FPS
        dead=~alive|(self.age>10)
        if dead.any(): 
            self.p[dead]=f.seed(dead.sum());self.history[:,dead,:]=self.p[dead];self.age[dead]=0
        self.history[:-1]=self.history[1:];self.history[-1]=self.p
        # Fixed-time histories reveal short trails and prolonged dwell at low speed.
        overlay=np.zeros((H,W,3),np.uint8)
        pts=np.rint(np.stack([FX+(self.history[:,:,0]-X0)*S,CY-self.history[:,:,1]*S],axis=-1)).astype(np.int32)
        for k in range(1,len(pts)):
            c=int(25+105*k/(len(pts)-1))
            cv2.polylines(overlay,list(np.ascontiguousarray(pts[k-1:k+1].transpose(1,0,2),dtype=np.int32)),False,(c,c,c),1 if k<8 else 2,cv2.LINE_AA)
        for x,y in pts[-1]:
            if 0<=x<W and 0<=y<H: cv2.circle(overlay,(int(x),int(y)),2,(210,225,235),-1,cv2.LINE_AA)
        overlay[f.solid]=0
        return overlay
tmp=OUT.with_name('rocket-cfd-build-v6.tmp.mp4')
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
def emit(f): proc.stdin.write(np.ascontiguousarray(f,dtype=np.uint8).tobytes())
try:
    cap.set(cv2.CAP_PROP_POS_FRAMES,0); count=round((cut+1)*FPS/SRC_FPS); current=-1
    for i in range(count):
        want=min(cut,int(i*SRC_FPS/FPS))
        while current<want:
            ok,f=cap.read();current+=1
            if not ok: raise RuntimeError('Original construction read failed')
        emit(neutral(f))
    Image.fromarray(cv2.cvtColor(last,cv2.COLOR_BGR2RGB)).save(POSTER,quality=94)
    for i in range(round(1.8*FPS)):
        emit(titles(rotate(i/(round(1.8*FPS)-1)),'02 / FLOW ALIGNMENT','Original CAD · continuous rotation into the center-plane projection'))
    for j,(name,field,(solid,mask)) in enumerate(zip(NAMES,fields,solids)):
        print('Rendering',name,flush=True)
        tr=Tracers(field);lines=field.streamlines()
        for i in range(round(6.5*FPS)):
            t=i/FPS;fade=smooth(t/.85)
            b=cv2.addWeighted(bg,1-fade,field.contour,fade,0)
            particles=tr.frame();b=cv2.add(b,np.uint8(lines*fade));b=cv2.add(b,np.uint8(particles*fade))
            frame=composite(b,solid,mask)
            frame=titles(frame,'03 / '+name.upper()+'  ·  '+str(j+1)+' OF 3','Solved steady CFD · projected streamlines and slowed velocity tracers',True,name)
            emit(frame)
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
    tmp.replace(OUT)
except BaseException:
    if proc.stdin and not proc.stdin.closed:proc.stdin.close()
    proc.kill();proc.wait()
    if tmp.exists():tmp.unlink()
    raise
finally:cap.release()
print('Rendered',OUT,OUT.stat().st_size,flush=True)
# Ensure a playable, high-resolution H.264 file and a matching poster before publication.
check=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height:format=duration','-of','json',str(OUT)]))
v=check['streams'][0];assert v['codec_name']=='h264' and v['width']==W and v['height']==H and float(check['format']['duration'])>22
assert OUT.stat().st_size<50_000_000 and POSTER.stat().st_size>1000
