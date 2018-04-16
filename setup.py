from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

extras = {
    'fab': ['flask_appbuilder']
}

setup(
    name="wtforms_jsonschema2",
    version="0.1.0.dev3",
    description="Package to convert WTForms to JSON Schema",
    long_description=long_description,
    url="https://github.com/dolfandringa/wtforms_jsonschema",
    author="Dolf Andringa",
    author_email="dolfandringa@gmail.com",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['wtforms'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov']+extras['fab'],
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
