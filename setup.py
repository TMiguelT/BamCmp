#!/usr/bin/env python3
from setuptools import setup

setup(
    name='bam_cmp',
    packages=['bam_cmp'],
    version='0.0.1',
    install_requires=[
        'pysam',
        'deepdiff'
    ],
    entry_points={
        'console_scripts': [
            'bamcmp = bam_cmp.bam_cmp:main'
        ]
    },
    test_suite="test"
)