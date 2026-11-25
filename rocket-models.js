/* The section stays hidden until actual, verified GLB exports are available. */
(async function(){
  const section=document.getElementById('rocket-model-section');
  if(!section)return;
  const manifestURL=new URL('../assets/models/rocket/manifest.json',location.href);
  let entries;
  try { const response=await fetch(manifestURL); if(!response.ok)return; entries=await response.json(); } catch { return; }
  if(!Array.isArray(entries)||entries.length===0)return;
  const valid=entries.filter(item=>item&&typeof item.label==='string'&&typeof item.file==='string'&&/^[a-z0-9-]+\.glb$/.test(item.file));
  if(!valid.length)return;
  const module=document.createElement('script'); module.type='module'; module.src='https://ajax.googleapis.com/ajax/libs/model-viewer/4.4.0/model-viewer.min.js';
  document.head.append(module);
  const select=document.getElementById('rocket-profile'), viewer=document.getElementById('rocket-model'), link=document.getElementById('rocket-model-download'), status=document.getElementById('rocket-model-status');
  for(const item of valid){const option=document.createElement('option');option.value=item.file;option.textContent=item.label;select.append(option);}
  function update(){const selected=valid.find(x=>x.file===select.value);if(!selected)return;const url=new URL(selected.file,manifestURL).href;status.textContent='Loading '+selected.label+' assembly…';viewer.alt=selected.label+' rocket assembly';viewer.src=url;link.href=url;}
  viewer.addEventListener('load',()=>{status.textContent='Rotate or zoom to inspect the assembly.';});
  viewer.addEventListener('error',()=>{status.textContent='The model could not be loaded. Try downloading the GLB.';});
  select.addEventListener('change',update);module.addEventListener('error',()=>{status.textContent='Interactive viewer could not be loaded. The GLB download remains available.';});
  section.hidden=false;update();
})();
