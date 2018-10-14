import copy
from collections import OrderedDict
from wtforms_jsonschema2.base import BaseConverter
from wtforms_jsonschema2.exceptions import UnsupportedFieldException
from unittest import TestCase
from wtforms.form import Form
from wtforms import validators
from wtforms.fields import (StringField, DecimalField, SelectField,
                            IntegerField, Field, DateTimeField,
                            TextAreaField)
from wtforms.widgets import TextInput


class CustomField(Field):
    widget = TextInput()


class UnsupportedForm(Form):
    custom_field = CustomField('Custom Field')
    first_name = StringField('First Name', validators=[validators.required()])


class StringTestForm(Form):
    _schema = OrderedDict([
        ('type', 'object'),
        ('properties', OrderedDict([
            ('email', {
                'type': 'string',
                'format': 'email',
                'title': 'Email Address'
            }),
            ('length_string', {
                'type': 'string',
                'minLength': 5,
                'maxLength': 10,
                'title': 'Name'
            }),
            ('simplestring', {
                'type': 'string',
                'title': 'Simple String',
                'maxLength': 255
            }),
            ('dt', {
                'type': 'string',
                'title': 'DateTime',
                'format': 'date-time'
            })
        ]))
    ])
    email = StringField('Email Address', validators=[validators.Email()])
    length_string = StringField('Name', validators=[validators.Length(5, 10)])
    simplestring = StringField('Simple String')
    dt = DateTimeField('DateTime')


class SimpleTestForm(Form):
    _schema = OrderedDict([
        ('type', 'object'),
        ('properties', OrderedDict([
            ('first_name', {
                'type': 'string',
                'title': 'First Name',
                'maxLength': 255
            }),
            ('nick_name', {
                'type': 'string',
                'title': 'Nickname',
                'maxLength': 255
            }),
            ('age', {
                'type': 'integer',
                'title': 'Age',
                'minimum': 0,
                'maximum': 10
            }),
            ('description', {
                'type': 'string',
                'title': 'Description'
            }),
            ('average', {
                'type': 'number',
                'title': 'Average',
                'minimum': 10,
                'maximum': 1000
            }),
            ('gender', {
                'type': 'string',
                'title': 'Gender',
                'enum': ['Male', 'Female', 'Alien', 'Other']
            }),
            ('some_field', {
                'type': 'integer',
                'title': 'Bla',
                'enum': [1, 2, 3]
            }),
            ('some_field2', {
                'type': 'number',
                'title': 'Bla',
                'enum': [1.5, 2.2, 3]
            }),
        ])),
        ('required', ['first_name', 'age'])
    ])
    first_name = StringField('First Name', validators=[validators.required()])
    nick_name = StringField('Nickname')
    age = IntegerField('Age', validators=[validators.number_range(0, 10),
                                          validators.required()])
    description = TextAreaField('Description')
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

    def test_field_order(self):
        schema = self.converter.convert(SimpleTestForm)
        self.assertEqual(list(schema.keys()),
                         ['type', 'properties', 'required'])
        self.assertEqual(schema['properties'].keys(),
                         SimpleTestForm._schema['properties'].keys())

    def test_skip_fields(self):
        converter = BaseConverter(skip_fields=['email'])
        schema = converter.convert(StringTestForm())
        correct_schema = copy.deepcopy(StringTestForm._schema)
        del(correct_schema['properties']['email'])
        self.assertEqual(schema, correct_schema)

    def test_string_fields(self):
        self.assertEqual(self.converter.convert(StringTestForm),
                         StringTestForm._schema)

    def test_unsupported_form(self):
        with self.assertRaises(UnsupportedFieldException):
            self.converter.convert(UnsupportedForm)

    def test_simple_form(self):
        self.assertEqual(self.converter.convert(SimpleTestForm),
                         SimpleTestForm._schema)
