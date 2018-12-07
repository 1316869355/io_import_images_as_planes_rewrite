# Import Images as Planes (Re-Write)

This is a rewrite of the import images as planes add-on for Blender 2.8

## Why?
- This was my first ever python script. I should know a lot better how to structure the code now.
- The old script has gotten to be one really huge file.
This intends to remedy that.
- The render-engine distinction (Blender Internal -- Cycles) does not matter anymore.
- Also there are many features in one Operator in the old version.
The thinking is, that maybe it could be better to give more specialized operators with not as broad a range.
- Already image-planes can now also be created from image-texture nodes and from the Image-Editor.


## Mapping old features to the re-write
<!-- ![Kiku](devdocs/old_options.png) -->
<img align="right" src="devdocs/new-ui-1.png">



#### Material Settings:
- No more "use alpha" checkbox
  - uses alpha now based on bit depth of image (24 vs 32)
  - alpha blend mode stays

- Main Shaders now (easily extensible):
  - Emission
  - Diffuse
  - Principled

- Old Shadeless converted to checkbox
  - restrict to camera rays works for every material type now
  - not single use case anymore

- Overwrite material renamed
  - "Reuse existing datablock" seems more descriptive

<img align="right" src="devdocs/old_options.png">

#### Position Settings
The offset planes (when importing multiple images) import option is removed.
For now the new Grid Arange Operator is called in this case.
In my estimation this feature does not really belong in the import settings. The distribution is better handled as a second step in the viewport interactively.

New is the Origin Location Option. Either put the origin at the center or at one of the corners.

The Operator now uses the "AddObjectHelper" class which manages position and orientation in the standard way.

#### Plane Dimension Settings
For now the planes are always created with Y-Dimension of 1 with the X-Dimension scaled accordingly. Not really sure if those other options are really 
