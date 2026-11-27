#!/usr/bin/env python3
"""Render the rocket showcase from its original film, CAD and solved CFD.

Pressure colors are from the exported Pressure column, referenced to 12.3 psi.
No new flow solution is calculated. Tracers follow projected steady velocities;
time is uniformly slowed. V15 uses native 1920 x 1440 rendering, a 15-second limit, registered CAD and upstream-only seeds.
"""
from pathlib import Path
import base64, json, math, subprocess, sys
import cv2
import numpy as np
from numba import njit
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import binary_dilation, binary_fill_holes
from scipy.optimize import least_squares
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'
SRC=A/'rocket-cfd-build-v5.mp4'
OUT=A/'rocket-cfd-build-v15.mp4'
POSTER=A/'rocket-cfd-build-v15-poster.webp'
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
W,H=1920,1440
FX=round(W*.045); FW=W-2*FX
S=FW/12; CY=round(H*.47); FH=round(4.7*S); FY=round(CY-FH/2)
TAIL=FX-X0*S
FONTS='/usr/share/fonts/truetype/dejavu/'
def font(n,bold=False):
    return ImageFont.truetype(FONTS+('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),max(12,round(n*W/1408)))
def smooth(t): 
    t=np.clip(t,0,1); return float(t*t*(3-2*t))
def xy(x,z): return np.asarray([FX+(x-X0)*S,CY-z*S])
# Native-resolution drafting stage, matched to reference poster styling.
yy,xx=np.mgrid[:H,:W]
r2=((xx-W/2)/W)**2+((yy-H/2)/H)**2
bg=np.uint8(np.clip(np.array([32.,24.,17.])[None,None,:]-r2[...,None]*np.array([12.,9.,6.]),0,255))
for x in range(0,W,48): cv2.line(bg,(x,0),(x,H-1),(36,29,23),1,cv2.LINE_AA)
for y in range(0,H,48): cv2.line(bg,(0,y),(W-1,y),(36,29,23),1,cv2.LINE_AA)
x0,x1=round(W*.43),round(W*.57)
y0,y1=round(H*.12),round(H*.81)
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
def unregistered(p):
    return np.column_stack([-p[:,1],-p[:,2],-p[:,0]])/.0254
REG={}
for name in NAMES:
    raw=json.loads((A/'cfd'/(name+'-samples-v10.json')).read_text())
    a=np.frombuffer(base64.b64decode(raw['data']),dtype='<f4').reshape(-1,7).astype(float)
    wall=a[np.linalg.norm(a[:,3:6],axis=1)<.001,:3]
    ring=wall[(wall[:,0]>-2.7)&(wall[:,0]<-1.5)]
    r=np.linalg.norm(ring[:,1:3],axis=1)
    ring=ring[(r>.37)&(r<.51)]
    assert len(ring)>40
    fit=least_squares(lambda c: np.linalg.norm(ring[:,1:3]-c,axis=1)-.4375,[0.,0.],loss='soft_l1',f_scale=.015).x
    nose=unregistered(MESH[name][1][0])
    cadcenter=(nose[:,2].min()+nose[:,2].max())/2
    shift=np.array([0.,-fit[0],fit[1]-cadcenter])
    REG[name]=shift
    before=np.median(abs(np.linalg.norm(ring[:,1:3]-[0.,cadcenter],axis=1)-.4375))
    after=np.median(abs(np.linalg.norm(ring[:,1:3]-fit,axis=1)-.4375))
    print(name,'registration shift screen XYZ',shift,'ring residual before/after',before,after,flush=True)
    assert after<.035 and after<before*.5
def mesh_view(p,name):
    return unregistered(p)+REG[name]
def physical_mesh(name):
    parts=[]
    for p,n,idx in MESH[name]:
        v=mesh_view(p,name).copy();v[:,1]*=-1
        parts.append(trimesh.Trimesh(vertices=v,faces=idx.reshape(-1,3),process=True))
    return trimesh.util.concatenate(parts)
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
        v=camera(mesh_view(p,name),pitch,roll)
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
    return rgb,m,dep
# Ray parity voxelization of closed CAD solids: distinct from the visible
# silhouette. True three-dimensional particles are not deleted by fin overlap.
@njit(cache=True)
def parity_vox(xyz,idx,mask,shell,dmin,dstep):
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
                iz=int(round((z-dmin)/dstep))
                if 0<=iz<nd: shell[iz,y,x]=True
def solid_volume(name):
    nx,nz,nd=480,200,141;dmin,dmax=-1.75,1.75
    total=np.zeros((nd,nz,nx),np.bool_)
    for p,n,idx in MESH[name]:
        v=mesh_view(p,name)
        v[:,0]=(v[:,0]-X0)/(X1-X0)*(nx-1)
        v[:,1]=(v[:,1]+Z1)/(Z1-Z0)*(nz-1)
        part=np.zeros_like(total);shell=np.zeros_like(total)
        parity_vox(np.ascontiguousarray(v),np.ascontiguousarray(idx),part,shell,dmin,(dmax-dmin)/(nd-1))
        total|=part|shell
    # One approximately 0.025-inch voxel of numerical safety, not a pressure cushion.
    # Close enclosed holes in each axial slice so thin surfaces cannot leak.
    for ix in range(nx): total[:,:,ix]=binary_fill_holes(total[:,:,ix])
    total=binary_dilation(total,iterations=1)
    assert total.any() and total.mean()<.25
    print(name,'CAD solid voxel fraction',float(total.mean()),flush=True)
    return total
# Extreme colors match the original source data, while the stops around zero
# make moderate suction regions visible without clipping the extrema.
stops=np.array([[PMIN,117,18,8],[-1100,186,35,10],[-600,242,77,12],[-250,245,153,30],[-60,190,170,98],[0,123,128,122],[80,93,163,194],[300,46,185,249],[700,31,113,239],[1200,25,49,214],[PMAX,24,15,150]],float)
def colors(v): return np.stack([np.interp(v,stops[:,0],stops[:,i]) for i in (1,2,3)],axis=-1)
@njit(cache=True)
def exact_vectors(points, transforms, neighbors, vertices, values, locator):
    # The lookup grid stores tetrahedron IDs only. It never stores or
    # interpolates velocity. The actual value is a barycentric interpolation
    # of the four original SolidWorks samples at each query position.
    out=np.zeros((len(points),4),np.float64)
    ok=np.zeros(len(points),np.bool_)
    nd,nz,nx=locator.shape
    for i in range(len(points)):
        x,y,z=points[i]
        ix=max(0,min(nx-1,int(round((x+7.)/12.*(nx-1)))))
        iy=max(0,min(nz-1,int(round((2.35-y)/4.7*(nz-1)))))
        iz=max(0,min(nd-1,int(round((z+1.75)/3.5*(nd-1)))))
        k=locator[iz,iy,ix]
        for j in range(96):
            if k<0: break
            dx=x-transforms[k,3,0];dy=y-transforms[k,3,1];dz=z-transforms[k,3,2]
            a=transforms[k,0,0]*dx+transforms[k,0,1]*dy+transforms[k,0,2]*dz
            b=transforms[k,1,0]*dx+transforms[k,1,1]*dy+transforms[k,1,2]*dz
            c=transforms[k,2,0]*dx+transforms[k,2,1]*dy+transforms[k,2,2]*dz
            d=1.-a-b-c
            if not math.isfinite(a+b+c+d): break
            if min(a,b,c,d)>=-1e-10:
                for m in range(4):
                    out[i,m]=a*values[vertices[k,0],m]+b*values[vertices[k,1],m]+c*values[vertices[k,2],m]+d*values[vertices[k,3],m]
                ok[i]=True;break
            index=0;least=a
            if b<least:index=1;least=b
            if c<least:index=2;least=c
            if d<least:index=3
            k=neighbors[k,index]
    return out,ok
class Field:
    def __init__(self,name,solid,depth):
        self.name=name; self.solid=solid; self.depth=depth
        # Visual projection guard, not a modification of the velocity field.
        filled=binary_fill_holes(solid)
        filled=cv2.morphologyEx(filled.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        self.occlusion=cv2.dilate(filled,np.ones((5,5),np.uint8)).astype(bool)
        rows=np.abs((np.arange(H)-CY)/S)<=.44
        self.core_occlusion=filled.astype(bool)&rows[:,None]
        # Interpolate directly on the original irregular sample coordinates,
        # retaining the solved wall samples and full three velocity components.
        raw=json.loads((A/'cfd'/(name+'-samples-v10.json')).read_text())
        samples=np.frombuffer(base64.b64decode(raw['data']),dtype='<f4').reshape(-1,7).astype(np.float64)
        assert len(samples)==raw['sampleCount']
        assert np.isfinite(samples).all()
        tri=Delaunay(samples[:,:3])
        self.interp=LinearNDInterpolator(tri,samples[:,3:7],fill_value=np.nan)
        self.transforms=np.ascontiguousarray(tri.transform)
        self.neighbors=np.ascontiguousarray(tri.neighbors)
        self.vertices=np.ascontiguousarray(tri.simplices)
        self.values=np.ascontiguousarray(samples[:,3:7])
        dd,zz,xx=np.meshgrid(np.linspace(-1.75,1.75,25),np.linspace(2.35,-2.35,49),np.linspace(-7,5,97),indexing='ij')
        q=np.column_stack([xx.ravel(),zz.ravel(),dd.ravel()])
        self.locator=np.ascontiguousarray(tri.find_simplex(q).reshape(xx.shape))
        rng=np.random.default_rng(42)
        probe=rng.uniform([-6.95,-2.3,-1.7],[4.95,2.3,1.7],size=(3000,3))
        fast,found=exact_vectors(probe,self.transforms,self.neighbors,self.vertices,self.values,self.locator)
        ref=self.interp(probe)
        comparable=found & np.isfinite(ref).all(axis=1)
        self.fast_enabled=bool(comparable.mean()>.65 and np.allclose(fast[comparable],ref[comparable],atol=1e-4,rtol=1e-6))
        print(name,'fast interpolation validated',self.fast_enabled,'coverage',float(comparable.mean()),flush=True)
        print(name,'tetrahedron locator coverage',float(found.mean()),flush=True)
        test=self.interp(samples[::137,:3])
        assert np.allclose(test,samples[::137,3:7],atol=1e-4,rtol=1e-6), 'Source vector interpolation verification failed'
        self.occupancy=solid_volume(name)
        self.samples=samples
        self.mesh=physical_mesh(name)
        wall=samples[np.linalg.norm(samples[:,3:6],axis=1)<.001,:3]
        distances=[]
        for chunk in np.array_split(wall,max(1,math.ceil(len(wall)/64))):
            _,dist,_=trimesh.proximity.closest_point(self.mesh,chunk)
            distances.extend(dist)
        distances=np.asarray(distances)
        for label,sel in [('nose',wall[:,0]<-3.5),('body',(wall[:,0]>=-3.5)&(wall[:,0]<-1.5)),('fin/tail',wall[:,0]>=-1.5)]:
            if sel.any(): print(name,label,'wall-to-CAD median/p90 in',np.median(distances[sel]),np.quantile(distances[sel],.9),flush=True)
        self.nose_x=min(float(mesh_view(p,name)[:,0].min()) for p,n,idx in MESH[name])
        self.tail_x=max(float(mesh_view(p,name)[:,0].max()) for p,n,idx in MESH[name])
        print(name,'direct interpolation',len(samples),'samples;',raw['noSlipWallSamples'],'wall samples',flush=True)
        j=json.loads((A/'cfd'/(name+'.json')).read_text());self.nx=j['width'];self.nz=j['height']
        assert j['bounds']==[X0,X1,Z0,Z1]
        self.a=np.frombuffer(base64.b64decode(j['data']),dtype='<i2').reshape(self.nz,self.nx,3).astype(float)
        valid=self.a[:,:,0]!=32767
        self.valid=valid
        pc=PRESSURE['cases'][name]
        assert PRESSURE['bounds']==j['bounds'] and PRESSURE['width']==self.nx and PRESSURE['height']==self.nz
        for k in ('xPlaneIn','tailYIn','centerZIn'): assert pc['sourceGridRegistration'][k]==j[k]
        xx,zz=np.meshgrid(np.linspace(X0,X1,self.nx),np.linspace(Z1,Z0,self.nz))
        queries=np.column_stack([xx.ravel(),zz.ravel(),np.zeros(xx.size)])
        pressure=self.interp(queries)[:,3].reshape(self.nz,self.nx).astype(np.float32)
        valid &= np.isfinite(pressure)
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
    def fluid(self,p):
        u=(p[:,0]-X0)/(X1-X0);v=(Z1-p[:,1])/(Z1-Z0);w=(p[:,2]+1.75)/3.5
        ok=(u>=0)&(u<1)&(v>=0)&(v<1)&(w>=0)&(w<1)
        nw,nv,nu=self.occupancy.shape
        ix=np.clip(np.rint(u*(nu-1)).astype(int),0,nu-1)
        iz=np.clip(np.rint(v*(nv-1)).astype(int),0,nv-1)
        id=np.clip(np.rint(w*(nw-1)).astype(int),0,nw-1)
        return ok & ~self.occupancy[id,iz,ix]
    def velocity3(self,p):
        fluid=self.fluid(p)
        if self.fast_enabled:
            data,found=exact_vectors(p,self.transforms,self.neighbors,self.vertices,self.values,self.locator)
        else:
            data=self.interp(p);found=np.isfinite(data).all(axis=1)
        # Rare failed tetrahedron walks use the exact SciPy interpolator.
        missing=fluid&~found
        if missing.any():
            data[missing]=self.interp(p[missing])
            found[missing]=np.isfinite(data[missing]).all(axis=1)
        ok=fluid&found
        return np.where(ok[:,None],data[:,:3],0.),ok
    def clear_segment(self,p,q):
        # At least five checks on every accepted short segment; no tunneling.
        ok=np.ones(len(p),bool)
        for t in (.2,.4,.6,.8,1.):
            ok &= self.fluid(p+(q-p)*t)
        return ok
    def seed(self,n,initial=False):
        p=np.column_stack([RNG.uniform(X0+.045,X0+.18,n),RNG.uniform(Z0+.07,Z1-.07,n),RNG.uniform(-1.35,1.35,n)])
        near=RNG.random(n)<.40
        p[near,1]=RNG.uniform(-.45,.45,near.sum())
        p[near,2]=RNG.uniform(-.45,.45,near.sum())
        for _ in range(30):
            _,ok=self.velocity3(p)
            if ok.all():
                assert (p[:,0]<self.nose_x-.5).all()
                return p
            p[~ok,1]=RNG.uniform(Z0+.07,Z1-.07,(~ok).sum())
            p[~ok,2]=RNG.uniform(-1.35,1.35,(~ok).sum())
        raise RuntimeError('Could not seed supported upstream inlet')
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
solids=[raster(n) for n in NAMES]; fields=[Field(n,m,d) for n,(_,m,d) in zip(NAMES,solids)]
# V8-style locked projection: a single in-plane quarter-turn, no yaw.
# The final model is pixel-identical to the model used in the CFD scene.
s0,m0,d0=solids[0]; canonical=composite(bg,s0,m0)
y,x=np.nonzero(m0); target=np.array([(x.min()+x.max())/2,(y.min()+y.max())/2])
target_w=x.max()-x.min()+1
start=np.array([(x0+x1-1)/2,(y0+y1-1)/2]); start_len=y1-y0
canonical_a=m0.astype(np.float32)
canonical_p=s0.astype(np.float32)*canonical_a[...,None]
def rotate(t):
    u=smooth(t)
    if t>=1:return canonical.copy()
    center=start*(1-u)+target*u
    scale=(start_len/target_w)*(1-u)+u
    M=cv2.getRotationMatrix2D(tuple(target),-90*(1-u),scale)
    M[:,2]+=center-target
    ca=cv2.warpAffine(canonical_a,M,(W,H),flags=cv2.INTER_LINEAR)
    cp=cv2.warpAffine(canonical_p,M,(W,H),flags=cv2.INTER_LINEAR)
    return np.uint8(np.clip(bg*(1-ca[...,None])+cp,0,255))
assert np.array_equal(rotate(1.),canonical)
# One model from sketch to solid to flow; no separately rendered upright splice.
upright=rotate(0.)
M0=cv2.getRotationMatrix2D(tuple(target),-90.,start_len/target_w)
M0[:,2]+=start-target
upright_mask=cv2.warpAffine(canonical_a,M0,(W,H),flags=cv2.INTER_LINEAR)
# Sequential arc-length drawing of actual silhouette and CAD creases.
paths=[]
for cnt in cv2.findContours((upright_mask>.5).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0]:
    p=cnt[:,0,:].astype(float)
    if len(p)>10:
        i=np.argmax(p[:,1]);p=np.roll(p,-i,axis=0);paths.append(np.vstack([p,p[0]]))
feature=np.zeros((H,W),np.uint8)
for p,n,idx in MESH[NAMES[0]]:
    v=mesh_view(p,NAMES[0])
    mesh=trimesh.Trimesh(vertices=v,faces=idx.reshape(-1,3),process=True)
    edges=mesh.face_adjacency_edges[mesh.face_adjacency_angles>math.radians(22)]
    for a,b in mesh.vertices[edges]:
        q=np.array([a,b]); pix=q[:,:2]*S+np.array([TAIL,CY])
        mid=pix.mean(axis=0);ix,iy=np.rint(mid).astype(int)
        if not (0<=ix<W and 0<=iy<H):continue
        if q[:,2].mean()<d0[iy,ix]-.055:continue
        pix=pix@M0[:,:2].T+M0[:,2]
        cv2.line(feature,tuple(np.rint(pix[0]).astype(int)),tuple(np.rint(pix[1]).astype(int)),255,2,cv2.LINE_AA)
for cnt in cv2.findContours((feature>100).astype(np.uint8),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)[0]:
    p=cnt[:,0,:].astype(float)
    if len(p)>12:paths.append(p)
paths.sort(key=lambda p:-p[:,1].mean())
lengths=[np.r_[0.,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))] for p in paths]
total=sum(l[-1] for l in lengths)
assert total>100
def build_frame(t):
    if t>=5.0:return upright.copy()
    base=bg.copy()
    if t<2.8:
        u=smooth(t/.45)
        cv2.line(base,(round(start[0]),round(start[1]+start_len*.53)),(round(start[0]),round(start[1]+start_len*.53-u*start_len*1.06)),(70,65,52),1,cv2.LINE_AA)
    budget=smooth((t-.18)/2.32)*total
    wire=np.zeros((H,W),np.uint8)
    for p,l in zip(paths,lengths):
        if budget<=0:break
        k=int(np.searchsorted(l,budget,side='right'))
        if k>=2:cv2.polylines(wire,[np.rint(p[:k]).astype(np.int32)],False,255,2,cv2.LINE_AA)
        budget-=l[-1]
    yy=np.arange(H)[:,None]
    nose=yy<start[1]-start_len*.02
    body_op=smooth((t-2.5)/1.55);nose_op=smooth((t-3.3)/1.7)
    opacity=np.where(nose,nose_op,body_op)
    base=np.uint8(np.clip(base*(1-opacity[...,None])+upright*opacity[...,None],0,255))
    alpha=(wire.astype(np.float32)/255*(1-opacity))[...,None]
    return np.uint8(np.clip(base*(1-alpha)+np.array([225.,192.,112.])*alpha,0,255))
class Tracers:
    duration=2.8
    dt=.00004
    def __init__(self,f):
        self.f=f
        self.advance=.0027/FPS/self.dt
        self.window=int(math.ceil(self.duration*FPS*self.advance))+3
        self.steps=3*self.window+3
        seeds=f.seed(2200)
        paths,exits,low,rev=self.trace(seeds)
        valid=np.ones(len(paths),bool)
        checked=0
        for i,path in enumerate(paths):
            if len(path)<2:continue
            a=path[:-1];b=path[1:]
            near=(np.minimum(a[:,0],b[:,0])<f.tail_x+.1)&(np.maximum(a[:,0],b[:,0])>f.nose_x-.1)&(np.minimum(abs(a[:,1]),abs(b[:,1]))<.98)&(np.minimum(abs(a[:,2]),abs(b[:,2]))<.98)
            a=a[near];b=b[near]
            delta=b-a;length=np.linalg.norm(delta,axis=1)
            good=length>1e-9
            a=a[good];delta=delta[good];length=length[good]
            if not len(a):continue
            checked+=len(a)
            hit,ray,tri=f.mesh.ray.intersects_location(a,delta/length[:,None],multiple_hits=True)
            if len(hit) and np.any(np.linalg.norm(hit-a[ray],axis=1)<=length[ray]+1e-7):valid[i]=False
        self.paths=paths
        self.lengths=np.array([len(p) for p in paths])
        self.exits=exits
        eligible=valid&(self.lengths>4)&(exits|(self.lengths>=self.window+3))
        self.inlet=np.flatnonzero(eligible)
        print(f.name,'upstream seeds',len(paths),'eligible',len(self.inlet),'unresolved short',int((~eligible&valid).sum()),'triangle-rejected',int((~valid).sum()),'triangle-tested segments',checked,'eligible reverse',int((eligible&rev).sum()),'eligible slow',int((eligible&low).sum()),flush=True)
        if len(self.inlet)<20:raise RuntimeError('Insufficient supported upstream trajectories')
        self.n=1300
        self.ids=RNG.choice(self.inlet,self.n,replace=True)
        maxphase=np.where(exits[self.ids],self.lengths[self.ids]-2,self.lengths[self.ids]-self.window-2)
        self.phase=RNG.random(self.n)*np.maximum(maxphase,0)
        self.history=np.repeat(self.positions()[None,:,:],7,axis=0)
    def trace(self,seeds):
        f=self.f;dt=self.dt
        p=seeds.copy();pool=len(p)
        tracks=np.empty((self.steps,pool,3),np.float32)
        tracks[0]=p
        active=np.ones(pool,bool);exits=np.zeros(pool,bool)
        ends=np.ones(pool,np.int32)
        low=np.zeros(pool,bool);rev=np.zeros(pool,bool)
        for k in range(1,self.steps):
            ids=np.flatnonzero(active)
            if not len(ids):break
            q=p[ids];v,ok=f.velocity3(q)
            low[ids]|=ok&(np.linalg.norm(v,axis=1)<500)
            rev[ids]|=ok&(v[:,0]<-5)
            mid=q+.5*dt*v;vm,ok2=f.velocity3(mid)
            # At the visible boundary an outward segment is clipped exactly
            # to the boundary; never recycle at an interior obstacle.
            def outside(a):
                return (a[:,0]<=X0)|(a[:,0]>=X1)|(a[:,1]<=Z0)|(a[:,1]>=Z1)|(a[:,2]<=-1.75)|(a[:,2]>=1.75)
            outer=outside(mid)
            vm[outer]=v[outer]
            nxt=q+dt*vm
            retry=ok&~outside(nxt)&(~ok2|~f.clear_segment(q,nxt))
            if retry.any():
                sub=q[retry].copy();safe=np.ones(len(sub),bool)
                for _ in range(4):
                    sv,sok=f.velocity3(sub)
                    sm=sub+dt*sv/8
                    sv2,sok2=f.velocity3(sm)
                    dest=sub+dt*sv2/4
                    safe &= sok&sok2&f.clear_segment(sub,sm)&f.clear_segment(sm,dest)&~outside(dest)
                    sub=dest
                ix=np.flatnonzero(retry)
                nxt[ix[safe]]=sub[safe]
                ok2[ix[safe]]=True
                ok2[ix[~safe]]=False
            exiting=ok&(ok2|outer)&outside(nxt)
            frac=np.ones(len(q))
            for axis,lo,hi in ((0,X0,X1),(1,Z0,Z1),(2,-1.75,1.75)):
                delta=nxt[:,axis]-q[:,axis]
                upper=(delta>0)&(nxt[:,axis]>=hi)
                lower=(delta<0)&(nxt[:,axis]<=lo)
                frac[upper]=np.minimum(frac[upper],(hi-q[upper,axis])/delta[upper])
                frac[lower]=np.minimum(frac[lower],(lo-q[lower,axis])/delta[lower])
            # Evaluate to just inside the display boundary for collision tests.
            test=q+(nxt-q)*np.maximum(0,frac-1e-6)[:,None]
            clear=f.clear_segment(q,test)&(outer|f.clear_segment(q,mid))
            good=ok&(ok2|outer)&clear&(~exiting)&(~outside(nxt))
            leave=exiting&clear
            tracks[k,ids[good]]=nxt[good]
            tracks[k,ids[leave]]= (q+(nxt-q)*frac[:,None])[leave]
            ends[ids[good|leave]]=k+1
            p[ids[good]]=nxt[good]
            exits[ids[leave]]=True
            active[ids[~good]]=False
        return [tracks[:ends[i],i].copy() for i in range(pool)],exits,low,rev
    def positions(self):
        pos=np.empty((self.n,3),np.float32)
        for i,(path_id,t) in enumerate(zip(self.ids,self.phase)):
            path=self.paths[path_id];j=min(int(t),len(path)-2);u=t-j
            pos[i]=(1-u)*path[j]+u*path[j+1]
        return pos
    def frame(self):
        self.phase+=self.advance
        end=self.phase>=self.lengths[self.ids]-1
        if np.any(end&~self.exits[self.ids]):
            raise RuntimeError('Non-exiting tracer exhausted its validated physical-time path')
        if end.any():
            self.ids[end]=RNG.choice(self.inlet,end.sum(),replace=True)
            self.phase[end]=0.
        p=self.positions()
        self.history[:,end]=p[end]
        self.history[:-1]=self.history[1:];self.history[-1]=p
        overlay=np.zeros((H,W,3),np.uint8)
        pts=np.rint(np.stack([FX+(self.history[:,:,0]-X0)*S,CY-self.history[:,:,1]*S],axis=-1)).astype(np.int32)
        # Depth-test each sampled pixel along every short rendered segment.
        for k in range(1,len(pts)):
            c=int(25+110*k/(len(pts)-1))
            for i in range(self.n):
                a,b=pts[k-1:k+1,i]; da,db=self.history[k-1:k+1,i,2]
                count=max(1,int(np.ceil(np.linalg.norm(b-a))))
                u=np.linspace(0.,1.,count+1)
                pp=np.rint(a[None,:]+u[:,None]*(b-a)[None,:]).astype(int)
                x,y=pp.T
                inside=(x>=0)&(x<W)&(y>=0)&(y<H)
                x=x[inside];y=y[inside];u=u[inside]
                visible=da+(db-da)*u>self.f.depth[y,x]+.008
                overlay[y[visible],x[visible]]=np.maximum(overlay[y[visible],x[visible]],c)
        for i,(x,y) in enumerate(pts[-1]):
            if FX<=x<FX+FW and FY<=y<FY+FH and self.history[-1,i,2]>self.f.depth[y,x]+.008:
                cv2.circle(overlay,(int(x),int(y)),3,(210,225,235),-1,cv2.LINE_AA)
        return overlay
tmp=OUT.with_name('rocket-cfd-build-v15.tmp.mp4')
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE)
def emit(f): proc.stdin.write(np.ascontiguousarray(f,dtype=np.uint8).tobytes())
try:
    for i in range(round(5.5*FPS)):
        t=i/FPS
        frame=build_frame(t)
        emit(titles(frame,'01 / CAD CONSTRUCTION','Original STEP geometry · feature drawing and surface reveal'))
    Image.fromarray(cv2.cvtColor(titles(upright,'01 / CAD CONSTRUCTION','Original STEP geometry · feature drawing and surface reveal'),cv2.COLOR_BGR2RGB)).save(POSTER,quality=94)
    assert np.array_equal(build_frame(5.5),rotate(0.)), 'Build/rotation handoff mismatch'
    for i in range(round(1.1*FPS)):
        t=i/(round(1.1*FPS)-1)
        frame=rotate(t)
        a=smooth(t/.20)
        build_title=titles(frame,'01 / CAD CONSTRUCTION','Original STEP geometry · feature drawing and surface reveal')
        align_title=titles(frame,'02 / FLOW ALIGNMENT','Original CAD · orthographic alignment')
        emit(cv2.addWeighted(build_title,1-a,align_title,a,0))
    for j,(name,field,(solid,mask,depth)) in enumerate(zip(NAMES,fields,solids)):
        print('Rendering',name,flush=True)
        tr=Tracers(field);lines=np.zeros((H,W,3),np.uint8) # avoid mixed 2D/3D paths
        for i in range(round(2.8*FPS)):
            t=i/FPS;fade=smooth(t/.30);particle_fade=smooth(t/.30)
            b=cv2.addWeighted(bg,1-fade,field.contour,fade,0)
            particles=tr.frame()
            # Subtle dark keylines beneath white tracer heads remain readable on warm contours.
            b=cv2.subtract(b,np.uint8(lines*fade*.24))
            silhouette=cv2.dilate(particles.max(axis=2),np.ones((3,3),np.uint8))
            silhouette[mask & (particles.max(axis=2)==0)]=0
            shadow=np.repeat((silhouette[...,None].astype(np.float32)*.32*particle_fade).astype(np.uint8),3,axis=2)
            b=cv2.subtract(b,shadow);b=cv2.add(b,np.uint8(particles*particle_fade*.85))
            frame=composite(b,solid,mask)
            frame[mask]=cv2.add(frame,np.uint8(particles*particle_fade*.85))[mask]
            flow_title=titles(frame,'03 / '+name.upper()+'  ·  '+str(j+1)+' OF 3','Solved static pressure · upstream-seeded 3D velocity tracers',True,name)
            if j==0 and i==0:
                assert np.array_equal(frame,canonical), 'Rotation/CFD handoff mismatch'
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
finally:pass
print('Rendered',OUT,OUT.stat().st_size,flush=True)
# Ensure a playable, high-resolution H.264 file and a matching poster before publication.
check=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height:format=duration','-of','json',str(OUT)]))
v=check['streams'][0];assert v['codec_name']=='h264' and v['width']==W and v['height']==H and 14.99<=float(check['format']['duration'])<=15.0
assert OUT.stat().st_size<50_000_000 and POSTER.stat().st_size>1000
