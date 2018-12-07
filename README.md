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
<img align="right" src="devdocs/old_options.png">


#### Import Options
- No thoughts yet if and how to bring back.
  - "Detect Sequences" checkbox seems necessary
  - "relative path" should also be similar to standard "Open image" [x]

#### Compositing Nodes:
- "Setup Corner Pin" should maybe be a secondary operator also?

#### Material Settings:
- No more "use alpha" checkbox
  - uses alpha now based on bit depth of image (24 vs 32)
  - alpha blend mode stays
  - this means alpha is now always autmatically used
- Main Shaders now:
  - Emission
  - Diffuse
  - Principled
  - (easily extensible)
- Old Shadeless converted to checkbox
  - restrict to camera rays works for every material type now
  - not single use case anymore
- Overwrite material renamed
  - "Reuse existing datablock" seems more descriptive


#### Position Settings
The offset planes (when importing multiple images) import option is removed.
For now the new "Grid Arange" Operator is called in this case.
In my estimation this feature does not really belong in the import settings. The distribution is better handled as a second step in the viewport interactively.

New is the Origin Location Option. Either put the origin at the center or at one of the corners.

The Operator now uses the "AddObjectHelper" class which manages position and orientation in the standard way.

<img align="right" src="devdocs/new-ui-1.png">

#### Plane Dimension Settings
For now the planes are always created with Y-Dimension of 1 with the X-Dimension scaled accordingly. Not really sure if those other options are really benificial.

#### Orientation Settings:
- handled by "AddObjectHelper" now
- "Track Camera" should also be a secondary Operator in the viewport.



## New Operators

#### image import operators
At the moment there are three operators:
- import images as planes [x]
  - the normal importing of images
- plane from image [x]
  - creates an image plane from the image in the image editor
- plane from texture [x]
  - creates an image plane from the selected image texture node in the node editor.

#### Grid Arange
Aranges selected objects in a 2d grid. Has widget to control number of rows. Still needs widgets to controll offsets.

#### Delete unused datablocks
One Operator for deleting (unused) images and one for materials. Mainly for devel. Can be turned of for release. Can also delete all datablocks of type.


## missing Operators
- Setup Corner pin
  - haven't even ever used that checkbox, need to see what it does
- Track Camera


## More thoughts
- maybe add an operator to apply the active image plane to the selected object as a decal
  - add geometry (real and or susurf modifier)
  - move to surface
  - add shrinkwrap