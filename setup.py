from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="wtforms_jsonschema",
    version="0.1.0.dev1",
    description="Package to convert WTForms to JSON Schema",
    long_description=long_description,
    url="https://github.com/dolfandringa/wtforms_jsonschema",
    author="Dolf Andringa",
    author_email="dolfandringa@gmail.com",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['wtforms'],
    extras_require={
        'test': ['pytest', 'pytest-cov']
    },
    project_urls={
        'Source': 'https://github.com/dolfandringa/wtforms_jsonschema/'
    }
)
