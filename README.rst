
WTForms JSONSchema 2
====================


.. image:: https://travis-ci.org/dolfandringa/wtforms_jsonschema.svg?branch=master
   :target: https://travis-ci.org/dolfandringa/wtforms_jsonschema
   :alt: Build status


WTForms JSONSchema 2 is a converter to turn forms made with WTForms into a OrderedDict following the JSONSchema syntax.

It was developed independently of `wtforms_jsonschema <https://pypi.python.org/pypi/wtforms-jsonschema/>`_. Main differences are that it is unit tested, adds support for validators and is easier to extend. That being said, not all fields that are supported by wtforms_jsonschema are supported by wtforms_jsonschema2.

The order of the original WTForm fields are kept intact.
The use case is to communicate these forms with other applications that will then display these forms. For instance a backend can make a simple CRUD application using `Flask Appbuilder <http://flask-appbuilder.readthedocs.io/en/latest/intro.html>`_ but also expose some forms to another frontend made in `Angular <https://angular.io>`_ or in a mobile app using `Ionic <https://ionicframework.com>`_.

JSONSchema is not specifically meant to be used to describe forms, but actually is quite extensive and provides enough flexibility to describe forms quite well. It supports limitations to fields, similar to validators, like email, url, date-time string formats, length limitations, minimum/maximum values for numbers, etc. For more info see `Understanding JSON Schema by the Space Telescope Science Institute <https://spacetelescope.github.io/understanding-json-schema/>`_

Installation
------------

Clone the repository form github and install it with

.. code-block:: bash

   pip install wtforms_jsonschema2

If you also want `Flask Appbuilder <http://flask-appbuilder.readthedocs.io/en/latest/intro.html>`_ support, install with

.. code-block:: bash

   pip install wtforms_jsonschema2[fab]

And if you want Geoalchemy2 support for Geometry columns in Flask Appbuilder, install with

.. code-block::

   pip install wtforms_jsonschema[geofab]

Testing
-------

Unittests can be run with

.. code-block:: bash

   python setup.py test

or

.. code-block:: bash

   pytest

Usage
-----

Here is an example how the package works:

.. code-block:: python

   from wtforms_jsonschema.base import BaseConverter
   from wtforms.form import Form
   from wtforms import validators
   from wtforms.fields.core import StringField, DecimalField, SelectField, IntegerField, Field, DateTimeField
   from wtforms.widgets import TextInput
   from pprint import pprint


   class SimpleTestForm(Form):
       """Simple Test Form displaying the conversion features"""
       first_name = StringField('First Name', validators=[validators.required()])
       nick_name = StringField('Nickname')
       age = IntegerField('Age', validators=[validators.number_range(0, 10),
                                             validators.required()])
       average = DecimalField('Average',
                              validators=[validators.number_range(10, 1000)])
       gender = SelectField("Gender", choices=['Male', 'Female', 'Alien',
                                               'Other'])
       some_field = SelectField("Bla", choices=[1, 2, 3])
       some_field2 = SelectField("Bla", choices=[1.5, 2.2, 3])
       email = StringField('Email Address', validators=[validators.Email()])
       length_string = StringField('Name', validators=[validators.Length(5, 10)])
       dt = DateTimeField('DateTime')

   converter = BaseConverter()
   pprint(converter.convert(SimpleTestForm))

Output:

.. code-block:: python


   OrderedDict([('type', 'object'),
                ('properties',
                 OrderedDict([('first_name',
                               {'title': 'First Name', 'type': 'string'}),
                              ('nick_name',
                               {'title': 'Nickname', 'type': 'string'}),
                              ('age',
                               {'maximum': 10,
                                'minimum': 0,
                                'title': 'Age',
                                'type': 'integer'}),
                              ('average',
                               {'maximum': 1000,
                                'minimum': 10,
                                'title': 'Average',
                                'type': 'number'}),
                              ('gender',
                               {'enum': ['Male', 'Female', 'Alien', 'Other'],
                                'title': 'Gender',
                                'type': 'string'}),
                              ('some_field',
                               {'enum': [1, 2, 3],
                                'title': 'Bla',
                                'type': 'integer'}),
                              ('some_field2',
                               {'enum': [1.5, 2.2, 3],
                                'title': 'Bla',
                                'type': 'number'}),
                              ('email',
                               {'format': 'email',
                                'title': 'Email Address',
                                'type': 'string'}),
                              ('length_string',
                               {'maxLength': 10,
                                'minLength': 5,
                                'title': 'Name',
                                'type': 'string'}),
                              ('dt',
                               {'format': 'date-time',
                                'title': 'DateTime',
                                'type': 'string'})])),
                ('required', ['first_name', 'age'])])

