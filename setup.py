from setuptools import setup
from smartbets_API import __version__, __author__


def get_file(nm: str) -> list:
    with open(nm) as file:
        return file.readlines()


setup(
    name="smartbetsAPI",
    packages=["smartbets_API"],
    version=__version__,
    url="https://github.com/Simatwa/smartbetsAPI",
    license="GPL-3.0",
    author=__author__,
    author_email="smartwacaleb@gmail.com",
    maintainer="Smartwa Caleb",
    maintainer_email="smartwacaleb@gmail.com",
    description="Simple football prediction API",
    long_description="\n".join(get_file("README.md")),
    long_description_content_type="text/markdown",
    install_requires=[
        "Flask==2.2.2",
        "appdirs==1.4.4",
        "requests==2.28.1",
        "colorama==0.4.6",
        "bs4==0.0.1",
        "Faker==15.3.4",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    keywords=[
        "Football",
        "Predictions",
        "Betting API",
        "Soccer predictions",
        "Football Predictions",
    ],
    entry_points={
        "console_scripts": ["smartbetsAPI = smartbets_API.interface:start_server"],
    },
)
