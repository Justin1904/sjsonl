from setuptools import setup, find_packages
from mypyc.build import mypycify

setup(
    name='sjsonl',
    version='0.1',
    packages=find_packages(include=['sjsonl']),
    ext_modules=mypycify([
        '--disallow-untyped-defs',
        'sjsonl/indexer.py',
        'sjsonl/dataset.py'
        ], opt_level="3", debug_level="1"),
)
