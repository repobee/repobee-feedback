import re
from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

# parse the version instead of importing it to avoid dependency-related crashes
with open("repobee_feedback/__version.py", mode="r", encoding="utf-8") as f:
    line = f.readline()
    __version__ = line.split("=")[1].strip(" '\"\n")
    assert re.match(r"^\d+(\.\d+){2}(-(alpha|beta|rc)(\.\d+)?)?$", __version__)

test_requirements = ["pytest", "pytest-cov", "repobee"]
required = ["repobee-plug>=0.10.0", "daiquiri"]

setup(
    name="repobee-feedback",
    version=__version__,
    description="A plugin that adds the issue-feedback command to RepoBee",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simon Larsén",
    author_email="slarse@kth.se",
    url="https://github.com/slarse/repobee-feedback",
    download_url="https://github.com/"
    "slarse"
    "/repobee-feedback"
    "/archive/v{}.tar.gz".format(__version__),
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    tests_require=test_requirements,
    install_requires=required,
    extras_require=dict(TEST=test_requirements),
    include_package_data=True,
    zip_safe=False,
)
