# masks
simple tool to create image masks

## Installation
Install from source as follows:

```bash
pip install https://github.com/emdb-empiar/masks
```

## How to Use

```
# view help
~$ masks -h

# use default options: 10^2 image; 6^2 mask placed (2,2) from top left
~$ masks make [options]

# the 'make' utility makes masks
~$ masks make -h
usage: mask make [-h] [-v] [-d] [-I IMAGE_SIZE [IMAGE_SIZE ...]] [-M MASK_SIZE [MASK_SIZE ...]] [-P MASK_POS [MASK_POS ...]] [-V VISIBLE_VALUE] [-X MASK_VALUE] [--invert]
                 [-D {2,3}] [-o OUTPUT] [-s {quad,ellipse}]

make an image mask

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output to terminal in addition to log files [default: False]
  -d, --debug           debug [False]
  -I IMAGE_SIZE [IMAGE_SIZE ...], --image-size IMAGE_SIZE [IMAGE_SIZE ...]
                        image size [10,10]
  -M MASK_SIZE [MASK_SIZE ...], --mask-size MASK_SIZE [MASK_SIZE ...]
                        mask size [6,6]
  -P MASK_POS [MASK_POS ...], --mask-pos MASK_POS [MASK_POS ...]
                        mask position [2,2]
  -V VISIBLE_VALUE, --visible-value VISIBLE_VALUE
                        visible value [1.0]
  -X MASK_VALUE, --mask-value MASK_VALUE
                        mask value [0.0]
  --invert              invert [False]
  -D {2,3}, --dimension {2,3}
                        dimensions [2]
  -o OUTPUT, --output OUTPUT
                        output file [None]
  -s {quad,ellipse}, --shape {quad,ellipse}
                        mask shape ['quad']

```

### Examples
1. Make a spherical 3D mask with a radius of 50 voxels in a 160^3 volume at the center and output it to an MRC file called `my_mask`

```
# verbose
~$ masks make --dimension 3 --image-size 160 160 160 --mask-size 100 100 100 --mask-pos 30 30 30 --shape ellipse --output my_mask.mrc --verbose
# or abbreviated
~$ masks make -D 3 -I 160 -M 100 -P 30 -s ellipse -o my_mask.mrc -v
```

2. Make a rectangular 2D mask which is 40wx20h in a 300wx200h at position (60,60) from the top left corner and save it as a text file called 'simple_mask.txt'.

```
# verbose
~$ masks make --image-size 300 200 --mask-size 40 20 --mask-pos 60 60 --output simple_mask.txt --verbose
# abbreviated
~$ masks make -I 300 200 -M 40 20 -P 60 -o simple_mask.txt -v
```



## API

There are two main classes: `Mask` and `Mask3D`

```python
from masks import Mask, Mask3D

m = Mask() # uses defaults: 10x10 image, 6x6 mask placed at (2,2) from top left
m = Mask(image_size=(100, 100), mask_size=(30,30), mask_pos=(0, 0)) # 30^2 mask in an 100^2 image placed at the origin

# 3D
m3 = Mask() # defaults: 10^3 volume, 6^3 mask placed at (2,2,2) from top corner
m3 = Mask(image_size=(100, 100, 100), mask_size=(30, 30, 30), mask_pos=(20, 20, 10))
```

By default it creates a cuboid mask with all internal values set to 1.0 and external values set to 0.0
Create an ellipsoidal mask by specifying the `shape` argument to `'ellipse'`.

```
m3 = Mask(shape='ellipse')
```
