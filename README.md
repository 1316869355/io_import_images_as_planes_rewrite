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
