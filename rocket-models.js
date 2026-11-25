/* A single persistent camera and scene for all original STEP-derived meshes. */
const section = document.getElementById('rocket-model-section');
const select = document.getElementById('rocket-profile');
const download = document.getElementById('rocket-model-download');
const reset = document.getElementById('rocket-reset');
const viewport = document.getElementById('rocket-model');
const status = document.getElementById('rocket-model-status');
const modelDir = new URL('../assets/models/rocket/', location.href);
const allowed = new Set(['blunt','hemisphere','biconic','conic','bowed','elliptical','parabolic','ogive']);
function updateDownload(){
  if(allowed.has(select.value)) download.href = new URL(select.value+'.step', modelDir).href;
}
select.addEventListener('change',updateDownload);
updateDownload();
async function init(){
  const [THREE,{GLTFLoader},{OrbitControls}] = await Promise.all([
    import('three'), import('three/addons/loaders/GLTFLoader.js'), import('three/addons/controls/OrbitControls.js')
  ]);
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(35,1,0.001,10);
  const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.05;
  viewport.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-label','Drag to rotate, scroll or pinch to zoom, right-drag or two-finger drag to pan');
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=false;controls.minDistance=0.07;controls.maxDistance=1.2;
  controls.target.set(0,0.0778,0);
  camera.position.set(0.18,0.15,0.27);
  controls.update();controls.saveState();
  scene.add(new THREE.HemisphereLight(0xffffff,0x828282,1.8));
  const key=new THREE.DirectionalLight(0xffffff,2.0);key.position.set(0.3,0.45,0.4);scene.add(key);
  const fill=new THREE.DirectionalLight(0xffffff,0.65);fill.position.set(-0.35,0.15,0.1);scene.add(fill);
  const rim=new THREE.DirectionalLight(0xffffff,1.0);rim.position.set(0.1,0.25,-0.4);scene.add(rim);
  const render=()=>renderer.render(scene,camera);
  const resize=()=>{const w=viewport.clientWidth,h=viewport.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render();};
  new ResizeObserver(resize).observe(viewport);
  controls.addEventListener('change',render);
  reset.addEventListener('click',()=>{controls.reset();render();});
  viewport.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(e.key))return;e.preventDefault();const offset=camera.position.clone().sub(controls.target);const sph=new THREE.Spherical().setFromVector3(offset);if(e.key==='ArrowLeft')sph.theta-=0.12;if(e.key==='ArrowRight')sph.theta+=0.12;if(e.key==='ArrowUp')sph.phi-=0.12;if(e.key==='ArrowDown')sph.phi+=0.12;if(e.key==='+'||e.key==='=')sph.radius*=0.9;if(e.key==='-')sph.radius*=1.1;sph.makeSafe();sph.radius=THREE.MathUtils.clamp(sph.radius,controls.minDistance,controls.maxDistance);camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(sph));controls.update();render();});
  const loader=new GLTFLoader(),cache=new Map();
  function getModel(name){
    if(!cache.has(name)){
      const promise=loader.loadAsync(new URL(name+'.glb?v=2',modelDir).href).then(gltf=>gltf.scene);
      cache.set(name,promise);promise.catch(()=>cache.delete(name));
    }
    return cache.get(name);
  }
  let displayed=null,request=0;
  async function switchProfile(){
    const name=select.value;if(!allowed.has(name))return;
    const seq=++request;
    status.textContent='Loading '+select.selectedOptions[0].textContent+' assembly…';
    try{
      const model=await getModel(name);
      if(seq!==request)return;
      // Do not fit, re-center, re-orient or modify the camera. Only swap geometry.
      if(displayed)scene.remove(displayed);
      scene.add(model);displayed=model;render();
      status.textContent='Rotate, pan or zoom. Your view is preserved when changing profiles.';
    }catch(e){if(seq===request)status.textContent='Unable to load the selected model. The STEP download is still available.';}
  }
  select.addEventListener('change',switchProfile);
  resize();await switchProfile();
  // Cache alternatives after the first model is visible, while keeping it interactive.
  for(const name of allowed){if(name!==select.value){try{await getModel(name);}catch{}}}
}
init().catch(()=>{status.textContent='The 3D viewer could not start. Select a profile and download its original STEP assembly.';reset.disabled=true;});
