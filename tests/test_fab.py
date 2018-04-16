from collections import OrderedDict
from wtforms_jsonschema2.fab import FABConverter
from unittest import TestCase
from wtforms.form import Form
from flask_appbuilder.fields import QuerySelectField


class FABTestForm(Form):
    _schema = OrderedDict([
        ('type', 'object'),
        ('properties', OrderedDict([
            ('gender', {
                'type': 'string',
                'title': 'Gender',
                'enum': ['Male', 'Female', 'Alien', 'Other']
            })
        ]))
    ])
    gender = QuerySelectField('Gender',
                              query_func=lambda: ['Male', 'Female',
                                                  'Alien', 'Other'])


class TestFABFormConvert(TestCase):
    def setUp(self):
        self.converter = FABConverter()
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_fab_form(self):
        self.assertEqual(self.converter.convert(FABTestForm),
                         FABTestForm._schema)
