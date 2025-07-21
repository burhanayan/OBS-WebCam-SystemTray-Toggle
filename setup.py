#!/usr/bin/env python3
"""
Setup script for OBS VirtualCam Tray Controller.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="obs-virtualcam-tray",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight system tray application for controlling OBS source visibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/burhanayan/obs-virtualcam-tray",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Desktop Environment :: Window Managers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "obs-tray=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 