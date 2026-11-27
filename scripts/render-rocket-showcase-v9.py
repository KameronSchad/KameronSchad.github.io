#!/usr/bin/env python3
"""Render the rocket showcase from its original film, CAD and solved CFD.

Pressure colors are from the exported Pressure column, referenced to 12.3 psi.
No new flow solution is calculated. Tracers follow projected steady velocities;
time is uniformly slowed. The original v5 construction footage is retained.
"""
from pathlib import Path
import base64, json, math, subprocess, sys
import cv2
import numpy as np
from numba import njit
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'
SRC=A/'rocket-cfd-build-v5.mp4'
OUT=A/'rocket-cfd-build-v9.mp4'
POSTER=A/'rocket-cfd-build-v9-poster.webp'
NAMES=['biconic','hemisphere','blunt']
PRESSURE=json.loads((A/'cfd'/'pressure-v7.json').read_text())
VOLUMES={n:json.loads((A/'cfd'/(n+'-volume-v9.json')).read_text()) for n in NAMES}
PMIN=min(v['rawPressureRangePa'][0] for v in VOLUMES.values())
PMAX=max(v['rawPressureRangePa'][1] for v in VOLUMES.values())
# Shared raw extrema; nonlinear color stops allocate contrast near freestream.
assert PMIN<0<PMAX
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
# All rotations and CFD shots use this same triangle mesh and z-buffer.
MESH={name:list(glb(A/'models'/'rocket'/(name+'.glb'))) for name in NAMES}
def mesh_view(p):
    return np.column_stack([-p[:,1],-p[:,2],-p[:,0]])/.0254
@njit(cache=True)
def draw_triangles(xyz,n,idx,dep,rgb):
    h,w=dep.shape
    for q in range(0,len(idx),3):
        ia,ib,ic=idx[q],idx[q+1],idx[q+2]
        a,b,c=xyz[ia],xyz[ib],xyz[ic]
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8: continue
        left=max(0,int(math.floor(min(a[0],b[0],c[0]))));right=min(w-1,int(math.ceil(max(a[0],b[0],c[0]))))
        top=max(0,int(math.floor(min(a[1],b[1],c[1]))));bottom=min(h-1,int(math.ceil(max(a[1],b[1],c[1]))))
        for y in range(top,bottom+1):
            for x in range(left,right+1):
                u=((b[1]-c[1])*(x+.5-c[0])+(c[0]-b[0])*(y+.5-c[1]))/den
                v=((c[1]-a[1])*(x+.5-c[0])+(a[0]-c[0])*(y+.5-c[1]))/den
                k=1-u-v
                if u<-.0001 or v<-.0001 or k<-.0001: continue
                z=u*a[2]+v*b[2]+k*c[2]
                if z<=dep[y,x]: continue
                nx=u*n[ia,0]+v*n[ib,0]+k*n[ic,0]
                ny=u*n[ia,1]+v*n[ib,1]+k*n[ic,1]
                nz=u*n[ia,2]+v*n[ib,2]+k*n[ic,2]
                norm=max(1e-8,math.sqrt(nx*nx+ny*ny+nz*nz))
                nx/=norm;ny/=norm;nz/=norm
                lit=max(0.,-.20*nx-.62*ny+.76*nz)
                rim=max(0.,.28*nx-.91*ny-.26*nz)
                gloss=max(0.,-.11*nx-.36*ny+.93*nz)**18
                shade=.48+.60*lit+.13*rim
                rgb[y,x,0]=min(255.,220.*shade+35.*gloss)
                rgb[y,x,1]=min(255.,207.*shade+35.*gloss)
                rgb[y,x,2]=min(255.,187.*shade+35.*gloss)
                dep[y,x]=z
def camera(p,pitch,roll):
    v=p.copy()
    c,s=math.cos(pitch),math.sin(pitch)
    v[:,0]=c*p[:,0]-s*p[:,2];v[:,2]=s*p[:,0]+c*p[:,2]
    q=v.copy();c,s=math.cos(roll),math.sin(roll)
    q[:,0]=c*v[:,0]-s*v[:,1];q[:,1]=s*v[:,0]+c*v[:,1]
    return q
