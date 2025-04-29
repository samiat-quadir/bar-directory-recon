"""Setup configuration for bar-directory-recon package."""
from setuptools import setup, find_packages

setup(
    name="bar-directory-recon",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
)