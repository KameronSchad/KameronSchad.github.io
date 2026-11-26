import pandas as pd,numpy as np,json, pathlib
from scipy.spatial import Delaunay,cKDTree
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import least_squares
from scipy.ndimage import binary_fill_holes
import sys
source=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.')
out=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else 'assets/cfd'); out.mkdir(parents=True,exist_ok=True)
W,H=240,100
# Display coordinates: nose points left; +screen x is -Y, +screen z is +Z.
# Same body-tail origin, physical scale and crop on each configuration.
xx=np.linspace(-7,5.0,W); zz=np.linspace(2.35,-2.35,H); Qx,Qz=np.meshgrid(xx,zz)
for n,L in [('Biconic',6.125),('Hemisphere',3.9375),('Blunt',3.75)]:
 d=pd.read_csv(source/(n+'.txt'),sep='\t').iloc[:,:10]; a=d.to_numpy(); surf=a[(a[:,6]==0)&np.isfinite(a[:,4])]; tip=surf[:,1].max(); tail=tip-L
 # Fit cylindrical body center using wall sample coordinates; radial distance fixed by CAD diameter.
 b=surf[(surf[:,1]>tail+1.5)&(surf[:,1]<tail+2.7)][:,[0,2]]
 p0=(b.min(0)+b.max(0))/2
 fit=least_squares(lambda c: np.linalg.norm(b-c,axis=1)-.4375,p0,loss='soft_l1',f_scale=.015)
 xc,zc=fit.x
 # Volume cell centers and no-slip wall samples; omit rows without solved velocities.
 near=a[np.isfinite(a[:,6:10]).all(1)&(abs(a[:,0]-xc)<.65)&(a[:,1]>tail-5.8)&(a[:,1]<tail+7.7)]
 pts=near[:,:3]; vals=near[:,[6,8,9]]; uni,idx=np.unique(pts,axis=0,return_index=True); vals=vals[idx]; pts=uni
 q=np.column_stack([np.full(Qx.size,xc),tail-Qx.ravel(),zc+Qz.ravel()]); tri=Delaunay(pts); v=LinearNDInterpolator(tri,vals)(q)
 # No invented zero-speed values at unsupported locations. Mark outside convex hull as missing.
 valid=np.isfinite(v).all(1); v[~valid]=0
 # Exclude solid with actual 2D longitudinal silhouette from geometry at display time; retain wall samples for interpolation.
 # Quantization to integer in/s; sentinel 32767 for missing.
 aout=np.rint(v).astype('<i2'); aout[~valid]=32767
 import base64
 packed=base64.b64encode(aout.tobytes()).decode()
 meta={'name':n.lower(),'width':W,'height':H,'bounds':[-7,5,-2.35,2.35],'sourceRows':len(a),'sampleCount':len(pts),'xPlaneIn':round(xc,6),'tailYIn':round(tail,6),'centerZIn':round(zc,6),'validFraction':round(valid.mean(),5),'method':'3D piecewise linear interpolation of finite volume and wall samples; body registration inferred from wall points and nominal CAD length; no extrapolation','encoding':'base64 int16 little endian interleaved speed,Vy,Vz; 32767 missing','scale':[0,2300]}
 path=out/(n.lower()+'.json'); path.write_text(json.dumps({**meta,'data':packed},separators=(',',':'))+'\n')
 print(n,meta, 'size',path.stat().st_size)
