import os
import sys

import mrcfile
import numpy

from . import cli


class Mask:
    def __init__(self, image_size=(10, 10), mask_size=(6, 6), mask_pos=(2, 2), visible_value=1.0, mask_value=0.0,
                 shape='quad'):
        self.width, self.height = image_size
        self.mask_width, self.mask_height = mask_size
        self.pos_width, self.pos_height = mask_pos
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


class Mask3D:
    def __init__(self, image_size=(10, 10, 10), mask_size=(6, 6, 6), mask_pos=(2, 2, 2), visible_value=1.0,
                 mask_value=0.0, shape='quad'):
        self.width, self.height, self.depth = image_size
        self.mask_width, self.mask_height, self.mask_depth = mask_size
        self.pos_width, self.pos_height, self.pos_depth = mask_pos
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
        fn_list = fn.split('.')
        fn_root, ext = '.'.join(fn_list[:-1]), fn_list[-1]
        if ext in ['mrc', 'map', 'rec']:
            with mrcfile.new(fn, overwrite=True) as f:
                f.set_data(self.mask.astype(numpy.float32))


class ArgsMask(Mask):
    def __init__(self, args):
        super().__init__(
            image_size=args.image_size,
            mask_size=args.mask_size,
            mask_pos=args.mask_pos,
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


def main():
    args = cli.parse_args()
    exit_status = os.EX_OK
    if args.command == 'make':
        mask = make_mask(args)
        if args.output:
            with open(args.output, 'w') as f:
                mask.save()
        else:
            if args.verbose:
                print(mask)
        print(f"created {args.mask_size} mask in image {args.image_size} at position {args.mask_pos}", file=sys.stderr)
    return exit_status


if __name__ == '__main__':
    sys.exit(main())