def raster(name,pitch=0.,roll=0.,desired_center=None,desired_scale=None):
    dep=np.full((H,W),-np.inf,np.float32);rgb=np.zeros((H,W,3),np.uint8)
    data=[]
    for p,n,idx in MESH[name]:
        v=camera(mesh_view(p),pitch,roll)
        normals=camera(np.column_stack([-n[:,1],-n[:,2],-n[:,0]]),pitch,roll)
        data.append((v,normals,idx))
    points=np.concatenate([d[0] for d in data])
    low=points[:,:2].min(axis=0);high=points[:,:2].max(axis=0);center=(low+high)/2
    scale=S if desired_scale is None else desired_scale
    dest=np.array([TAIL,CY])+center*S if desired_center is None else np.asarray(desired_center)
    for v,n,idx in data:
        q=v.copy();q[:,:2]=(q[:,:2]-center)*scale+dest
        draw_triangles(np.ascontiguousarray(q),np.ascontiguousarray(n),np.ascontiguousarray(idx),dep,rgb)
    m=np.isfinite(dep)
    if m.sum()<.007*W*H: raise RuntimeError('Unexpected CAD projection: '+name)
    return rgb,m
# Ray parity voxelization of closed CAD solids: distinct from the visible
# silhouette. True three-dimensional particles are not deleted by fin overlap.
@njit(cache=True)
def parity_vox(xyz,idx,mask,dmin,dstep):
    nd,nz,nx=mask.shape
    for q in range(0,len(idx),3):
        a,b,c=xyz[idx[q]],xyz[idx[q+1]],xyz[idx[q+2]]
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9: continue
        left=max(0,int(math.ceil(min(a[0],b[0],c[0]))));right=min(nx-1,int(math.floor(max(a[0],b[0],c[0]))))
        top=max(0,int(math.ceil(min(a[1],b[1],c[1]))));bottom=min(nz-1,int(math.floor(max(a[1],b[1],c[1]))))
        for y in range(top,bottom+1):
            for x in range(left,right+1):
                # tiny non-integer perturbation avoids double-counting shared triangle edges
                xx=x+1e-5;yy=y+3e-5
                u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
                v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
                k=1-u-v
                if min(u,v,k)<0: continue
                z=u*a[2]+v*b[2]+k*c[2]
                end=min(nd-1,int(math.floor((z-dmin)/dstep)))
                for iz in range(end+1): mask[iz,y,x]=not mask[iz,y,x]
def solid_volume(name):
    nx,nz,nd=240,100,71;dmin,dmax=-1.75,1.75
    total=np.zeros((nd,nz,nx),np.bool_)
    for p,n,idx in MESH[name]:
        v=mesh_view(p)
        v[:,0]=(v[:,0]-X0)/(X1-X0)*(nx-1)
        v[:,1]=(v[:,1]+Z1)/(Z1-Z0)*(nz-1)
        part=np.zeros_like(total)
        parity_vox(np.ascontiguousarray(v),np.ascontiguousarray(idx),part,dmin,(dmax-dmin)/(nd-1))
        total|=part
    assert total.any() and total.mean()<.25
    print(name,'CAD solid voxel fraction',float(total.mean()),flush=True)
    return total
