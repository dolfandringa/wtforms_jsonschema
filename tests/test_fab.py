from pprint import pprint
from collections import OrderedDict
from wtforms_jsonschema2.fab import FABConverter
from unittest import TestCase
from wtforms.form import Form
from flask_appbuilder.fields import QuerySelectField, EnumField
from flask_appbuilder import AppBuilder
from flask import Flask
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import (Column, Integer, String, ForeignKey, DateTime, Numeric,
                        Boolean)
from flask_appbuilder.models.mixins import ImageColumn
from sqlalchemy import MetaData, create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


cfg = {'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
       'CSRF_ENABLED': False,
       'IMG_UPLOAD_URL': '/',
       'IMG_UPLOAD_FOLDER': '/tmp/',
       'WTF_CSRF_ENABLED': False,
       'SECRET_KEY': 'bla'}


app = Flask('wtforms_jsonschema2_fab_testing')
app.config.update(cfg)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata = MetaData(bind=engine)
db = SQLAlchemy(app, metadata=metadata)
ctx = app.app_context()
ctx.push()
appbuilder = AppBuilder(app, db.session)
db.session.commit()


class Gender(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return self.name


class FABTestForm(Form):
    _schema = OrderedDict([
        ('type', 'object'),
        ('properties', OrderedDict([
            ('gender', {
                'type': 'object',
                'title': 'Gender',
                'enum': [{'id': '1', 'label': 'Male'},
                         {'id': '2', 'label': 'Female'},
                         {'id': '3', 'label': 'Alien'},
                         {'id': '4', 'label': 'Other'}]
            })
        ]))
    ])
    gender = QuerySelectField('Gender',
                              query_func=lambda: [Gender(1, 'Male'),
                                                  Gender(2, 'Female'),
                                                  Gender(3, 'Alien'),
                                                  Gender(4, 'Other')],
                              allow_blank=True,
                              get_pk_func=lambda x: x.id)


class PersonType(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return 'Person Type %s' % self.id


class Person(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dt = Column(DateTime)
    person_type_id = Column(Integer, ForeignKey('person_type.id'),
                            nullable=False)
    person_type = relationship(PersonType, backref='people')

    def __repr__(self):
        return self.name


class Picture(db.Model):
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    person = relationship(Person, backref='pictures')
    validated = Column(Boolean)
    picture = Column(ImageColumn(size=(2048, 2048, False),
                                 thumbnail_size=(800, 800, True)),
                     nullable=False)

    def __repr__(self):
        return self.picture


class Observation(db.Model):
    id = Column(Integer, primary_key=True)
    species = Column(String, nullable=False)
    length = Column(Numeric)


class PictureView(ModelView):
    datamodel = SQLAInterface(Picture)
    add_columns = ['picture', 'validated']
    show_title = 'Picture'
    list_title = 'Pictures'
    edit_title = 'Edit Picture'
    add_title = 'Add Picture'


class PersonView(ModelView):
    datamodel = SQLAInterface(Person)
    related_views = [PictureView]
    add_columns = ['name', 'dt', 'person_type']
    show_title = 'Person'
    list_title = 'People'
    edit_title = 'Edit Person'
    add_title = 'Add Person'


class PersonTypeView(ModelView):
    datamodel = SQLAInterface(PersonType)
    related_views = [PersonView]


class ObservationView(ModelView):
    datamodel = SQLAInterface(Observation)
    add_columns = ['species', 'length']
    show_title = 'Observation'
    add_title = 'Add Observation'


appbuilder.add_view(PersonView, 'people')
appbuilder.add_view(PersonTypeView, 'people types')
appbuilder.add_view(PictureView, 'pictures')
appbuilder.add_view(ObservationView, 'observations')


person_observation_schema = OrderedDict([
    ('type', 'object'),
    ('definitions', OrderedDict([
        ('Person', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('name', {
                    'type': 'string',
                    'title': 'Name'
                }),
                ('dt', {
                    'type': 'string',
                    'format': 'date-time',
                    'title': 'Dt'
                }),
                ('person_type', {
                    'title': 'Person Type',
                    'type': 'object',
                    'enum': [{'id': '1', 'label': 'male'},
                             {'id': '2', 'label': 'Person Type 2'}]
                }),
                ('pictures', {
                    'type': 'array',
                    'title': 'Pictures',
                    'items': [
                        {'$ref': '#/definitions/Picture'}
                    ]
                })
            ])),
            ('required', ['name', 'person_type'])
        ])),
        ('Picture', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('picture', {
                    'title': 'Picture',
                    'type': 'string',
                    'contentEncoding': 'base64',
                    'contentMediaType': 'image/jpeg'
                }),
                ('validated', {
                    'title': 'Validated',
                    'type': 'boolean'
                }),
            ])),
            ('required', ['picture'])
        ])),
        ('Observation', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('species', {
                    'type': 'string',
                    'title': 'Species'
                }),
                ('length', {
                    'type': 'number',
                    'title': 'Length'
                })
            ])),
            ('required', ['species'])
        ]))
    ])),
    ('type', 'object'),
    ('properties', OrderedDict([
        ('Person', {'$ref': '#/definitions/Person'}),
        ('Observation', {'$ref': '#/definitions/Observation'})
    ]))

])

