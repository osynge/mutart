from sys import version_info
from pymutart.__version__ import version

try:
    from setuptools import setup, find_packages
except ImportError:
	try:
            from distutils.core import setup
	except ImportError:
            from ez_setup import use_setuptools
            use_setuptools()
            from setuptools import setup, find_packages
# we want this module for nosetests
try:
    import multiprocessing
except ImportError:
    # its not critical if this fails though.
    pass

setup(name='mutart',
    version=version,
    description="Adds Album art to FLAC music files",
    long_description="""Adds album art to flac files (and maybe other formats later) using meta data retrieved from LastFM (and maybe other metadata servers later)""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[
       "mutagen",
        ],
    url = 'https://github.com/hepix-virtualisation/mutart',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    packages = ['pymutart'],
    scripts=['mutart'],
    data_files=[('/usr/share/doc/mutart-%s' % (version),[
        'README.md',
        'ChangeLog'
        ])],
    tests_require=[
        'coverage >= 3.0',
        'nose >= 1.1.0',
        'mock',
    ],
    setup_requires=[
        'nose',
    ],
    test_suite = 'nose.collector',
    )

