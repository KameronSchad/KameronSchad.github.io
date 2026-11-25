/* CAD animation and project media scrubbers. Ordinary page scrolling remains untouched. */
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
let threePromise;
const library=()=>threePromise??=Promise.all([import('three'),import('three/addons/loaders/GLTFLoader.js')]);
function onVisible(el,callback){if(!('IntersectionObserver' in window)){callback();return;}const o=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){o.disconnect();callback();}},{rootMargin:'150px'});o.observe(el);}
async function buildCAD(stage,file,cinematic=false){
  const [T,{GLTFLoader}]=await library();
  const gltf=await new GLTFLoader().loadAsync(new URL(file,location.href).href);
  const model=gltf.scene;model.updateMatrixWorld(true);
  const box=new T.Box3().setFromObject(model),center=box.getCenter(new T.Vector3()),size=box.getSize(new T.Vector3());
  const span=Math.max(size.x,size.y,size.z);if(!(span>0))throw Error('Invalid CAD bounds');
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.6));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.03;
  const scene=new T.Scene(),camera=new T.PerspectiveCamera(35,1,.005,100),group=new T.Group(),surfaces=[],lines=[];
  scene.add(group,new T.HemisphereLight(0xffffff,0x687483,1.65));
  for(const [pos,intensity] of [[[3,5,4],2.5],[[-3,1,2],.8],[[1,3,-4],1.3]]){const l=new T.DirectionalLight(0xffffff,intensity);l.position.set(...pos);scene.add(l);}
  model.traverse(obj=>{if(!obj.isMesh)return;const g=obj.geometry.clone();g.applyMatrix4(obj.matrixWorld);g.translate(-center.x,-center.y,-center.z);g.scale(1/span,1/span,1/span);const mat=new T.MeshStandardMaterial({color:0xa8b0b8,roughness:.57,metalness:.08,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});group.add(new T.Mesh(g,mat));surfaces.push(mat);
    if(cinematic){const edge=new T.LineBasicMaterial({color:0x9ce8e2,transparent:true,opacity:1,depthWrite:false});group.add(new T.LineSegments(new T.EdgesGeometry(g,18),edge));lines.push(edge);}
  });
  const dark=new T.Color(0x122c3a),gray=new T.Color(0xaeb7bf);
  let progress=0;
  function render(p=progress){
    progress=clamp(p);
    const mix=cinematic?smooth((progress-.16)/.68):1;
    for(const m of surfaces)m.color.copy(dark).lerp(gray,mix);
    for(const l of lines)l.opacity=1-mix*.96;
    if(cinematic){const theta=-.48+progress*1.03;camera.position.set(Math.sin(theta)*2.35,1.22-.24*progress,Math.cos(theta)*2.35);stage.style.setProperty('--phase',mix.toFixed(3));}
    else{const theta=.55+progress*Math.PI*2;camera.position.set(Math.sin(theta)*2.45,1.1,Math.cos(theta)*2.45);}
    camera.lookAt(0,0,0);renderer.render(scene,camera);
  }
  function resize(){const w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render();}
  stage.appendChild(renderer.domElement);new ResizeObserver(resize).observe(stage);resize();return render;
}
const cinematic=document.getElementById('cinematic-stage');
if(cinematic){onVisible(cinematic,async()=>{
 const slider=document.getElementById('cinematic-progress'),replay=document.getElementById('cinematic-replay'),status=document.getElementById('cinematic-status'),phase=document.getElementById('cinematic-phase'),percent=document.getElementById('cinematic-percent');
 try{const draw=await buildCAD(cinematic,'assets/helmet-light-mount.glb?v=2',true);cinematic.classList.add('is-ready');slider.disabled=false;replay.disabled=false;let animation=0;
 const update=p=>{p=clamp(p);draw(p);slider.value=Math.round(p*100);percent.textContent=String(Math.round(p*100)).padStart(2,'0')+'%';phase.textContent=p<.25?'01 / TECHNICAL LINEWORK':p<.83?'02 / SURFACE REVEAL':'03 / SHADED CAD';};
 const play=()=>{cancelAnimationFrame(animation);if(reduced){update(1);return;}const start=performance.now();const tick=t=>{const p=clamp((t-start)/2850);update(smooth(p));if(p<1)animation=requestAnimationFrame(tick);};animation=requestAnimationFrame(tick);};
 slider.addEventListener('input',()=>{cancelAnimationFrame(animation);update(Number(slider.value)/100);});replay.addEventListener('click',play);status.textContent='The animation plays when visible. Replay or scrub to inspect the transition.';play();
 }catch(e){cinematic.querySelector('canvas')?.remove();status.textContent='Interactive animation unavailable; original CAD image shown.';}
});}
const controllers=[];
document.querySelectorAll('[data-motion-kind]').forEach(card=>{
 const stage=card.querySelector('[data-motion-stage]'),range=card.querySelector('[data-motion-range]'),label=card.querySelector('[data-motion-label]'),kind=card.dataset.motionKind,frames=JSON.parse(card.dataset.motionFrames||'[]'),labels=JSON.parse(card.dataset.motionLabels||'[]');
 let draw=null,p=0,manual=false,ready=false,loading=false;
 function set(next){p=clamp(next);range.value=Math.round(p*100);if(draw)draw(p);}
 async function init(){
 if(ready||loading)return;loading=true;
 try{
 if(kind==='cad'){const render=await buildCAD(stage,card.dataset.motionFile);stage.dataset.liveCad='true';stage.classList.add('is-ready');draw=x=>{render(x);label.textContent='Rotation · '+Math.round(x*360)+'°';};}
 else if(kind==='video'){
   const video=document.createElement('video');video.muted=true;video.playsInline=true;video.preload='metadata';video.poster=frames[0];video.src=card.dataset.motionFile;video.setAttribute('aria-label','Original class testing footage');stage.append(video);
   await new Promise((resolve,reject)=>{if(video.readyState>=1)return resolve();video.addEventListener('loadedmetadata',resolve,{once:true});video.addEventListener('error',reject,{once:true});});
   draw=x=>{if(Number.isFinite(video.duration)){const time=x*Math.max(0,video.duration-.06);if(Math.abs(video.currentTime-time)>.045)video.currentTime=time;label.textContent='Test footage · '+time.toFixed(1)+' s';}};
 }else if(kind==='detail'){
   const img=stage.querySelector('img');draw=x=>{img.style.setProperty('transform','scale('+(1+x*1.1)+')','important');img.style.transformOrigin='50% 48%';label.textContent=x<.45?labels[0]:labels[1];};
 }else{
   const first=stage.querySelector('img'),second=first.cloneNode();second.className='motion-second';second.alt='';second.setAttribute('aria-hidden','true');stage.insertBefore(second,stage.querySelector('.card-number'));
   const loaded=frames.map(src=>{const img=new Image();img.src=src;return img;});
   draw=x=>{const idx=x*(frames.length-1),i=Math.min(Math.floor(idx),frames.length-1),j=Math.min(i+1,frames.length-1),blend=idx-i;if(first.getAttribute('src')!==frames[i])first.src=frames[i];if(second.getAttribute('src')!==frames[j])second.src=frames[j];first.alt=labels[i];second.style.opacity=loaded[j].complete&&loaded[j].naturalWidth?String(blend):'0';label.textContent=labels[blend>.55?j:i];};
 }
 ready=true;range.disabled=false;set(p);
 }catch(e){stage.querySelector('canvas')?.remove();stage.querySelector('video')?.remove();label.textContent='Static preview · open full case study';}
 finally{loading=false;}
 }
 onVisible(card,init);
 range.addEventListener('input',()=>{manual=true;set(Number(range.value)/100);});
 stage.addEventListener('wheel',e=>{if(!ready||reduced||e.ctrlKey||e.metaKey)return;manual=true;set(p+e.deltaY/700);},{passive:true});
 controllers.push(()=>{if(!ready||manual||reduced||card.hidden)return;const rect=card.getBoundingClientRect(),vh=innerHeight;if(rect.bottom<0||rect.top>vh)return;set((vh-rect.top)/(vh+rect.height*.36));});
});
let frame=0;
function scrollUpdate(){frame=0;controllers.forEach(fn=>fn());const nav=document.getElementById('main-navigation');if(!nav)return;const links=[...nav.querySelectorAll('a[href^="#"]')];let active=links[0];for(const link of links){const section=document.getElementById(link.hash.slice(1));if(section&&section.getBoundingClientRect().top<=145)active=link;}if(innerHeight+scrollY>=document.documentElement.scrollHeight-30)active=links.at(-1);for(const link of links){if(link===active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');}}
function requestUpdate(){if(!frame)frame=requestAnimationFrame(scrollUpdate);}
window.addEventListener('scroll',requestUpdate,{passive:true});window.addEventListener('resize',requestUpdate,{passive:true});requestUpdate();
document.querySelectorAll('[data-home-filter]').forEach(a=>a.addEventListener('click',()=>{document.querySelector('[data-filter="'+a.dataset.homeFilter+'"]')?.click();}));
