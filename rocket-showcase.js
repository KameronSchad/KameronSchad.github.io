/* Rocket showcase: original STEP-derived geometry + solved 120 mph CFD exports.
   Fields are reconstructed on a common YZ plane; tracers are slowed for display. */
(() => {
  'use strict';
  const NAMES = ['biconic','hemisphere','blunt'];
  const LABELS = ['BICONIC','HEMISPHERE','BLUNT'];
  const DURATION = 23.5, W = 800, H = 600, MID = 3.0625;
  const X0 = -7, X1 = 5, Z0 = -2.35, Z1 = 2.35, FIELD = {x:30,y:155.0833333333,w:740,h:289.8333333333};
  const SCALE = FIELD.w/(X1-X0), TAIL = FIELD.x-X0*SCALE, CY=300;
  const clamp = (x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const ease = x=>{x=clamp(x);return x*x*(3-2*x);};
  const mix = (a,b,t)=>a+(b-a)*t;
  const stops = [[0,177,35,42],[400,238,79,45],[850,250,190,66],[1250,177,224,112],[1650,69,195,210],[2112,31,85,196],[2300,22,42,126]];
  function color(v){v=clamp(v,0,2300);let i=1;while(i<stops.length-1&&v>stops[i][0])i++;const a=stops[i-1],b=stops[i],t=(v-a[0])/(b[0]-a[0]);return [1,2,3].map(k=>Math.round(mix(a[k],b[k],t)));}
  function canvas(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
  function makeField(raw){
    if(raw.width!==240||raw.height!==100||raw.bounds.join(',')!==[X0,X1,Z0,Z1].join(','))throw new Error('Unexpected CFD grid');
    const bytes=Uint8Array.from(atob(raw.data),c=>c.charCodeAt(0));
    if(bytes.length!==raw.width*raw.height*6)throw new Error('Incomplete CFD grid');
    const view=new DataView(bytes.buffer), values=new Int16Array(bytes.length/2);
    for(let i=0;i<values.length;i++)values[i]=view.getInt16(i*2,true);
    const c=canvas(raw.width,raw.height),ctx=c.getContext('2d'),img=ctx.createImageData(c.width,c.height);
    for(let i=0;i<c.width*c.height;i++){const v=values[i*3];if(v===32767)continue;const rgb=color(v);img.data.set([...rgb,255],i*4);}
    ctx.putImageData(img,0,0);return {...raw,values,image:c};
  }
  // Read the actual STEP-derived GLB directly. These assets contain two named,
  // untransformed indexed triangle meshes. No CDN, WebGL, or loader name rewriting.
  function parseGLB(buffer){
    const dv=new DataView(buffer);if(dv.getUint32(0,true)!==0x46546c67||dv.getUint32(4,true)!==2)throw Error('Invalid CAD GLB');
    const jsonLen=dv.getUint32(12,true),json=JSON.parse(new TextDecoder().decode(new Uint8Array(buffer,20,jsonLen)).trim()),bin=20+jsonLen+8;
    function accessor(i){const a=json.accessors[i],v=json.bufferViews[a.bufferView],n=a.type==='VEC3'?3:1;
      const bytes=a.componentType===5123?2:4,base=bin+(v.byteOffset||0)+(a.byteOffset||0),stride=v.byteStride||n*bytes;
      if(![5123,5125,5126].includes(a.componentType))throw Error('Unsupported CAD accessor');
      const out=new (a.componentType===5126?Float32Array:Uint32Array)(a.count*n);
      for(let j=0;j<a.count;j++)for(let k=0;k<n;k++){const at=base+j*stride+k*bytes;out[j*n+k]=a.componentType===5126?dv.getFloat32(at,true):a.componentType===5125?dv.getUint32(at,true):dv.getUint16(at,true);}return out;}
    function part(name){const node=json.nodes.find(n=>n.name===name||n.name===name.replaceAll(' ','_'));if(!node||node.mesh===undefined)throw Error('Missing CAD part: '+name);
      if(node.matrix||node.translation||node.rotation||node.scale)throw Error('Unexpected CAD transform');
      const p=json.meshes[node.mesh].primitives[0];return {pos:accessor(p.attributes.POSITION),normal:accessor(p.attributes.NORMAL),idx:accessor(p.indices)};}
    return {body:part('Rocket body'),nose:part('Nose cone')};
  }
  // Software orthographic rasterizer: triangle coverage and depth from the original
  // CAD, with interpolated vertex normals for clean metallic shading. The same
  // projection is used for the outline, the solid overlay, and tracer exclusion.
  function raster(part,base){
    const w=960,h=376,c=canvas(w,h),ctx=c.getContext('2d'),img=ctx.createImageData(w,h),depth=new Float32Array(w*h);depth.fill(-Infinity);
    const m=canvas(w,h),mc=m.getContext('2d'),mask=mc.createImageData(w,h),p=part.pos,n=part.normal,ind=part.idx;
    const xx=new Float32Array(p.length/3),yy=new Float32Array(xx.length),zz=new Float32Array(xx.length);
    for(let i=0;i<xx.length;i++){xx[i]=(-p[i*3+1]/.0254-X0)/(X1-X0)*w;yy[i]=(Z1-p[i*3+2]/.0254)/(Z1-Z0)*h;zz[i]=-p[i*3]/.0254;}
    for(let q=0;q<ind.length;q+=3){const a=ind[q],b=ind[q+1],d=ind[q+2],ax=xx[a],ay=yy[a],bx=xx[b],by=yy[b],dx=xx[d],dy=yy[d];
      const den=(by-dy)*(ax-dx)+(dx-bx)*(ay-dy);if(Math.abs(den)<1e-7)continue;
      const minx=Math.max(0,Math.floor(Math.min(ax,bx,dx))),maxx=Math.min(w-1,Math.ceil(Math.max(ax,bx,dx))),miny=Math.max(0,Math.floor(Math.min(ay,by,dy))),maxy=Math.min(h-1,Math.ceil(Math.max(ay,by,dy)));
      for(let y=miny;y<=maxy;y++)for(let x=minx;x<=maxx;x++){
        const u=((by-dy)*(x+.5-dx)+(dx-bx)*(y+.5-dy))/den,v=((dy-ay)*(x+.5-dx)+(ax-dx)*(y+.5-dy))/den,k=1-u-v;if(u<-.0001||v<-.0001||k<-.0001)continue;
        const at=y*w+x,dep=u*zz[a]+v*zz[b]+k*zz[d];if(dep<depth[at])continue;depth[at]=dep;
        let nx=u*n[a*3]+v*n[b*3]+k*n[d*3],ny=u*n[a*3+1]+v*n[b*3+1]+k*n[d*3+1],nz=u*n[a*3+2]+v*n[b*3+2]+k*n[d*3+2];const norm=Math.hypot(nx,ny,nz)||1;nx/=norm;ny/=norm;nz/=norm;
        const lit=Math.max(0,-.76*nx+.20*ny+.62*nz),rim=Math.max(0,.26*nx-.28*ny+.91*nz),gloss=Math.pow(Math.max(0,-.93*nx+.11*ny+.36*nz),18);
        const light=.43+.60*lit+.16*rim,at4=at*4;for(let ch=0;ch<3;ch++){img.data[at4+ch]=Math.min(255,base[ch]*light+42*gloss);mask.data[at4+ch]=255;}img.data[at4+3]=mask.data[at4+3]=255;
      }
    }
    ctx.putImageData(img,0,0);mc.putImageData(mask,0,0);return {image:c,mask:m};
  }
  function outline(mask){const c=canvas(mask.width,mask.height),ctx=c.getContext('2d');for(let i=0;i<8;i++){let a=i*Math.PI/4;ctx.drawImage(mask,2*Math.cos(a),2*Math.sin(a));}ctx.globalCompositeOperation='destination-out';ctx.drawImage(mask,0,0);ctx.globalCompositeOperation='source-in';ctx.fillStyle='#82d9dc';ctx.fillRect(0,0,c.width,c.height);return c;}
  function maskUnion(body,nose){const c=canvas(body.width,body.height),ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(body,0,0);ctx.drawImage(nose,0,0);return {w:c.width,h:c.height,alpha:ctx.getImageData(0,0,c.width,c.height).data};}
  function solid(mask,x,z){const u=Math.floor((x-X0)/(X1-X0)*mask.w),v=Math.floor((Z1-z)/(Z1-Z0)*mask.h);return u<0||u>=mask.w||v<0||v>=mask.h||mask.alpha[(v*mask.w+u)*4+3]>32;}
  function velocity(f,x,z){const u=(x-X0)/(X1-X0)*(f.width-1),v=(Z1-z)/(Z1-Z0)*(f.height-1);if(u<0||v<0||u>=f.width-1||v>=f.height-1)return null;const i=Math.floor(u),j=Math.floor(v),fx=u-i,fy=v-j,k=(j*f.width+i)*3;const ids=[k,k+3,k+f.width*3,k+f.width*3+3];if(ids.some(n=>f.values[n]===32767))return null;const sample=c=>mix(mix(f.values[ids[0]+c],f.values[ids[1]+c],fx),mix(f.values[ids[2]+c],f.values[ids[3]+c],fx),fy);return [-sample(1),sample(2)];}
  const px=x=>FIELD.x+(x-X0)*SCALE, py=z=>CY-z*SCALE;
  function rocketController(slide){
    const stage=slide.querySelector('.claw-film-stage'),old=stage.querySelector('video'),caption=slide.querySelector('figcaption span');
    const player=new EventTarget();let t=0,paused=true,ended=false,ready=false,failed=false,raf=0,last=0,initializing=null,epoch=0;
    let body,noses,fields,masks,bodyOutline,noseOutline,particles=[],active=-1;
    const layer=document.createElement('div');layer.style.cssText='position:absolute;inset:0;background:#0d1722;overflow:hidden;';
    layer.setAttribute('role','img');layer.setAttribute('aria-label','Rocket CAD assembly followed by biconic, hemisphere and blunt CFD velocity magnitude and projected velocity tracers at 120 mph.');
    const display=canvas(W*2,H*2),ctx=display.getContext('2d');display.style.cssText='position:absolute;inset:0;width:100%;height:100%;display:block;';ctx.setTransform(2,0,0,2,0,0);layer.append(display);
    const status=document.createElement('div');status.style.cssText='position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:24px;color:#b7cbd6;font:600 14px system-ui;background:#0d1722;';status.textContent='Rocket aerodynamics · preparing original CAD and solved CFD';layer.append(status);
    old.style.visibility='hidden';stage.append(layer);
    Object.defineProperties(player,{duration:{get:()=>DURATION},readyState:{get:()=>ready?1:0},paused:{get:()=>paused},ended:{get:()=>ended},error:{get:()=>failed},currentTime:{get:()=>t,set:v=>{t=clamp(Number(v)||0,0,DURATION);ended=t>=DURATION;last=0;active=-1;if(ready)draw(0);player.dispatchEvent(new Event('seeked'));}}});
    const font=(size,weight=500)=>{ctx.font=weight+' '+size+'px system-ui, sans-serif';};
    function label(s,x,y,size=14,col='#a9c0cd',weight=500,align='left'){font(size,weight);ctx.fillStyle=col;ctx.textAlign=align;ctx.fillText(s,x,y);ctx.textAlign='left';}
    function background(){ctx.clearRect(0,0,W,H);const g=ctx.createRadialGradient(400,280,35,400,280,510);g.addColorStop(0,'#172e3e');g.addColorStop(1,'#0c1621');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.strokeStyle='#7699af12';ctx.lineWidth=1;ctx.beginPath();for(let x=0;x<W;x+=32){ctx.moveTo(x,0);ctx.lineTo(x,H);}for(let y=0;y<H;y+=32){ctx.moveTo(0,y);ctx.lineTo(W,y);}ctx.stroke();}
    function hud(phase,detail,step){label('02 / ROCKET AERODYNAMICS',30,35,15,'#a7c6d2',700);label(phase,770,35,15,'#8bdcd7',700,'right');ctx.strokeStyle='#64839455';ctx.beginPath();ctx.moveTo(30,51);ctx.lineTo(770,51);ctx.stroke();label(detail,30,570,13,'#a9c0cd');label(step,770,570,13,'#8bdcd7',650,'right');}
    function blueprint(part,offset,reveal,alpha){if(reveal<=0||alpha<=0)return;ctx.save();ctx.globalAlpha=alpha;ctx.beginPath();ctx.rect(0,550-500*reveal,W,500*reveal);ctx.clip();ctx.translate(400,310);ctx.rotate(Math.PI/2);const s=61;ctx.translate((MID+offset)*s,0);ctx.drawImage(part,X0*s,-Z1*s,(X1-X0)*s,(Z1-Z0)*s);ctx.restore();}
    function shaded(part,offset,alpha,rotation,scale,centerX,centerY){if(alpha<=0)return;ctx.save();ctx.globalAlpha=alpha;ctx.translate(centerX,centerY);ctx.rotate(rotation);ctx.translate((MID+offset)*scale,0);ctx.drawImage(part.image,X0*scale,-Z1*scale,(X1-X0)*scale,(Z1-Z0)*scale);ctx.restore();}
    function spawn(p,initial=false){for(let i=0;i<30;i++){p.x=initial?mix(X0+.05,X1-.05,Math.random()):X0+.03;p.z=mix(Z0+.06,Z1-.06,Math.random());if(!solid(masks[active],p.x,p.z))break;}p.age=0;}
    function fieldDraw(i,dt,fade){const f=fields[i],m=masks[i];if(active!==i){active=i;particles=Array.from({length:220},()=>{const p={};spawn(p,true);return p;});}
      ctx.save();ctx.globalAlpha=fade;ctx.imageSmoothingEnabled=true;ctx.drawImage(f.image,FIELD.x,FIELD.y,FIELD.w,FIELD.h);ctx.strokeStyle='#a7c9dc80';ctx.lineWidth=1;ctx.strokeRect(FIELD.x,FIELD.y,FIELD.w,FIELD.h);ctx.beginPath();ctx.rect(FIELD.x,FIELD.y,FIELD.w,FIELD.h);ctx.clip();
      // Tracer advection uses projected solved velocity, not a cosmetic flow pattern.
      ctx.strokeStyle='rgba(230,249,255,.65)';ctx.lineWidth=1.15;ctx.lineCap='round';ctx.beginPath();
      for(const p of particles){let v=velocity(f,p.x,p.z);if(!v||solid(m,p.x,p.z)||p.age>5){spawn(p);continue;}const d=dt*.0035, mx=p.x+v[0]*d*.5,mz=p.z+v[1]*d*.5;const mid=velocity(f,mx,mz)||v;const nx=p.x+mid[0]*d,nz=p.z+mid[1]*d;if(nx>=X1||nx<=X0||nz<=Z0||nz>=Z1||solid(m,nx,nz)||solid(m,mx,mz)){spawn(p);continue;}p.age+=dt;p.x=nx;p.z=nz;const tx=p.x-v[0]*.00025,tz=p.z-v[1]*.00025;if(!solid(m,tx,tz)){ctx.moveTo(px(tx),py(tz));ctx.lineTo(px(p.x),py(p.z));}}
      ctx.stroke();ctx.restore();
      label('FREESTREAM  120 mph  /  2112 in/s',30,113,17,'#d4e5ef',650);label('−Y  →',770,113,16,'#8bdcd7',700,'right');label('VELOCITY MAGNITUDE  |  in/s',30,474,13,'#d4e5ef',650);const lx=30,ly=486,lw=740,lh=14;const gradient=ctx.createLinearGradient(lx,0,lx+lw,0);for(const s of stops)gradient.addColorStop(s[0]/2300,'rgb('+s.slice(1).join(',')+')');ctx.fillStyle=gradient;ctx.fillRect(lx,ly,lw,lh);for(const v of [0,575,1150,1725,2300]){const x=lx+lw*v/2300;ctx.strokeStyle='#b5c8d4';ctx.beginPath();ctx.moveTo(x,ly+lh);ctx.lineTo(x,ly+lh+5);ctx.stroke();label(String(v),x,525,13,'#b5c8d4',500,v===0?'left':v===2300?'right':'center');}
    }
    function draw(dt){if(!ready)return;background();const horizontal=ease((t-4.0)/1.7),flow=t>=5.7,i=t<11.6?0:t<17.5?1:2;
      const centerX=mix(400,TAIL-MID*SCALE,horizontal),centerY=mix(310,CY,horizontal),scale=mix(61,SCALE,horizontal),rotation=Math.PI/2*(1-horizontal),alpha=ease((t-1.85)/.7);
      if(!flow){const join=ease((t-2.55)/1.25),offBody=.36*(1-join),offNose=-.9*(1-join);blueprint(bodyOutline,offBody,ease(t/.95),1-alpha);blueprint(noseOutline,offNose,ease((t-.65)/1.05),1-alpha);shaded(body,offBody,alpha,rotation,scale,centerX,centerY);shaded(noses[0],offNose,alpha,rotation,scale,centerX,centerY);
        hud(t<2.1?'01 / PROFILE REVEAL':t<4?'02 / ASSEMBLY':'03 / FLOW ALIGNMENT',t<2.1?'Original CAD silhouette · clean external outlines':t<4?'Finned body + interchangeable biconic nose':'Orthographic side view · fixed physical scale',t<4?'01 / 02':'02 / 02');}
      else{fieldDraw(i,dt,ease((t-5.7)/.55));shaded(body,0,1,0,scale,centerX,centerY);shaded(noses[i],0,1,0,scale,centerX,centerY);hud(LABELS[i]+' / '+(i+1)+' OF 3','Interpolated steady CFD slice · projected tracers slowed for display','Y–Z PLANE');}
    }
    async function init(){
      const load=(url,kind)=>fetch(url).then(r=>{if(!r.ok)throw Error(url+' returned '+r.status);return r[kind]();});
      const [raw,models]=await Promise.all([Promise.all(NAMES.map(n=>load('assets/cfd/'+n+'.json?v=1','json'))),Promise.all(NAMES.map(n=>load('assets/models/rocket/'+n+'.glb?v=2','arrayBuffer')))]);
      fields=raw.map(makeField);const cad=models.map(parseGLB);body=raster(cad[0].body,[165,181,195]);noses=cad.map(m=>raster(m.nose,[194,211,218]));
      bodyOutline=outline(body.mask);noseOutline=outline(noses[0].mask);masks=noses.map(n=>maskUnion(body.mask,n.mask));
      if(!masks.every(m=>m.alpha.some((v,i)=>i%4===3&&v>0)))throw Error('CAD projection is empty');
      ready=true;status.hidden=true;status.style.display='none';layer.style.display='block';old.style.visibility='hidden';caption.textContent='Original CAD · solved 120 mph CFD, interpolated center-plane · steady-flow tracers slowed';draw(0);player.dispatchEvent(new Event('loadedmetadata'));
    }
    function tick(now){raf=0;if(paused||!ready)return;const dt=last?Math.min((now-last)/1000,.05):0;last=now;t=Math.min(DURATION,t+dt);draw(dt);if(t>=DURATION){paused=true;ended=true;player.dispatchEvent(new Event('ended'));return;}raf=requestAnimationFrame(tick);}
    player.play=async()=>{if(ended)return;const e=++epoch;paused=false;layer.style.display='block';old.style.visibility='hidden';try{if(!initializing)initializing=init();await initializing;if(e!==epoch||paused)return;last=0;if(!raf)raf=requestAnimationFrame(tick);player.dispatchEvent(new Event('play'));}catch(err){if(e!==epoch)return;paused=true;failed=true;initializing=null;ready=false;layer.style.display='none';old.style.visibility='visible';caption.textContent='CAD poster · animation unavailable ('+String(err.message||err).slice(0,100)+'). Replay to retry.';console.error('Rocket showcase initialization:',err);player.dispatchEvent(new Event('error'));}};
    player.pause=()=>{epoch++;paused=true;if(raf)cancelAnimationFrame(raf);raf=0;last=0;player.dispatchEvent(new Event('pause'));};
    player.load=()=>{player.pause();t=0;ended=false;failed=false;active=-1;if(ready)draw(0);else{status.hidden=false;status.style.display='grid';status.textContent='Rocket aerodynamics · preparing original CAD and solved CFD';layer.style.display='block';old.style.visibility='hidden';}};
    return player;
  }
  window.createRocketShowcase=rocketController;
})();
