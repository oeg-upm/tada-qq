import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
with open("README.md") as f:
    README = f.read()
    lines = README.split('\n')
    desc_lines = [line for line in lines if line[:2] != "[!"]
    README = "\n".join(desc_lines)
# This call to setup() does all the work
setup(
    name="tada-qq",
    version="2.0.2",
    description="Quantile Quantile Plot with Linear Approximation and Semantic Labelling of Numeric Columns",
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
    packages=["tadaqq.qq", "tadaqq.slabel"],
    include_package_data=True,
    install_requires=["pandas", "easysparql", "pcake"]
)