# Extreme colors match the original source data, while the stops around zero
# make moderate suction regions visible without clipping the extrema.
stops=np.array([[PMIN,117,18,8],[-1100,186,35,10],[-600,242,77,12],[-250,245,153,30],[-60,190,170,98],[0,123,128,122],[80,93,163,194],[300,46,185,249],[700,31,113,239],[1200,25,49,214],[PMAX,24,15,150]],float)
def colors(v): return np.stack([np.interp(v,stops[:,0],stops[:,i]) for i in (1,2,3)],axis=-1)
class Field:
    def __init__(self,name,solid):
        self.name=name; self.solid=solid
        self.volume=VOLUMES[name]
        self.dv,self.zv,self.xv=self.volume['depthCount'],self.volume['height'],self.volume['width']
        self.v3=np.frombuffer(base64.b64decode(self.volume['data']),dtype='<i2').reshape(self.dv,self.zv,self.xv,3).astype(np.float32)
        self.occupancy=solid_volume(name)
        j=json.loads((A/'cfd'/(name+'.json')).read_text());self.nx=j['width'];self.nz=j['height']
        assert j['bounds']==[X0,X1,Z0,Z1]
        self.a=np.frombuffer(base64.b64decode(j['data']),dtype='<i2').reshape(self.nz,self.nx,3).astype(float)
        valid=self.a[:,:,0]!=32767
        self.valid=valid
        pc=PRESSURE['cases'][name]
        assert PRESSURE['bounds']==j['bounds'] and PRESSURE['width']==self.nx and PRESSURE['height']==self.nz
        for k in ('xPlaneIn','tailYIn','centerZIn'): assert pc['sourceGridRegistration'][k]==j[k]
        pressure=np.frombuffer(base64.b64decode(pc['data']),dtype='<i2').reshape(self.nz,self.nx).astype(np.float32)
        assert (int(pressure.min()),int(pressure.max()))==tuple(pc['rangePa'])
        val=cv2.resize(np.where(valid,pressure,0),(FW,FH),interpolation=cv2.INTER_LINEAR)
        weight=cv2.resize(valid.astype(np.float32),(FW,FH),interpolation=cv2.INTER_LINEAR)
        col=colors(val/np.maximum(weight,1e-5))
        self.contour=bg.copy()
        b=bg[FY:FY+FH,FX:FX+FW].astype(float)
        a=np.where(weight>.995,.96,0.)[...,None]
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
    def velocity3(self,p):
        # p columns: axial, vertical, depth. Depth increases toward the camera.
        u=(p[:,0]-X0)/(X1-X0);v=(Z1-p[:,1])/(Z1-Z0);w=(p[:,2]+1.75)/3.5
        ok=(u>=0)&(u<1)&(v>=0)&(v<1)&(w>=0)&(w<1)
        nu,nv,nw=self.occupancy.shape[2],self.occupancy.shape[1],self.occupancy.shape[0]
        ix=np.clip(np.rint(u*(nu-1)).astype(int),0,nu-1)
        iz=np.clip(np.rint(v*(nv-1)).astype(int),0,nv-1)
        id=np.clip(np.rint(w*(nw-1)).astype(int),0,nw-1)
        ok &= ~self.occupancy[id,iz,ix]
        u=np.clip(u*(self.xv-1),0,self.xv-1.00001)
        v=np.clip(v*(self.zv-1),0,self.zv-1.00001)
        w=np.clip(w*(self.dv-1),0,self.dv-1.00001)
        i,j,k=u.astype(int),v.astype(int),w.astype(int);a,b,c=u-i,v-j,w-k
        out=np.zeros((len(p),3),np.float32)
        for dz in (0,1):
            for dy in (0,1):
                for dx in (0,1):
                    vec=self.v3[k+dz,j+dy,i+dx]
                    ok &= vec[:,0]!=32767
                    weight=(a if dx else 1-a)*(b if dy else 1-b)*(c if dz else 1-c)
                    out+=weight[:,None]*vec
        return out,ok
    def seed(self,n,initial=False):
        p=np.column_stack([RNG.uniform(X0+.035,X1-.035 if initial else X0+.22,n),RNG.uniform(Z0+.07,Z1-.07,n),RNG.uniform(-1.35,1.35,n)])
        near=RNG.random(n)<.30
        p[near,1]=RNG.uniform(-.52,.52,near.sum())
        p[near,2]=RNG.uniform(-.65,.65,near.sum())
        for _ in range(30):
            _,ok=self.velocity3(p)
            if ok.all(): return p
            p[~ok,0]=RNG.uniform(X0+.035,X1-.035 if initial else X0+.22,(~ok).sum())
            p[~ok,1]=RNG.uniform(Z0+.07,Z1-.07,(~ok).sum())
            p[~ok,2]=RNG.uniform(-1.35,1.35,(~ok).sum())
        raise RuntimeError('Could not seed outside CAD')
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
        d.text((FX,ly-round(H*.034)),'STATIC PRESSURE  /  Δp (Pa) relative to 12.3 psi',font=font(17,True),fill=(210,229,237))
        bar=np.uint8(colors(np.linspace(PMIN,PMAX,FW))[:,::-1]);bar=np.repeat(bar[None,:,:],lh,axis=0)
        im.paste(Image.fromarray(bar),(FX,ly))
        for v in (PMIN,-1000,-500,0,500,1000,PMAX):
            x=round(FX+FW*(v-PMIN)/(PMAX-PMIN));d.line((x,ly+lh,x,ly+lh+5),fill=(180,198,210),width=1)
            d.text((x,ly+lh+7),str(v),font=font(15),fill=(180,198,210),anchor='la' if v==PMIN else 'ra' if v==PMAX else 'ma')
    return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)
