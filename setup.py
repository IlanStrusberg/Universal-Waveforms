from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="UniversalWaveforms",
    version="0.1",
    author="Ilan Strusberg, Bark Rom and Re'em Sari",
    author_email="ilan.strusberg@mail.hujo.ac.il",
    description="A package for generating and analyzing the dominant mode of the universal gravitational waveforms.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IlanStrusberg/Universal-Waveforms.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=[
        "numpy",
        "matplotlib",
        "pytest"
    ],
    python_requires=">=3.6",
)
