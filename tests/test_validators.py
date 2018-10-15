from pprint import pprint
from collections import OrderedDict
from wtforms_jsonschema2.fab import FABConverter
from unittest import TestCase
from flask_appbuilder import AppBuilder
from flask import Flask
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import (Column, Integer, String, Boolean, Numeric)
from sqlalchemy import MetaData, create_engine
from flask_sqlalchemy import SQLAlchemy
from wtforms.jsonschema2 import validators


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


class Observation(db.Model):
    id = Column(Integer, primary_key=True)
    species = Column(String, nullable=False)
    length = Column(Numeric)
    boolfield = Column(Boolean)


class ObservationView(ModelView):
    datamodel = SQLAInterface(Observation)
    add_columns = ['species', 'length', 'boolfield']
    show_title = 'Observation'
    list_title = 'Observations'
    edit_title = 'Edit Observation'
    add_title = 'Add Observation'

    validators_columns = {
        'boolfield': [validators.ValueRequired(True, "Wrong Value")]
    }


class TestValidators(TestCase):
    def setUp(self):
        self.converter = FABConverter()
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        self.db = db
        db.create_all()
        db.session.commit()

    def tearDown(self):
        try:
            self.db.session.commit()
        except:
            pass
        db.drop_all()

    def test_ValueRequired(self):
        schema = self.converter.convert(ObservationView)
        allof = schema['definitions']['Observation']['allOf']
        pprint(allof)
        self.assertEqual(allof['properties']['boolfield'], {'enum': [True]})
        self.db.session.commit()
