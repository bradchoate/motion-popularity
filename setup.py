#!/usr/bin/env python

from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='motion-popularity',
    version='1.0',
    description='Provides a view to popular/active posts',
    author='Brad Choate',
    author_email='brad@bradchoate.com',
    url='http://github.com/bradchoate/motion-popularity',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],

    packages=['popularity'],
    include_package_data=True,
    zip_safe=False,
    requires=['motion'],
    install_requires=['motion'],
)
