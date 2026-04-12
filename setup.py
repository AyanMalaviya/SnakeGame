#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Linked List Snake game.
Supports both Windows and Linux packaging.
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='linked-list-snake',
    version='1.0.0',
    description='A Linked List Snake game built with Pygame',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/SnakeGame',
    python_requires='>=3.8',
    py_modules=['main'],
    install_requires=[
        'pygame>=2.1.0',
    ],
    entry_points={
        'console_scripts': [
            'linked-list-snake=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Games/Entertainment',
    ],
)
