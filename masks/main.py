import os
import re
import sys

import mrcfile
import numpy

from . import cli


class Mask:
    def __init__(self, image_size=(10, 10), mask_size=(6, 6), mask_pos=(2, 2), voxel_size=(1.0, 1.0), visible_value=1.0, mask_value=0.0,
                 shape='quad'):
        self.width, self.height = image_size
        self.mask_width, self.mask_height = mask_size
        self.pos_width, self.pos_height = mask_pos
        self.voxel_size = voxel_size
        self.visible_value = visible_value
        self.mask_value = mask_value
        self.shape = shape
        self.mask = self._create()

    def _create(self):
        if self.mask_value != 0.0:
            image = numpy.ones((self.height, self.width)) * self.mask_value
        else:
            image = numpy.zeros((self.height, self.width))
        if self.shape == 'quad':
            image[self.pos_height:self.mask_height + self.pos_height,
            self.pos_width:self.mask_width + self.pos_width] = self.visible_value
        elif self.shape == 'ellipse':
            # mask = numpy.zeros((self.mask_height, self.mask_width))
            image = numpy.zeros((self.height, self.width))
            radius = self.mask_width / 2
            for j in range(self.mask_height):
                for i in range(self.mask_width):
                    if (i - radius) ** 2 + (j - radius) ** 2 <= radius ** 2:
                        image[j + self.pos_height, i + self.pos_width] = self.visible_value
        return image

    def __str__(self):
        return str(self.mask)

    def __getitem__(self, item):
        return self.mask[item]

    def __setitem__(self, item, value):
        self.mask[item] = value

    def save(self, fn, *args, **kwargs):
        numpy.savetxt(fn, self.mask, fmt='%.4g', *args, **kwargs)

    def apply(self, image):
        return image * self.mask


class Mask3D:
    def __init__(self, image_size=(10, 10, 10), mask_size=(6, 6, 6), mask_pos=(2, 2, 2), voxel_size=(1.0, 1.0, 1.0), visible_value=1.0,
                 mask_value=0.0, shape='quad'):
        self.width, self.height, self.depth = image_size
        self.mask_width, self.mask_height, self.mask_depth = mask_size
        self.pos_width, self.pos_height, self.pos_depth = mask_pos
        self.voxel_size = voxel_size
        self.visible_value = visible_value
        self.mask_value = mask_value
        self.shape = shape
        self.mask = self._create()

    def _create(self):
        if self.mask_value != 0.0:
            image = numpy.ones((self.height, self.width, self.depth)) * self.mask_value
        else:
            image = numpy.zeros((self.height, self.width, self.depth))
        if self.shape == 'quad':
            image[self.pos_height:self.mask_height + self.pos_height,
            self.pos_width:self.mask_width + self.pos_width,
            self.pos_depth:self.mask_depth + self.pos_depth] = self.visible_value
        elif self.shape == 'ellipse':
            image = numpy.zeros((self.height, self.width, self.depth))
            radius = self.mask_width / 2
            print(f"{radius=}; {self.height}; {self.width}; {self.depth}")
            for k in range(self.mask_depth):
                for j in range(self.mask_height):
                    for i in range(self.mask_width):
                        if (i - radius) ** 2 + (j - radius) ** 2 + (k - radius) ** 2 <= radius ** 2:
                            image[j + self.pos_height, i + self.pos_width, k + self.pos_depth] = self.visible_value
        return image

    def __str__(self):
        return str(self.mask)

    def __getitem__(self, item):
        return self.mask[item]

    def __setitem__(self, item, value):
        self.mask[item] = value

    def save(self, fn, *args, **kwargs):
        if re.match(r".*\.(mrc|map|rec)$", fn, re.IGNORECASE):
            with mrcfile.new(fn, overwrite=True) as f:
                f.set_data(self.mask.astype(numpy.float32))
                # fixme: set the voxel size
                f.voxel_size = self.voxel_size

    def apply(self, image):
        return self.mask * image


class ArgsMask(Mask):
    def __init__(self, args):
        super().__init__(
            image_size=args.image_size,
            mask_size=args.mask_size,
            mask_pos=args.mask_pos,
            voxel_size=args.voxel_size,
            visible_value=args.visible_value,
            mask_value=args.mask_value,
            shape=args.shape,
        )
        self._args = args

    def save(self, *args, **kwargs):
        if self._args.output:
            super().save(self._args.output, *args, **kwargs)


class ArgsMask3D(Mask3D):
    def __init__(self, args):
        super().__init__(
            image_size=args.image_size,
            mask_size=args.mask_size,
            mask_pos=args.mask_pos,
            voxel_size=args.voxel_size,
            visible_value=args.visible_value,
            mask_value=args.mask_value,
            shape=args.shape,
        )
        self._args = args

    def save(self, *args, **kwargs):
        if self._args.output:
            super().save(self._args.output, *args, **kwargs)


def make_mask(args):
    if args.dimension == 2:
        mask = ArgsMask(args)
    elif args.dimension == 3:
        mask = ArgsMask3D(args)
    return mask


def handle_make(args):
    mask = make_mask(args)
    # deal with outputting the mask if needed
    if args.output:
        with open(args.output, 'w') as f:
            mask.save()
    else:
        if args.verbose:
            print(mask)
    print(
        f"created {args.mask_size} mask in image {args.image_size} at "
        f"position {args.mask_pos} with voxel size {args.voxel_size}",
        file=sys.stderr
    )
    # write images if needed
    if args.input_image:
        with mrcfile.open(args.input_image) as inmrc:
            image = inmrc.data
            masked = mask.apply(image)
            with mrcfile.new(args.output_image, overwrite=True) as outmrc:
                outmrc.set_data(masked.astype(numpy.float32))
                outmrc.voxel_size = inmrc.voxel_size
                outmrc.nstart = inmrc.nstart
        print(
            f"masked image {args.input_image} as {args.mask_size} mask in image {args.image_size} at position {args.mask_pos} written to {args.output_image}",
            file=sys.stderr)
    return os.EX_OK


def main():
    args = cli.parse_args()
    exit_status = os.EX_OK
    if args.command == 'make':
        return handle_make(args)
    return exit_status


if __name__ == '__main__':
    sys.exit(main())
