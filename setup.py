#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='aurqt',
      version='0.1.0',
      description='INSERT TAGLINE HERE.',
      author='Kwpolska',
      author_email='kwpolska@kwpolska.tk',
      url='https://github.com/Kwpolska/aurqt',
      license='3-clause BSD',
      long_description=open('./docs/README.rst').read(),
      platforms='Arch Linux',
      classifiers=['Development Status :: 1 - Planning',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Topic :: System',
                   'Topic :: System :: Archiving :: Packaging',
                   'Topic :: Utilities'],
      packages=['aurqt'],
      requires=['pkgbuilder', 'requests'],
      scripts=['bin/pkgbuilder', 'bin/pb'],
      data_files=[('share/man/man8', ['docs/pkgbuilder.8.gz']),
                  ('share/man/man8', ['docs/pb.8.gz']),
                  ('share/locale/en/LC_MESSAGES', ['locale/en/LC_MESSAGES/\
pkgbuilder.mo']),
                  ('share/locale/pl/LC_MESSAGES', ['locale/pl/LC_MESSAGES/\
pkgbuilder.mo'])])