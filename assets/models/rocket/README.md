# Rocket assembly viewer assets

Export the eight original SolidWorks **assemblies** to GLB (or export to STEP/STL and convert to GLB with an appropriate CAD/mesh tool). Keep units and orientation consistent. Do not publish approximate reconstructions as original CAD.

Expected file names: blunt.glb, hemisphere.glb, biconic.glb, conic.glb, bowed.glb, elliptical.glb, parabolic.glb, ogive.glb.

Once actual files are added here, populate manifest.json with entries such as {"label":"Blunt","file":"blunt.glb"}. The public viewer is hidden while the manifest is empty.