person_schema = OrderedDict([
    ('type', 'object'),
    ('definitions', OrderedDict([
        ('Person', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('name', {
                    'type': 'string',
                    'title': 'Name'
                }),
                ('dt', {
                    'type': 'string',
                    'format': 'date-time',
                    'title': 'Dt'
                }),
                ('person_type', {
                    'title': 'Person Type',
                    'type': 'object',
                    'enum': [{'id': '1', 'label': 'male'},
                             {'id': '2', 'label': 'Person Type 2'}]
                }),
                ('pictures', {
                    'type': 'array',
                    'title': 'Pictures',
                    'items': [
                        {'$ref': '#/definitions/Picture'}
                    ]
                })
            ])),
            ('required', ['name', 'person_type'])
        ])),
        ('Picture', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('picture', {
                    'title': 'Picture',
                    'type': 'string',
                    'contentEncoding': 'base64',
                    'contentMediaType': 'image/jpeg'
                }),
                ('validated', {
                    'title': 'Validated',
                    'type': 'boolean'
                }),
            ])),
            ('required', ['picture'])
        ]))
    ])),
    ('type', 'object'),
    ('properties', OrderedDict([
        ('Person', {'$ref': '#/definitions/Person'})
    ]))

])


class TestFABFormConvert(TestCase):
    def setUp(self):
        self.converter = FABConverter()
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        self.db = db
        db.create_all()
        db.session.add(PersonType(name='male'))
        db.session.add(PersonType())
        db.session.commit()
        db.session.flush()

    def tearDown(self):
        try:
            self.db.session.commit()
        except:
            pass
        db.drop_all()

    def test_full_view(self):
        schema = self.converter.convert(PersonView)
        pprint(schema)
        pprint(person_schema)
        self.assertEqual(schema, person_schema)
        self.db.session.commit()

    def test_full_multiple_view(self):
        schema = self.converter.convert([PersonView, ObservationView])
        pprint(schema)
        pprint(person_observation_schema)
        self.assertEqual(schema, person_observation_schema)
        self.db.session.commit()

    def test_enum_field(self):

        class testform(Form):
            enumfield = EnumField(None, ['option1', 'option2'])

        field, req = self.converter.convert_field(testform().enumfield)
        self.assertEqual(field, {'enum': [{'id': 'option1',
                                           'label': 'option1'},
                                          {'id': 'option2',
                                           'label': 'option2'}
                                          ],
                                 'title': 'Enumfield',
                                 'type': 'string'})

    def test_fab_form(self):
        schema = self.converter.convert(FABTestForm)
        pprint(schema)
        pprint(FABTestForm._schema)
        self.assertEqual(schema,
                         FABTestForm._schema)
        self.db.session.commit()
