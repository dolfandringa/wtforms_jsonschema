# WTForms JSONSchema 2
[![Build status](https://travis-ci.org/dolfandringa/wtforms_jsonschema.svg?branch=master)](https://travis-ci.org/dolfandringa/wtforms_jsonschema)

WTForms JSONSchema 2 is a converter to turn forms made with WTForms into a OrderedDict following the JSONSchema syntax.

It was developed independently of wtforms_jsonschema. Main differences are that it is unit tested, adds support for validators and is easier to extend. That being said, not all fields that are supported by wtforms_jsonschema are supported by wtforms_jsonschema2.

The order of the original WTForm fields are kept intact.
The use case is to communicate these forms with other applications that will then display these forms. For instance a backend can make a simple CRUD application using [Flask Appbuilder](http://flask-appbuilder.readthedocs.io/en/latest/intro.html) but also expose some forms to another frontend made in [Angular](https://angular.io) or in a mobile app using [Ionic](https://ionicframework.com).

JSONSchema is not specifically meant to be used to describe forms, but actually is quite extensive and provides enough flexibility to describe forms quite well. It supports limitations to fields, similar to validators, like email, url, date-time string formats, length limitations, minimum/maximum values for numbers, etc. For more info see [Understanding JSON Schema by the Space Telescope Science Institute](https://spacetelescope.github.io/understanding-json-schema/)

## Installation
Clone the repository form github and install it with
```bash
pip install wtforms_jsonschema2
```
If you also want [Flask Appbuilder](http://flask-appbuilder.readthedocs.io/en/latest/intro.html) support, install with
```
pip install wtforms_jsonschema2[fab]
```

## Testing
Unittests can be run with
```bash
python setup.py test
```

## Usage
Here is an example how the package works:

```python
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
```
Output:
```python
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
```

## Extending

The library is based around the ```wtforms_jsonschema2.base.BaseConverter``` class.
This class has methods that are all decorated with ```@converts(*<classes>)```.
These conversion methods return the tuple (fieldtype, options, required) which are a string, dict and boolean respectively that signify the JSONSchema type, additional parameters for the field like [enum](https://spacetelescope.github.io/understanding-json-schema/reference/generic.html#enumerated-values) or other value restrictions derived from the validators and whether the field is required.

To support additional fields, either contribute back by adding functions to the BaseConverter class that convert your specific field,
or create a new class that inherits from BaseConverter and adds functions for your specific field types.

This is an example for the DecimalField:

```python
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
```

## Credits

WTForms JSONSchema 2 is developed by [Dolf Andringa](https://allican.be), but was inspired by the sqlalchemy conversion component of [Flask-Admin](https://github.com/flask-admin/flask-admin/) (especially the @converts decorator).
