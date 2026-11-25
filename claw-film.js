/* Pre-rendered films only; no scroll scrubbing, WebGL, or forced scrolling. */
(()=>{const root=document.getElementById('engineering-showcase');if(!root)return;
const slides=[...root.querySelectorAll('[data-showcase-slide]')],tabs=[...root.querySelectorAll('[data-showcase-select]')],videos=slides.map(s=>s.querySelector('video')),toggle=root.querySelector('[data-showcase-toggle]'),bar=root.querySelector('[data-showcase-progress]'),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let index=0,auto=!reduced,visible=false,hover=false,timer=0,epoch=0,manual=false;
const current=()=>videos[index];
const clear=()=>{clearTimeout(timer);timer=0;};
function updateToggle(){toggle.textContent=auto?'Pause slideshow':'Play slideshow';toggle.setAttribute('aria-pressed',String(!auto));}
function updateProgress(){const v=current();bar.style.transform='scaleX('+((Number.isFinite(v.duration)&&v.duration>0)?Math.min(1,v.currentTime/v.duration):0)+')';}
function mayPlay(){return visible&&!document.hidden&&!hover&&(auto||manual);}
function schedule(){clear();if(auto&&visible&&!hover&&!document.hidden){const e=epoch;timer=setTimeout(()=>{if(e===epoch&&auto&&visible&&!hover&&!document.hidden)show(index+1,false);},650);}}
function play(){const v=current(),e=epoch;if(!mayPlay())return;if(v.ended){if(auto&&!manual){schedule();return;}v.currentTime=0;}v.play().then(()=>{if(e!==epoch||!mayPlay())v.pause();}).catch(()=>{if(e!==epoch)return;auto=false;manual=false;updateToggle();});}
function sync(){clear();if(mayPlay())play();else current().pause();}
function show(next,user){clear();epoch++;current().pause();index=(next+slides.length)%slides.length;slides.forEach((s,i)=>{s.hidden=i!==index;s.classList.toggle('is-active',i===index);tabs[i].setAttribute('aria-pressed',String(i===index));});const v=current();if(v.readyState>0)v.currentTime=0;else v.load();manual=!!user&&!auto;bar.style.transform='scaleX(0)';sync();}
videos.forEach((v,i)=>{v.addEventListener('timeupdate',()=>{if(i===index)updateProgress();});v.addEventListener('ended',()=>{if(i!==index)return;manual=false;updateProgress();schedule();});v.addEventListener('error',()=>{if(i===index){manual=false;schedule();}});slides[i].querySelector('[data-showcase-replay]').addEventListener('click',()=>{clear();epoch++;v.currentTime=0;manual=!auto;sync();});});
tabs.forEach((b,i)=>b.addEventListener('click',()=>show(i,true)));root.querySelector('[data-showcase-prev]').addEventListener('click',()=>show(index-1,true));root.querySelector('[data-showcase-next]').addEventListener('click',()=>show(index+1,true));
toggle.addEventListener('click',()=>{auto=!auto;manual=false;updateToggle();if(auto&&current().ended)show(index+1,false);else sync();});
if(matchMedia('(hover:hover) and (pointer:fine)').matches)slides.forEach(s=>{const stage=s.querySelector('.claw-film-stage');stage.addEventListener('pointerenter',()=>{if(s.hidden)return;hover=true;sync();});stage.addEventListener('pointerleave',()=>{hover=false;sync();});});
document.addEventListener('visibilitychange',sync);
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{visible=entries.some(e=>e.isIntersecting);sync();},{threshold:.2});observer.observe(root);}else{visible=true;sync();}
updateToggle();updateProgress();
})();