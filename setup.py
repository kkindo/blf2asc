from setuptools import setup, find_packages

setup(
    name="blf2asc",
    version="2.0",
    url="https://github.com/kkindo/blf2asc",
    author="Kaoru Kindo",
    author_email="kaoru.kindo.private.work@gmail.com",
    description="",
    packages=find_packages(),
    install_requires=[
        "python-can==4.2.2",
        "argparse"
    ],
)
