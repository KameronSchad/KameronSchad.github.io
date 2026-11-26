/* Hover holds the current slide AFTER playback ends. It never interrupts the film. */
(()=>{const root=document.getElementById('engineering-showcase');if(!root)return;
const slides=[...root.querySelectorAll('[data-showcase-slide]')],tabs=[...root.querySelectorAll('[data-showcase-select]')],videos=slides.map(s=>s.hasAttribute('data-rocket-film')&&typeof window.createRocketShowcase==='function'?window.createRocketShowcase(s):s.querySelector('video')),toggle=root.querySelector('[data-showcase-toggle]'),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const hoverCapable=matchMedia('(hover:hover) and (pointer:fine)').matches;
let index=0,auto=!reduced,visible=false,hover=false,focused=false,timer=0,epoch=0,manual=false,failed=false;
const current=()=>videos[index],clear=()=>{clearTimeout(timer);timer=0;};
function updateToggle(){toggle.textContent=auto?'Pause slideshow':'Play slideshow';toggle.setAttribute('aria-pressed',String(!auto));}
function canPlay(){return visible&&!document.hidden&&(auto||manual);}
function canAdvance(){return auto&&visible&&!hover&&!focused&&!document.hidden;}
function schedule(){clear();if(!canAdvance())return;const e=epoch;timer=setTimeout(()=>{if(e===epoch&&canAdvance()&&(current().ended||failed))show(index+1,false);},750);}
function play(){const v=current(),e=epoch;if(!canPlay())return;if(v.ended||failed){schedule();return;}if(!v.paused)return;v.play().then(()=>{if(e!==epoch||!canPlay())v.pause();}).catch(()=>{if(e!==epoch)return;auto=false;manual=false;updateToggle();});}
function sync(){clear();if(!canPlay()){current().pause();return;}if(current().ended||failed)schedule();else play();}
function show(next,user){clear();epoch++;current().pause();index=(next+slides.length)%slides.length;failed=false;
slides.forEach((s,i)=>{s.hidden=i!==index;s.classList.toggle('is-active',i===index);tabs[i].setAttribute('aria-pressed',String(i===index));});
const v=current();if(v.readyState>0)v.currentTime=0;else v.load();manual=!!user&&!auto;sync();}
videos.forEach((v,i)=>{v.addEventListener('ended',()=>{if(i!==index)return;manual=false;schedule();});v.addEventListener('error',()=>{if(i!==index)return;failed=true;manual=false;schedule();});slides[i].querySelector('[data-showcase-replay]').addEventListener('click',()=>{clear();epoch++;failed=false;if(v.error)v.load();else v.currentTime=0;manual=!auto;sync();});});
tabs.forEach((b,i)=>b.addEventListener('click',()=>show(i,true)));
root.querySelector('[data-showcase-prev]').addEventListener('click',()=>show(index-1,true));root.querySelector('[data-showcase-next]').addEventListener('click',()=>show(index+1,true));
toggle.addEventListener('click',()=>{auto=!auto;manual=false;updateToggle();sync();});
if(hoverCapable){root.addEventListener('pointerenter',()=>{hover=true;clear();});root.addEventListener('pointerleave',()=>{hover=false;if(current().ended||failed)schedule();});}
root.addEventListener('focusin',e=>{if(e.target.matches(':focus-visible')){focused=true;clear();}});
root.addEventListener('focusout',e=>{if(!root.contains(e.relatedTarget)){focused=false;if(current().ended||failed)schedule();}});
document.addEventListener('visibilitychange',sync);
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{visible=entries.some(e=>e.isIntersecting);if(hoverCapable)hover=root.matches(':hover');sync();},{threshold:.2});observer.observe(root);}else{visible=true;sync();}
updateToggle();
})();