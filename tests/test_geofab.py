from pprint import pprint
from collections import OrderedDict
from wtforms_jsonschema2.geofab import GeoFABConverter
from unittest import TestCase
from flask_appbuilder import AppBuilder
from fab_geoalchemy.interface import GeoSQLAInterface
from flask import Flask
from fab_geoalchemy.views import GeoModelView
from sqlalchemy import Column, Integer, String
from sqlalchemy import MetaData, create_engine
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
import logging

logging.getLogger('wtforms_jsonschema2').setLevel(logging.DEBUG)

cfg = {'SQLALCHEMY_DATABASE_URI': 'postgres:///test',
       'CSRF_ENABLED': False,
       'IMG_UPLOAD_URL': '/',
       'IMG_UPLOAD_FOLDER': '/tmp/',
       'WTF_CSRF_ENABLED': False,
       'SECRET_KEY': 'bla'}

app = Flask('wtforms_jsonschema2_geofabtesting')
app.config.update(cfg)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
metadata = MetaData(bind=engine)
db = SQLAlchemy(app, metadata=metadata)
appbuilder = AppBuilder(app, db.session)
db.session.commit()


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

observation_schema = OrderedDict([
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
                            'type': 'string',
                            'title': 'Latitude',
                            'format': 'coordinate_point_latitude'
                        }),
                        ('lon', {
                            'type': 'string',
                            'title': 'Longitude',
                            'format': 'coordinate_point_longitude'
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


class TestGeoFABFormConvert(TestCase):
    def setUp(self):
        self.converter = GeoFABConverter()
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        ctx = app.app_context()
        ctx.push()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    def test_full_view(self):
        schema = self.converter.convert(GeoObservationView)
        pprint(schema)
        pprint(observation_schema)
        self.assertEqual(schema, observation_schema)
