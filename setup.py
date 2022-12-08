from setuptools import setup, find_packages

VERSION = "0.1"
DESCRIPTION = "General structure optimizer leveraging AI."


with open("requirements.txt") as f:
    required = f.read().splitlines()

# Setting up
setup(
    name="theeng",
    version=VERSION,
    author="Massimo Brivio",
    author_email="m.g.brivio@gmail.ch",
    description=DESCRIPTION,
    packages=find_packages(where=".", include=["theeng*"]),
    long_description_content_type="text/markdown",
    long_description="The Eng is a Python library for dealing with structural optimization.",
    install_requires=required,
    url="",
)

# 1 python setup.py sdist bdist
# 2 twine upload --repository testpypi dist/*
# 3 twine upload dist/* --> only for final release
