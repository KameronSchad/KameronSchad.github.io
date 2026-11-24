/* Progressive enhancement: project filters, carousel, image lightbox, mobile nav. */
(() => {
  const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const mobile=document.querySelector('[data-menu-toggle]');
  const nav=document.getElementById('main-navigation');
  if(mobile&&nav){
    mobile.addEventListener('click',()=>{
      const open=mobile.getAttribute('aria-expanded')!=='true';
      mobile.setAttribute('aria-expanded',String(open));
      nav.classList.toggle('is-open',open);
    });
    nav.addEventListener('click',e=>{
      if(e.target.closest('a')){mobile.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}
    });
  }
  const filterPanel=document.querySelector('[data-filters]');
  if(filterPanel){
    const buttons=[...filterPanel.querySelectorAll('[data-filter]')];
    const cards=[...document.querySelectorAll('.project-card[data-category]')];
    const empty=document.querySelector('[data-filter-empty]');
    const apply=name=>{
      let count=0;
      cards.forEach(card=>{const visible=name==='all'||card.dataset.category===name;card.hidden=!visible;if(visible)count++;});
      buttons.forEach(b=>{const active=b.dataset.filter===name;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
      if(empty)empty.hidden=count>0;
    };
    buttons.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.filter)));
  }
  const carousel=document.querySelector('[data-carousel]');
  if(carousel){
    const slides=[...carousel.querySelectorAll('[data-feature-slide]')];
    const tabs=document.querySelector('[data-carousel-tabs]');
    const prev=document.querySelector('[data-carousel-prev]');
    const next=document.querySelector('[data-carousel-next]');
    const pause=document.querySelector('[data-carousel-pause]');
    let active=0;let timer=null;let playing=!reduceMotion;
    if(slides.length&&tabs){
      slides.forEach((slide,i)=>{
        const button=document.createElement('button');button.type='button';
        button.textContent=slide.dataset.title||`Project ${i+1}`;
        button.setAttribute('aria-label',`Show ${slide.dataset.title||'project '+(i+1)}`);
        button.addEventListener('click',()=>{show(i);start();});tabs.appendChild(button);
      });
      const dots=[...tabs.querySelectorAll('button')];
      const show=i=>{
        active=(i+slides.length)%slides.length;
        slides.forEach((s,j)=>{s.hidden=j!==active;s.setAttribute('aria-hidden',String(j!==active));});
        dots.forEach((d,j)=>d.setAttribute('aria-current',String(j===active)));
      };
      const stop=()=>{clearInterval(timer);timer=null;};
      const start=()=>{stop();if(playing&&!document.hidden)timer=setInterval(()=>show(active+1),10000);};
      prev?.addEventListener('click',()=>{show(active-1);start();});
      next?.addEventListener('click',()=>{show(active+1);start();});
      const setPause=()=>{if(pause){pause.textContent=playing?'Pause':'Play';pause.setAttribute('aria-label',playing?'Pause slideshow':'Play slideshow');pause.setAttribute('aria-pressed',String(!playing));}};
      pause?.addEventListener('click',()=>{playing=!playing;setPause();start();});
      document.addEventListener('visibilitychange',start);
      carousel.addEventListener('focusin',stop);
      carousel.addEventListener('focusout',e=>{if(!carousel.contains(e.relatedTarget))start();});
      show(0);setPause();start();
    }
  }
  const dialog=document.getElementById('lightbox');
  if(dialog&&typeof dialog.showModal==='function'){
    const photo=dialog.querySelector('[data-lightbox-image]');
    const caption=dialog.querySelector('[data-lightbox-caption]');
    let origin;
    document.querySelectorAll('[data-lightbox]').forEach(a=>a.addEventListener('click',e=>{
      e.preventDefault();origin=a;photo.src=a.href;
      photo.alt=a.querySelector('img')?.alt||'Expanded project image';
      caption.textContent=a.dataset.caption||photo.alt;dialog.showModal();
    }));
    const close=()=>{dialog.close();photo.removeAttribute('src');origin?.focus();};
    dialog.querySelector('[data-lightbox-close]')?.addEventListener('click',close);
    dialog.addEventListener('click',e=>{if(e.target===dialog)close();});
    dialog.addEventListener('close',()=>{photo.removeAttribute('src');origin?.focus();});
  }
})();
