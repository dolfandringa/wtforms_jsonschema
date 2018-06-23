from setuptools import setup, find_packages
# To use a consistent encoding
from os import path
import codecs
import wtforms_jsonschema2

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open('README.rst') as f:
    long_description = f.read()

extras = {
    'fab': ['flask_appbuilder', 'pillow'],
    'geofab': ['fab_geoalchemy', 'flask_appbuilder', 'pillow'],
    'test': ['pytest', 'pytest-cov']
}


setup(
    name="wtforms_jsonschema2",
    version=wtforms_jsonschema2.__version__,
    description="Package to convert WTForms to JSON Schema",
    long_description=long_description,
    url="https://github.com/dolfandringa/wtforms_jsonschema",
    author="Dolf Andringa",
    author_email="dolfandringa@gmail.com",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['wtforms'],
    setup_requires=['pytest-runner', 'm2r'],
    tests_require=extras['test']+extras['fab']+extras['geofab'],
    extras_require=extras,
    project_urls={
        'Source': 'https://github.com/dolfandringa/wtforms_jsonschema/'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='wtforms jsonschema'
)
