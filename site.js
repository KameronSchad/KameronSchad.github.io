/* Progressive enhancement: project filters, ordering, section navigation, image lightbox and mobile nav. */
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
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&mobile.getAttribute('aria-expanded')==='true'){mobile.setAttribute('aria-expanded','false');nav.classList.remove('is-open');mobile.focus();}});
    nav.addEventListener('click',e=>{
      if(e.target.closest('a')){mobile.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}
    });
  }
  const filterPanel=document.querySelector('[data-filters]');
  if(filterPanel){
    const buttons=[...filterPanel.querySelectorAll('[data-filter]')];
    const cards=[...document.querySelectorAll('.project-card[data-category]')];
    const empty=document.querySelector('[data-filter-empty]');
    const search=document.querySelector('[data-project-search]');
    const apply=name=>{
      let count=0;
      cards.forEach(card=>{const query=(search?.value||'').toLowerCase().trim().split(/\s+/).filter(Boolean);const haystack=((card.dataset.search||'')+' '+card.textContent).toLowerCase();const visible=(name==='all'||card.dataset.category===name)&&query.every(word=>haystack.includes(word));card.hidden=!visible;if(visible)count++;});
      buttons.forEach(b=>{const active=b.dataset.filter===name;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
      if(empty)empty.hidden=count>0;
    };
    let current='all';
    const sorter=document.querySelector('[data-project-sort]');
    const grid=document.getElementById('project-list');
    const countLabel=document.querySelector('[data-project-count]');
    function filter(name){current=name;apply(name);const n=cards.filter(c=>!c.hidden).length;if(countLabel)countLabel.textContent=n+' '+(n===1?'project':'projects');}
    buttons.forEach(b=>b.addEventListener('click',()=>{filter(b.dataset.filter);history.replaceState(null,'',b.dataset.filter==='all'?location.pathname:location.pathname+'#'+b.dataset.filter);}));
    function fromHash(){const name=location.hash.slice(1);filter(buttons.some(b=>b.dataset.filter===name)?name:'all');}
    sorter?.addEventListener('change',()=>{const mode=sorter.value;const sorted=[...cards].sort((a,b)=>{const rank=Number(a.dataset.rank)-Number(b.dataset.rank);return mode==='featured'?rank:(mode==='newest'?Number(b.dataset.year)-Number(a.dataset.year):Number(a.dataset.year)-Number(b.dataset.year))||rank;});sorted.forEach(c=>grid?.appendChild(c));filter(current);});
    search?.addEventListener('input',()=>filter(current));
    fromHash();window.addEventListener('hashchange',fromHash);
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
  const toc=[...document.querySelectorAll('.case-toc a[href^="#"]')];
  if(toc.length&&'IntersectionObserver' in window){const tracked=toc.map(a=>({link:a,section:document.getElementById(a.hash.slice(1))})).filter(x=>x.section);let frame=0;const update=()=>{frame=0;let active=tracked[0];for(const x of tracked){if(x.section.getBoundingClientRect().top<=170)active=x;}for(const x of tracked){if(x===active)x.link.setAttribute('aria-current','location');else x.link.removeAttribute('aria-current');}};const onScroll=()=>{if(!frame)frame=requestAnimationFrame(update);};window.addEventListener('scroll',onScroll,{passive:true});update();}
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

/* Milestones: hover/focus previews on desktop, explicit disclosure on touch. */
(()=>{const rows=[...document.querySelectorAll('[data-milestone]')];if(!rows.length)return;const close= row=>{row.classList.remove('preview-open');row.querySelector('.milestone-toggle').setAttribute('aria-expanded','false');};for(const row of rows){const toggle=row.querySelector('.milestone-toggle');toggle.addEventListener('click',()=>{const open=!row.classList.contains('preview-open');rows.forEach(close);if(open){row.classList.add('preview-open');toggle.setAttribute('aria-expanded','true');}});row.addEventListener('keydown',e=>{if(e.key==='Escape'){close(row);row.querySelector('.milestone-dot').focus();row.classList.add('preview-dismissed');}});row.addEventListener('pointerenter',()=>row.classList.remove('preview-dismissed'));row.addEventListener('focusin',e=>{if(!row.contains(e.relatedTarget))row.classList.remove('preview-dismissed');});}document.addEventListener('click',e=>{if(!e.target.closest('[data-milestone]'))rows.forEach(close);});})();
