/* Original STEP-derived CAD sequence. No synthetic CFD fields. */
(() => {
  const slide = document.querySelector('[data-rocket-film]');
  if (!slide) return;
  const stage = slide.querySelector('.claw-film-stage');
  const video = stage.querySelector('video');
  const caption = slide.querySelector('figcaption span');
  const names = ['biconic', 'hemisphere', 'blunt'];
  const labels = ['Biconic', 'Hemisphere', 'Blunt'];
  let initializing = false;
  const clamp = x => Math.max(0, Math.min(1, x));
  const smooth = x => { x=clamp(x); return x*x*(3-2*x); };
  async function init() {
    if (initializing) return;
    initializing = true;
    let layer, renderer, resizeObserver, raf = 0;
    try {
      const [THREE, {GLTFLoader}] = await Promise.all([
        import('three'), import('three/addons/loaders/GLTFLoader.js')
      ]);
      const loader = new GLTFLoader();
      const models = await Promise.all(names.map(n => loader.loadAsync('assets/models/rocket/'+n+'.glb?v=2')));
      const body = models[0].scene.getObjectByName('Rocket body');
      const noses = models.map(m => m.scene.getObjectByName('Nose cone'));
      if (!body || noses.some(n => !n)) throw new Error('Assembly parts unavailable');
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0d1722);
      const camera = new THREE.OrthographicCamera(-1,1,1,-1,.001,10);
      camera.position.set(0,0,.65);
      camera.lookAt(0,0,0);
      renderer = new THREE.WebGLRenderer({antialias:true,alpha:false});
      renderer.setPixelRatio(Math.min(devicePixelRatio || 1,2));
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.1;
      scene.add(new THREE.HemisphereLight(0xdbeeff,0x354554,2.2));
      for (const [color,intensity,pos] of [[0xffffff,3.0,[.25,.35,.45]],[0x8dd5e3,1.3,[-.3,.1,.15]],[0xffffff,1.7,[.1,.2,-.3]]]) {
        const light = new THREE.DirectionalLight(color,intensity);
        light.position.set(...pos); scene.add(light);
      }
      const pivot = new THREE.Group(), assembly = new THREE.Group(), roll = new THREE.Group();
      scene.add(pivot); pivot.add(roll); roll.add(assembly);
      // All exported models share the body base at Y=0. Preserve that alignment.
      assembly.position.set(.005403,-.0777875,0);
      assembly.add(body,...noses);
      const bodyMat = new THREE.MeshStandardMaterial({color:0x8e9ca8,metalness:.12,roughness:.48});
      const noseMat = new THREE.MeshStandardMaterial({color:0xb7d3d8,metalness:.16,roughness:.42});
      body.traverse(o=>{if(o.isMesh)o.material=bodyMat;});
      noses.forEach(n=>n.traverse(o=>{if(o.isMesh)o.material=noseMat;}));
      layer = document.createElement('div');
      layer.style.cssText='position:absolute;inset:0;overflow:hidden;pointer-events:none;background:#0d1722;';
      renderer.domElement.style.cssText='position:absolute;inset:0;width:100%;height:100%;display:block;';
      layer.append(renderer.domElement);
      const hud = document.createElement('div');
      hud.style.cssText='position:absolute;inset:0;display:flex;flex-direction:column;justify-content:space-between;padding:14px 16px;color:#b7cbd6;font:600 clamp(9px,1.3vw,12px)/1.4 system-ui;letter-spacing:.055em;';
      const top = document.createElement('div'), bottom = document.createElement('div');
      top.style.cssText='display:flex;justify-content:space-between;gap:8px;align-items:flex-start;';
      bottom.style.cssText='display:flex;justify-content:space-between;gap:8px;align-items:flex-end;';
      const title = document.createElement('span'), phase = document.createElement('span');
      title.textContent='02 / ROCKET AERODYNAMICS'; phase.style.color='#8dded8';
      top.append(title,phase);
      const detail = document.createElement('span'), counter = document.createElement('span');
      detail.style.cssText='max-width:80%;letter-spacing:.02em;font-weight:500;'; counter.style.color='#8dded8';
      bottom.append(detail,counter); hud.append(top,bottom); layer.append(hud);
      // Keep the existing video as the carousel's playback clock and as a fallback.
      stage.append(layer);
      function draw(){
        const t = clamp(video.duration>0 && Number.isFinite(video.duration) ? video.currentTime/video.duration : 0);
        const horizontal = smooth((t-.27)/.17);
        const i=t<.64?0:t<.82?1:2;
        pivot.rotation.z = Math.PI/2 * horizontal;
        roll.rotation.y = (1-horizontal)*(.55 + .28*smooth(t/.27));
        body.position.y = -.035*(1-smooth(t/.12));
        noses.forEach((n,k)=>{n.visible=k===i;n.position.y=k===0?.04*(1-smooth((t-.09)/.17)):0;});
        pivot.position.y = -.012*(1-horizontal);
        if(t<.27){
          phase.textContent='01 / ASSEMBLY';
          detail.textContent='Original CAD · interchangeable nose + finned body';
          counter.textContent='01 / 04';
        } else if(t<.44){
          phase.textContent='02 / ALIGNMENT';
          detail.textContent='Rotating assembly into orthographic side view';
          counter.textContent='02 / 04';
        } else {
          phase.textContent=labels[i].toUpperCase()+' / SIDE VIEW';
          detail.textContent='Freestream: left to right · 120 mph test condition · CFD field pending';
          counter.textContent=(i+1)+' / 3';
        }
        renderer.render(scene,camera);
      }
      function resize(){
        const w=stage.clientWidth,h=stage.clientHeight;
        if(!w||!h)return;
        const a=w/h, half=Math.max(.128,.145/a);
        camera.left=-half*a;camera.right=half*a;camera.top=half;camera.bottom=-half;
        camera.updateProjectionMatrix();
        renderer.setSize(w,h,false);draw();
      }
      function frame(){raf=0;draw();if(!video.paused&&!video.ended&&!slide.hidden)raf=requestAnimationFrame(frame);}
      function start(){if(!raf)raf=requestAnimationFrame(frame);}
      function stop(){if(raf)cancelAnimationFrame(raf);raf=0;draw();}
      video.addEventListener('play',start);
      video.addEventListener('pause',stop);
      video.addEventListener('ended',stop);
      video.addEventListener('seeked',draw);
      video.addEventListener('loadedmetadata',draw);
      resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);
      caption.textContent='Original CAD assembly and fixed side-view profile comparison · CFD fields pending';
      video.setAttribute('aria-label','Biconic rocket assembly upright, rotates horizontally, then compares biconic, hemisphere and blunt profiles. CFD fields are not yet shown.');
      resize();start();
    } catch (error) {
      if(raf)cancelAnimationFrame(raf);
      resizeObserver?.disconnect();layer?.remove();renderer?.dispose();
      // The original, accurately labeled qualitative video remains available.
      console.warn('Rocket CAD film unavailable; using original video.',error);
    }
  }
  const observer = new MutationObserver(()=>{if(!slide.hidden){observer.disconnect();init();}});
  if(!slide.hidden)init();else observer.observe(slide,{attributes:true,attributeFilter:['hidden']});
})();
