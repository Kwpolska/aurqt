#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='aurqt',
      version='0.1.1',
      description='A graphical AUR manager.',
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
      packages=['aurqt', 'aurqt.ui'],
      requires=['pkgbuilder', 'requests', 'bs4'],
      scripts=['bin/aurqt'],
      data_files=[('share/man/man8', ['docs/aurqt.8.gz']),
                  ('share/icons/hicolor/16x16/apps', ['icons/16/aurqt.png']),
                  ('share/icons/hicolor/22x22/apps', ['icons/22/aurqt.png']),
                  ('share/icons/hicolor/32x32/apps', ['icons/32/aurqt.png']),
                  ('share/icons/hicolor/48x48/apps', ['icons/48/aurqt.png']),
                  ('share/icons/hicolor/96x96/apps', ['icons/96/aurqt.png']),
                  ('share/icons/hicolor/128x128/apps', ['icons/128/aurqt.png']),
                  ('share/icons/hicolor/256x256/apps', ['icons/256/aurqt.png']),
                  ('share/icons/hicolor/scalable/apps', ['icons/aurqt.svg']),
                  ('share/applicatons', ['aurqt.desktop'])])
