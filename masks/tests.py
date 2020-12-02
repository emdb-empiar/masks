import os
import sys
import unittest
from io import StringIO

import numpy

from . import cli
from . import main


class TestCLI(unittest.TestCase):
    def test_default(self):
        args = cli.cli(f"masks make")
        self.assertEqual(args.command, 'make')
        self.assertEqual(args.image_size, (10, 10))
        self.assertEqual(args.mask_size, (6, 6))
        self.assertEqual(args.mask_pos, (2, 2))
        self.assertEqual(args.visible_value, 1.0)
        self.assertEqual(args.mask_value, 0.0)
        self.assertFalse(args.invert)
        self.assertEqual(args.dimension, 2)
        self.assertIsNone(args.output)
        self.assertEqual(args.shape, 'quad')
        self.assertIsNone(args.input_image)
        self.assertIsNone(args.output_image)

    def test_single_value(self):
        args = cli.cli(f"masks make -I 20")
        self.assertEqual(args.image_size, (20, 20))
        args = cli.cli(f"masks make -I 50 -M 20")
        self.assertEqual(args.mask_size, (20, 20))
        args = cli.cli(f"masks make -I 50 -P 20")
        self.assertEqual(args.mask_pos, (20, 20))

    def test_validate_dims(self):
        output = StringIO()
        sys.stdout = output
        sys.stderr = output
        with self.assertRaises(ValueError):
            cli.cli(f"masks make -I 10 -M 20")

    def test_visible_value(self):
        args = cli.cli(f"masks make -I 10 -M 5 -P 0 -V 3")
        mask = main.make_mask(args)
        self.assertEqual(mask[0, 0], 3.0)

    def test_mask_value(self):
        args = cli.cli(f"masks make -I 10 -M 5 -P 1 1 -X 9")
        mask = main.make_mask(args)
        self.assertEqual(mask[0, 0], 9.0)

    def test_3d(self):
        args = cli.cli(f"masks make -I 10 -M 6 -P 2 -D 3")
        self.assertEqual(args.image_size, (10, 10, 10))
        self.assertEqual(args.mask_size, (6, 6, 6))
        self.assertEqual(args.mask_pos, (2, 2, 2))

    def test_consistency(self):
        with self.assertRaises(ValueError):
            cli.cli(f"masks make -I 10 10 10 -M 6 6 -P 2 2 2 -D 3")
        with self.assertRaises(ValueError):
            cli.cli(f"masks make -I 10 10 10 -M 6 6 6 -P 2 2 -D 3")
        with self.assertRaises(ValueError):
            cli.cli(f"masks make -I 10 10 -M 6 6 6 -P 2 2 2 -D 3")

    def test_input_image(self):
        args = cli.cli(f"masks make --input-image file.mrc --output-image outfile.mrc")
        self.assertEqual(args.input_image, 'file.mrc')
        self.assertEqual(args.output_image, 'outfile.mrc')
        with self.assertRaises(ValueError):
            cli.cli(f"masks make --input-image file.mrc")
        with self.assertRaises(ValueError):
            cli.cli(f"masks make --output-image file.mrc")


class TestMain(unittest.TestCase):
    def test_make_mask(self):
        args = cli.cli(f"masks make")
        mask = main.make_mask(args)
        self.assertIsInstance(mask, main.ArgsMask)

    def test_make_3dmask(self):
        args = cli.cli(f"masks make -D 3")
        mask = main.make_mask(args)
        self.assertIsInstance(mask, main.ArgsMask3D)
        self.assertEqual(len(mask.mask.shape), 3)

    def test_output(self):
        self.assertFalse(os.path.exists('mask.txt'))
        args = cli.cli(f"masks make -o mask.txt")
        main.main()
        self.assertTrue(os.path.exists('mask.txt'))
        os.remove('mask.txt')

    def test_output3d(self):
        self.assertFalse(os.path.exists('mask.mrc'))
        args = cli.cli(f"masks make -D 3 -o mask.mrc")
        main.main()
        self.assertTrue(os.path.exists('mask.mrc'))
        os.remove('mask.mrc')

    def test_ellipse(self):
        cli.cli(f"masks make -I 40 20 -M 20 -P 20 -5 -s ellipse -o test.txt")
        main.main()
        os.system('cat test.txt')

    def test_ellipse3d(self):
        cli.cli(f"masks make -I 200 -M 100 -P 0 -s ellipse -D 3 -o ellipse3d.mrc")
        main.main()
        os.system('header ellipse3d.mrc')

    def test_mask_apply(self):
        args = cli.cli(f"masks make")
        mask = main.make_mask(args)
        image = numpy.random.rand(10, 10)
        masked = mask.apply(image)
        self.assertIsInstance(masked, numpy.ndarray)
        self.assertEqual(masked.shape, image.shape)
        self.assertEqual(masked.shape, mask.mask.shape)

    def test_mask_apply3d(self):
        args = cli.cli(f"masks make -I 3 -M 1 -P 1 -D 3")
        mask = main.make_mask(args)
        image = numpy.random.rand(*mask.mask.shape)
        masked = mask.apply(image)
        self.assertIsInstance(masked, numpy.ndarray)
        self.assertEqual(masked.shape, image.shape)
        self.assertEqual(masked.shape, mask.mask.shape)

    def test_input(self):
        try:
            os.remove('emd_5625_masked.map')
        except FileNotFoundError:
            pass
        self.assertFalse(os.path.exists('emd_5625_masked.map'))
        cli.cli(f"masks make -I 56 -M 20 -P 0 -D 3 --input-image emd_5625.map --output-image emd_5625_masked.map")
        main.main()
        self.assertTrue(os.path.exists('emd_5625_masked.map'))
        os.remove('emd_5625_masked.map')




if __name__ == '__main__':
    unittest.main()
