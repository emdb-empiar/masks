import argparse
import shlex
import sys

# a global variable
parser = argparse.ArgumentParser(prog='mask', description='simple tool to create image masks')
# parent_parser
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-v', '--verbose', default=False, action='store_true',
                           help="verbose output to terminal in addition to log files [default: False]")
parent_parser.add_argument('-d', '--debug', default=False, action='store_true', help='debug [False]')
# subparsers
subparsers = parser.add_subparsers(dest='command', title='Tools', help='masks utilities')
# init
make_parser = subparsers.add_parser(
    'make',
    description='make an image mask',
    help='make mask',
    parents=[parent_parser]
)
make_parser.add_argument('-I', '--image-size', nargs='+', default=(10,), type=int, help='image size [10,10]')
make_parser.add_argument('-M', '--mask-size', nargs='+', default=(6,), type=int, help='mask size [6,6]')
make_parser.add_argument('-P', '--mask-pos', nargs='+', default=(2,), type=int, help='mask position [2,2]')
make_parser.add_argument('-V', '--visible-value', default=1.0, type=float, help='visible value [1.0]')
make_parser.add_argument('-X', '--mask-value', default=0.0, type=float, help='mask value [0.0]')
# make_parser
make_parser.add_argument('--invert', default=False, action='store_true', help='invert [False]')
make_parser.add_argument('-D', '--dimension', default=2, choices=[2, 3], type=int, help='dimensions [2]')
make_parser.add_argument('-o', '--output', help='output file [None]')
make_parser.add_argument('-s', '--shape', default='quad', choices=['quad', 'ellipse'], help="mask shape ['quad']")


def _validate3d(args):
    i_h, i_w, i_d = args.image_size
    m_h, m_w, m_d = args.mask_size
    p_h, p_w, p_d = args.mask_pos
    # height
    try:
        assert i_h >= m_h + p_h
    except AssertionError:
        raise ValueError(f"mask vertical position ({p_h}) and height ({m_h}) incompatible with image height ({i_h})")
    # width
    try:
        assert i_w >= m_w + p_w
    except AssertionError:
        raise ValueError(f"mask horizontal position ({p_w}) and width ({m_w}) incompatible with image width ({i_w})")
    # depth
    try:
        assert i_d >= m_d + p_d
    except AssertionError:
        raise ValueError(f"mask depth position ({p_d}) and depth ({m_d}) incompatible with image depth ({i_d})")


def _validate2d(args):
    i_h, i_w = args.image_size
    m_h, m_w = args.mask_size
    p_h, p_w = args.mask_pos
    # height
    try:
        assert i_h >= m_h + p_h
    except AssertionError:
        raise ValueError(f"mask vertical position ({p_h}) and height ({m_h}) incompatible with image height ({i_h})")
    # width
    try:
        assert i_w >= m_w + p_w
    except AssertionError:
        raise ValueError(f"mask horizontal position ({p_w}) and width ({m_w}) incompatible with image width ({i_w})")


def parse_args():
    """Parse CLI args"""
    args = parser.parse_args()
    if args.command == 'make':
        if len(args.image_size) == 1:
            args.image_size = (args.image_size[0],) * args.dimension
        if len(args.mask_size) == 1:
            args.mask_size = (args.mask_size[0],) * args.dimension
        if len(args.mask_pos) == 1:
            args.mask_pos = (args.mask_pos[0],) * args.dimension
        # ensure consistency
        try:
            assert len(args.image_size) == len(args.mask_size) == len(args.mask_pos)
        except AssertionError:
            raise ValueError(f"inconsistent dimensions: image={args.image_size}; mask={args.mask_size}; pos={args.mask_pos}")
        # validate
        if args.dimension == 2:
            _validate2d(args)
        elif args.dimension == 3:
            _validate3d(args)
    else:
        parser.print_help()
    return args


def cli(cmd):
    sys.argv = shlex.split(cmd)
    return parse_args()