.. code-block:: python


   from wtforms_jsonschema2.geofab import GeoFABConverter
   from geoalchemy2 import Geometry
   from fab_geoalchemy.interface import GeoSQLAInterface
   from fab_geoalchemy.views import GeoModelView
   from flask_sqlalchemy import SQLA
   from sqlalchemy import Column, Integer, String

   app = Flask('myapp')
   app.config.update(cfg)
   db = SQLA(app)
   appbuilder = AppBuilder(app, db.session)

   class GeoObservation(db.Model):
       id = Column(Integer, primary_key=True)
       name = Column(String, nullable=False)
       location = Column(Geometry(geometry_type='POINT', srid=4326),
                         nullable=False)

       def __repr__(self):
           return self.name


   class GeoObservationView(GeoModelView):
       datamodel = GeoSQLAInterface(GeoObservation)
       add_columns = ['name', 'location']
       show_title = 'GeoObservation'
       add_title = 'Add GeoObservation'


   appbuilder.add_view(GeoObservationView, 'observations')

   ctx = app.app_context()
   ctx.push()
   db.create_all()
   db.session.commit()

   converter = GeoFABConverter()
   schema = converter.convert(GeoObservationView)
   pprint(schema)

Output:

.. code-block:: python

   OrderedDict([
       ('type', 'object'),
       ('definitions', OrderedDict([
           ('GeoObservation', OrderedDict([
               ('type', 'object'),
               ('properties', OrderedDict([
                   ('name', {
                       'type': 'string',
                       'title': 'Name'
                   }),
                   ('location', OrderedDict([
                       ('type', 'object'),
                       ('properties', OrderedDict([
                           ('lat', {
                               'type': 'number',
                               'title': 'Latitude',
                           }),
                           ('lon', {
                               'type': 'number',
                               'title': 'Longitude'
                           })
                       ])),
                       ('required', ['lat', 'lon']),
                       ('title', 'Location')
                   ])),
               ])),
               ('required', ['name'])
           ]))
       ])),
       ('type', 'object'),
       ('properties', OrderedDict([
           ('GeoObservation', {'$ref': '#/definitions/GeoObservation'})
       ]))
   ])

Extending
---------

The library is based around the ``wtforms_jsonschema2.base.BaseConverter`` class.
This class has methods that are all decorated with ``@converts(*<classes>)``.
These conversion methods return the tuple (fieldtype, options, required) which are a string, dict and boolean respectively that signify the JSONSchema type, additional parameters for the field like `enum <https://spacetelescope.github.io/understanding-json-schema/reference/generic.html#enumerated-values>`_ or other value restrictions derived from the validators and whether the field is required.

To support additional fields, either contribute back by adding functions to the BaseConverter class that convert your specific field,
or create a new class that inherits from BaseConverter and adds functions for your specific field types.

This is an example for the DecimalField:

.. code-block:: python

   from wtforms.fields.core import DecimalField
   from wtforms.validators import NumberRange
   from wtforms_jsonschema.base import BaseConverter, converts

   class MyConverter(BaseConverter):
       @converts(DecimalField)
       def decimal_field(self, field):
           fieldtype = 'number'
           options = {}
           required = False
           vals = dict([(v.__class__, v) for v in field.validators])
           required = self._is_required(vals)
           if NumberRange in vals.keys():
               options['minimum'] = vals[NumberRange].min
               options['maximum'] = vals[NumberRange].max
           return fieldtype, options, required

Credits
-------

WTForms JSONSchema 2 is developed by `Dolf Andringa <https://allican.be>`_\ , but was inspired by the sqlalchemy conversion component of `Flask-Admin <https://github.com/flask-admin/flask-admin/>`_ (especially the @converts decorator).
