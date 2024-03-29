from setuptools import setup, find_packages

setup(
    name='masks',
    version='0.1.1',
    packages=find_packages(),
    url='',
    license='Apache Public License',
    author='Paul K. Korir, PhD',
    author_email='pkorir@ebi.ac.uk, paulkorir@gmail.com',
    description='simple tool to create image masks',
    install_requires=['numpy', 'mrcfile'],
    entry_points={
        'console_scripts': [
            'masks = masks.main:main',
        ]
    },
)
