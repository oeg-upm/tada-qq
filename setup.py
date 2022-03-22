import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = ("README.md").read_text()
README = "".join(README.split('\n')[7:])
# This call to setup() does all the work
setup(
    name="qq-plot",
    version="1.0.0",
    description="Quantile Quantile Plot with Linear Approximation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/oeg-upm/tada-qq",
    author="Ahmad Alobaid",
    author_email="aalobaid@fi.upm.es",
    license="Apache2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["qq", "slabelling"],
    include_package_data=True,
    install_requires=["pandas", "easysparql", "pcake"],
    # entry_points={
    #     "console_scripts": [
    #         "realpython=reader.__main__:main",
    #     ]
    # },
)