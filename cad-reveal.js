/* One original mesh, one camera; two simultaneous render passes. */
const stage=document.getElementById('cad-reveal-stage'),slider=document.getElementById('cad-reveal-slider'),reset=document.getElementById('cad-reveal-reset'),status=document.getElementById('cad-reveal-status');
async function init(){
const [THREE,{GLTFLoader},{OrbitControls}]=await Promise.all([import('three'),import('three/addons/loaders/GLTFLoader.js'),import('three/addons/controls/OrbitControls.js')]);
const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;renderer.autoClear=false;stage.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(35,1,.0001,10),solid=new THREE.Scene(),wire=new THREE.Scene();
solid.add(new THREE.HemisphereLight(0xffffff,0x778899,2));const light=new THREE.DirectionalLight(0xffffff,2.7);light.position.set(.12,.22,.16);solid.add(light);const fill=new THREE.DirectionalLight(0xffffff,1.0);fill.position.set(-.15,.02,.06);solid.add(fill);
const gltf=await new GLTFLoader().loadAsync(new URL('assets/helmet-light-mount.glb?v=2',location.href).href),model=gltf.scene;model.updateMatrixWorld(true);
const bounds=new THREE.Box3().setFromObject(model),center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),span=Math.max(size.x,size.y,size.z);
if(!Number.isFinite(span)||span<=0)throw Error('Invalid model bounds');
const solidGroup=new THREE.Group(),wireGroup=new THREE.Group();
model.traverse(obj=>{if(!obj.isMesh)return;const geo=obj.geometry.clone();geo.applyMatrix4(obj.matrixWorld);geo.translate(-center.x,-center.y,-center.z);const shade=new THREE.MeshStandardMaterial({color:0xa8b0b8,roughness:.56,metalness:.12});solidGroup.add(new THREE.Mesh(geo,shade));const dark=new THREE.MeshBasicMaterial({color:0x142c39,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1});wireGroup.add(new THREE.Mesh(geo,dark));const edges=new THREE.LineSegments(new THREE.WireframeGeometry(geo),new THREE.LineBasicMaterial({color:0x83dfda,transparent:true,opacity:.48}));wireGroup.add(edges);});
solid.add(solidGroup);wire.add(wireGroup);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,0,0);camera.position.set(span*1.55,span*1.25,span*2.15);controls.minDistance=span*.65;controls.maxDistance=span*6;controls.enableDamping=false;controls.update();controls.saveState();
let w=1,h=1;
function render(){const x=Math.round(w*Number(slider.value)/100);stage.style.setProperty('--split',slider.value+'%');renderer.setScissorTest(false);renderer.setViewport(0,0,w,h);renderer.clear();renderer.setScissorTest(true);if(x>0){renderer.setScissor(0,0,x,h);renderer.render(wire,camera);}if(x<w){renderer.setScissor(x,0,w-x,h);renderer.render(solid,camera);}renderer.setScissorTest(false);}
function resize(){w=stage.clientWidth||1;h=stage.clientHeight||1;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render();}
new ResizeObserver(resize).observe(stage);controls.addEventListener('change',render);slider.addEventListener('input',render);reset.addEventListener('click',()=>{controls.reset();render();});
slider.disabled=false;reset.disabled=false;stage.classList.add('ready');status.textContent='Move the slider to reveal the solid. Drag the model to rotate both views together.';resize();}
if(stage){const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();init().catch(()=>{stage.querySelector('canvas')?.remove();status.textContent='Interactive comparison unavailable. The original CAD image is shown instead.';});}},{rootMargin:'200px'});observer.observe(stage);}