solids=[raster(n) for n in NAMES]; fields=[Field(n,m) for n,(_,m) in zip(NAMES,solids)]
# Rebuild the complete handoff as a continuous 3D camera move.
# The start projection is fitted to the original upright frame. During the
# first part of the movement the source image is gently registered to the
# CAD render; no image substitution or geometry crossfade occurs at the end.
s0,m0=solids[0]; canonical=composite(bg,s0,m0)
y,x=np.nonzero(m0);target=np.array([(x.min()+x.max())/2,(y.min()+y.max())/2])
start=np.array([(x0+x1-1)/2,(y0+y1-1)/2]);start_len=y1-y0
pitch0=math.radians(8.)
upright_pts=np.concatenate([camera(mesh_view(p),pitch0,math.pi/2) for p,n,idx in MESH[NAMES[0]]])
initial_scale=start_len/(upright_pts[:,1].max()-upright_pts[:,1].min())
def rotate(t):
    if t>=1:return canonical.copy()
    u=smooth(t)
    center=start*(1-u)+target*u
    scale=initial_scale*(1-u)+S*u
    pitch=pitch0*(1-u);roll=math.pi/2*(1-u)
    solid,mask=raster(NAMES[0],pitch,roll,center,scale)
    rendered=composite(bg,solid,mask)
    if t<.30:
        # Align the pre-existing upright footage to the new moving model.
        M=cv2.getRotationMatrix2D(((crop.shape[1]-1)/2,(crop.shape[0]-1)/2),90*u,scale/initial_scale)
        M[:,2]+=center-np.array([(crop.shape[1]-1)/2,(crop.shape[0]-1)/2])
        a=cv2.warpAffine(crop_a,M,(W,H),flags=cv2.INTER_LINEAR)
        p=cv2.warpAffine(crop,M,(W,H),flags=cv2.INTER_LINEAR)
        orig=np.uint8(np.clip(bg*(1-a[...,None])+p,0,255))
        blend=smooth(t/.30)
        rendered=cv2.addWeighted(orig,1-blend,rendered,blend,0)
    return rendered
