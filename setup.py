"""
Setup script for NAP CLI — Modo Imersivo.

Installs the `nap` command globally via pip.
Usage: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="nap-nexus",
    version="0.2.0",
    description="NAP - Nexus AI Platform: Modo Imersivo CLI",
    long_description="CLI interativo para orquestração de agentes de IA",
    author="NAP Team",
    python_requires=">=3.10",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "httpx>=0.27.0",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
    ],
    entry_points={
        "console_scripts": [
            "nap=cli.shell:main",
            "nap-v2=cli.v2.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Code Generators",
    ],
)