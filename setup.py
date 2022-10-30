"""Configuration for building the wheel package."""

import setuptools
import re

ENTRY_POINT_SCRIPTS = [
    'pocket-stats=colifer.reportextenders.articles.pocket_stats:main',
]

VERSION = "0.0.1"

try:
    with open("README.md", "r", encoding="utf-8") as readme_file:
        readme = readme_file.read()
except IOError:
    readme = 'Checkout https://github.com/oshev/colifer.git'

with open('requirements.txt') as f:
    required = [line for line in f.read().splitlines()
                if not re.match(r'^\s*(-i|--index-url|--extra-index-url|--find-links).*', line)]
with open('test_requirements.txt') as f:
    test_reqs = f.read().splitlines()


setuptools.setup(
    name="colifer",
    version=VERSION,
    author="Oleg Sehvelev",
    description="CoLifer",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/oshev/colifer",
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires=">=3.8.*",
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    dependency_links=None,
    extras_require={
        'test': test_reqs
    },
    tests_require=test_reqs,
    entry_points={'console_scripts': ENTRY_POINT_SCRIPTS},
)