class Tracers:
    def __init__(self,f):
        self.f=f;self.n=1250;self.p=f.seed(self.n,True);self.history=np.repeat(self.p[None,:,:],10,axis=0)
    def frame(self):
        f=self.f
        # Integrate the solved projected velocity. No particle age or TTL.
        # If a step enters the solid or unsupported interior, retry with smaller
        # steps and otherwise keep the last valid point, never teleport it.
        exited=np.zeros(self.n,bool)
        def outside(p):
            return (p[:,0]<=X0)|(p[:,0]>=X1)|(p[:,1]<=Z0)|(p[:,1]>=Z1)
        for _ in range(4):
            pending=~exited
            for fraction in (1.,.5,.25,.125,.0625):
                ids=np.flatnonzero(pending)
                if len(ids)==0: break
                p=self.p[ids];v,ok=f.velocity3(p)
                dt=.0027/(FPS*4)*fraction
                mid=p+v*dt*.5
                # When the integrated step passes the visible domain boundary,
                # it may exit even though the midpoint has no grid support.
                vm,ok2=f.velocity3(mid)
                vm[outside(mid)]=v[outside(mid)]
                nxt=p+vm*dt
                out=outside(nxt)
                _,ok3=f.velocity3(nxt)
                leave=ok&out&(ok2|outside(mid))
                good=ok&ok2&ok3&(~out)
                self.p[ids[good]]=nxt[good]
                exited[ids[leave]]=True
                pending[ids[good|leave]]=False
        if exited.any():
            self.p[exited]=f.seed(exited.sum())
            self.history[:,exited,:]=self.p[exited]
        self.history[:-1]=self.history[1:];self.history[-1]=self.p
        # Fixed-time histories reveal short trails and prolonged dwell at low speed.
        overlay=np.zeros((H,W,3),np.uint8)
        pts=np.rint(np.stack([FX+(self.history[:,:,0]-X0)*S,CY-self.history[:,:,1]*S],axis=-1)).astype(np.int32)
        for k in range(1,len(pts)):
            c=int(25+105*k/(len(pts)-1))
            cv2.polylines(overlay,list(np.ascontiguousarray(pts[k-1:k+1].transpose(1,0,2),dtype=np.int32)),False,(c,c,c),1 if k<8 else 2,cv2.LINE_AA)
        for x,y in pts[-1]:
            if FX<=x<FX+FW and FY<=y<FY+FH: cv2.circle(overlay,(int(x),int(y)),2,(210,225,235),-1,cv2.LINE_AA)
        overlay[f.solid]=0
        return overlay
tmp=OUT.with_name('rocket-cfd-build-v9.tmp.mp4')
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
    for i in range(round(2.35*FPS)):
        t=i/(round(2.35*FPS)-1)
        image=rotate(t)
        titled=titles(image,'02 / FLOW ALIGNMENT','Original CAD · orthographic alignment')
        if t<.08:
            titled=cv2.addWeighted(last,1-smooth(t/.08),titled,smooth(t/.08),0)
        emit(titled)
    for j,(name,field,(solid,mask)) in enumerate(zip(NAMES,fields,solids)):
        print('Rendering',name,flush=True)
        tr=Tracers(field);lines=field.streamlines()
        for i in range(round(6.5*FPS)):
            t=i/FPS;fade=smooth(t/.85);particle_fade=smooth((t-.25)/.75)
            b=cv2.addWeighted(bg,1-fade,field.contour,fade,0)
            particles=tr.frame()
            # Subtle dark keylines beneath white tracer heads remain readable on warm contours.
            b=cv2.subtract(b,np.uint8(lines*fade*.24))
            silhouette=cv2.dilate(particles.max(axis=2),np.ones((3,3),np.uint8))
            shadow=np.repeat((silhouette[...,None].astype(np.float32)*.32*particle_fade).astype(np.uint8),3,axis=2)
            b=cv2.subtract(b,shadow);b=cv2.add(b,np.uint8(particles*particle_fade*.85))
            frame=composite(b,solid,mask)
            flow_title=titles(frame,'03 / '+name.upper()+'  ·  '+str(j+1)+' OF 3','Static pressure slice · 3D velocity tracers, slowed uniformly',True,name)
            if j==0 and fade<1:
                align_title=titles(frame,'02 / FLOW ALIGNMENT','Original CAD · orthographic alignment')
                flow_title=cv2.addWeighted(align_title,1-fade,flow_title,fade,0)
            emit(flow_title)
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
