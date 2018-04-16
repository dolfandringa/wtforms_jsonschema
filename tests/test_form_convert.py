import copy
from wtforms_jsonschema.base import BaseConverter
from wtforms_jsonschema.exceptions import UnsupportedFieldException
from unittest import TestCase
from wtforms.form import Form
from wtforms import validators
from wtforms.fields.core import (StringField, DecimalField, SelectField,
                                 IntegerField, Field, DateTimeField)
from wtforms.widgets import TextInput
from flask_appbuilder.fields import QuerySelectField


class CustomField(Field):
    widget = TextInput()


class UnsupportedForm(Form):
    custom_field = CustomField('Custom Field')
    first_name = StringField('First Name', validators=[validators.required()])


class FABTestForm(Form):
    _schema = {
        'type': 'object',
        'properties': {
            'gender': {
                'type': 'string',
                'title': 'Gender',
                'enum': ['Male', 'Female', 'Alien', 'Other']
            }
        }
    }
    gender = QuerySelectField('Gender',
                              query_func=lambda: ['Male', 'Female',
                                                  'Alien', 'Other'])


class StringTestForm(Form):
    _schema = {
        'type': 'object',
        'properties': {
            'email': {
                'type': 'string',
                'format': 'email',
                'title': 'Email Address'
            },
            'length_string': {
                'type': 'string',
                'minLength': 5,
                'maxLength': 10,
                'title': 'Name'
            },
            'simplestring': {
                'type': 'string',
                'title': 'Simple String'
            },
            'dt': {
                'type': 'string',
                'title': 'DateTime',
                'format': 'date-time'
            }
        }
    }
    email = StringField('Email Address', validators=[validators.Email()])
    length_string = StringField('Name', validators=[validators.Length(5, 10)])
    simplestring = StringField('Simple String')
    dt = DateTimeField('DateTime')


class SimpleTestForm(Form):
    _schema = {
        'type': 'object',
        'properties': {
            'first_name': {
                'type': 'string',
                'title': 'First Name',
            },
            'nick_name': {
                'type': 'string',
                'title': 'Nickname'
            },
            'age': {
                'type': 'integer',
                'title': 'Age',
                'minimum': 0,
                'maximum': 10
            },
            'average': {
                'type': 'number',
                'title': 'Average',
                'minimum': 10,
                'maximum': 1000
            },
            'gender': {
                'type': 'string',
                'title': 'Gender',
                'enum': ['Male', 'Female', 'Alien', 'Other']
            },
            'some_field': {
                'type': 'integer',
                'title': 'Bla',
                'enum': [1, 2, 3]
            },
            'some_field2': {
                'type': 'number',
                'title': 'Bla',
                'enum': [1.5, 2.2, 3]
            }
        },
        'required': ['first_name', 'age']
    }
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


class TestFormConvert(TestCase):
    def setUp(self):
        self.converter = BaseConverter()
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_skip_fields(self):
        converter = BaseConverter(skip_fields=['email'])
        schema = converter.convert(StringTestForm())
        correct_schema = copy.deepcopy(StringTestForm._schema)
        del(correct_schema['properties']['email'])
        self.assertEqual(schema, correct_schema)

    def test_fab_form(self):
        self.assertEqual(self.converter.convert(FABTestForm),
                         FABTestForm._schema)

    def test_string_fields(self):
        self.assertEqual(self.converter.convert(StringTestForm),
                         StringTestForm._schema)

    def test_unsupported_form(self):
        with self.assertRaises(UnsupportedFieldException):
            self.converter.convert(UnsupportedForm)

    def test_simple_form(self):
        self.assertEqual(self.converter.convert(SimpleTestForm),
                         SimpleTestForm._schema)
