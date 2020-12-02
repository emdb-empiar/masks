# masks
simple tool to create image masks

## Installation
Install from source as follows:

```bash
pip install git+https://github.com/emdb-empiar/masks
```

## How to Use

```
# view help
~$ masks -h

# use default options: 10^2 image; 6^2 mask placed (2,2) from top left
~$ masks make [options]

# the 'make' utility makes masks
~$ masks make -h
usage: mask make [-h] [-v] [-d] [-I IMAGE_SIZE [IMAGE_SIZE ...]] [-M MASK_SIZE [MASK_SIZE ...]] [-P MASK_POS [MASK_POS ...]] [-V VISIBLE_VALUE] [-X MASK_VALUE] [--invert] [-D {2,3}] [-o OUTPUT] [-s {quad,ellipse}] [--input-image INPUT_IMAGE] [--output-image OUTPUT_IMAGE]

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
  --input-image INPUT_IMAGE
                        input file on which to apply the mask [None]
  --output-image OUTPUT_IMAGE
                        output file on which to the mask is applied [None]


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

3. Apply a mask to an image file by employing `--input-image` and `--output-image` options while creating the mask. To do this you will need to keep two points in mind:
    - You must **specify both the input and output files**; specifying one will fail.
    - You need to know the **dimensions of the input file** so that the mask matches. Use IMOD's `header` command on the input file:
    
        ```bash
        ~$ header emd_5625.map
        
        RO image file on unit   1 : emd_5625.map     Size=        687 K
        
        Number of columns, rows, sections .....      56      56      56
        Map mode ..............................    2   (32-bit real)              
        Start cols, rows, sects, grid x,y,z ...  -28   -28   -28      56     56     56
        Pixel spacing (Angstroms)..............   4.230      4.230      4.230    
        Cell angles ...........................   90.000   90.000   90.000
        Fast, medium, slow axes ...............    X    Y    Z
        Origin on x,y,z .......................    0.000       0.000       0.000    
        Minimum density .......................  -1.5000    
        Maximum density .......................   7.9407    
        Mean density ..........................  0.25216    
        RMS deviation from mean................  0.86932    
        tilt angles (original,current) ........   0.0   0.0   0.0   0.0   0.0   0.0
        Space group,# extra bytes,idtype,lens .        1        0        0        0
        
         1 Titles :
        ::::EMDATABANK.org::::EMD-5625::::                                             
        ```

    Now run the following to apply the mask:
    
    ```bash
    ~$ masks make -I 56 -M 20 -P 18 -D 3 --input-image emd_5625.map --output-image emd_5625_masked_ellipse.mrc -s ellipse
    created (20, 20, 20) mask in image (56, 56, 56) at position (18, 18, 18)
    masked image emd_5625.map as (20, 20, 20) mask in image (56, 56, 56) at position (18, 18, 18) written to emd_5625_masked_ellipse.mrc
    ```

## API

### Creating a mask
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

### Applying a mask to an image

The `Mask.apply(image)` and `Mask3D.apply(image)` methods apply the implied mask on image data.

```python
import mrcfile
from masks import Mask3D

mask = Mask3D(image_size=(56,)*3, mask_size=(20,)*3, mask_pos=(18,)*3, shape='ellipse')
with mrcfile.open('emd_5625.map') as mrc:
    image = mrc.data
    masked = mask.apply(image)
    # now write it out as a new file
    # this must be nested because we still refer to mrc
    with mrcfile.new('emd_5625_masked.map') as mrc2:
        mrc2.set_data(masked)
        mrc2.voxel_size = mrc.voxel_size
        mrc2.nstart = mrc.nstart
```
