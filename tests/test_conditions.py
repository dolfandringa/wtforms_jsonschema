from pprint import pprint
from collections import OrderedDict
from wtforms_jsonschema2.fab import FABConverter
from wtforms_jsonschema2.conditions import oneOf
from unittest import TestCase
from flask_appbuilder.fields import QuerySelectField
from flask_appbuilder import AppBuilder
from flask import Flask
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import (Column, Integer, String, ForeignKey, Numeric,
                        Boolean, MetaData, create_engine, Enum)
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


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


class BaseObservation(db.Model):
    __tablename__ = 'observation'
    id = Column(Integer, primary_key=True)
    alive = Column(Boolean)
    length = Column(Numeric, nullable=False)
    dead_observation = relationship('DeadObservation',
                                    back_populates='base_observation',
                                    uselist=False)
    live_observation = relationship('LiveObservation',
                                    back_populates='base_observation',
                                    uselist=False)


class DeadObservation(db.Model):
    __tablename__ = 'dead_observation'
    id = Column(Integer, primary_key=True)
    observation_id = Column(Integer, ForeignKey('observation.id'),
                            nullable=False)
    cause_of_death = Column(Enum('stranding', 'bycatch'), nullable=False)
    base_observation = relationship(BaseObservation,
                                    back_populates='dead_observation')
    stranding = relationship('Stranding', back_populates='dead_observation',
                             uselist=False)
    bycatch = relationship('Bycatch', back_populates='dead_observation',
                           uselist=False)


class LiveObservation(db.Model):
    __tablename__ = 'live_observation'
    id = Column(Integer, primary_key=True)
    observation_id = Column(Integer, ForeignKey('observation.id'),
                            nullable=False)
    live_observation_type = Column(Enum('in-water', 'nesting'), nullable=False)
    base_observation = relationship(BaseObservation,
                                    back_populates='live_observation')


class Stranding(db.Model):
    __tablename__ = 'stranding'
    id = Column(Integer, primary_key=True)
    stranding_info = Column(String)
    dead_observation_id = Column(Integer, ForeignKey('dead_observation.id'),
                                 nullable=False)
    dead_observation = relationship(DeadObservation,
                                    back_populates='stranding')


class Bycatch(db.Model):
    __tablename__ = 'bycatch'
    id = Column(Integer, primary_key=True)
    fishing_gear = Column(String)
    dead_observation_id = Column(Integer, ForeignKey('dead_observation.id'),
                                 nullable=False)
    dead_observation = relationship(DeadObservation,
                                    back_populates='bycatch')


class BycatchView(ModelView):
    datamodel = SQLAInterface(Bycatch)
    add_columns = ['fishing_gear', 'dead_observation_id']
    show_title = 'Bycatch'
    add_title = 'Add Bycatch'


class StrandingView(ModelView):
    datamodel = SQLAInterface(Stranding)
    add_columns = ['stranding_info', 'dead_observation_id']
    show_title = 'Stranding'
    add_title = 'Add Stranding'


class DeadObservationView(ModelView):
    datamodel = SQLAInterface(DeadObservation)
    add_columns = ['cause_of_death', 'observation_id']
    show_title = 'Dead Observation'
    add_title = 'Add Dead Observation'
    related_views = [BycatchView, StrandingView]

    _conditional_relations = [
        oneOf({
            BycatchView: {'cause_of_death': 'bycatch'},
            StrandingView: {'cause_of_death': 'stranding'}
        })
    ]


class LiveObservationView(ModelView):
    datamodel = SQLAInterface(LiveObservation)
    add_columns = ['live_observation_type', 'observation_id']
    show_title = 'Live Observation'
    add_title = 'Add Live Observation'


class ObservationView(ModelView):
    datamodel = SQLAInterface(BaseObservation)
    add_columns = ['length', 'alive']
    show_title = 'Observation'
    add_title = 'Add Observation'
    related_views = [DeadObservationView, LiveObservationView]

    _conditional_relations = [
        oneOf({
            LiveObservationView: {'alive': True},
            DeadObservationView: {'alive': False}
        })
    ]


appbuilder.add_view(ObservationView, 'observations')
appbuilder.add_view(LiveObservationView, 'live observations')
appbuilder.add_view(DeadObservationView, 'dead observations')
appbuilder.add_view(StrandingView, 'strandings')
appbuilder.add_view(BycatchView, 'bycatch')

observation_schema = OrderedDict([
    ('type', 'object'),
    ('definitions', OrderedDict([

        # Observation definition
        ('Observation', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('length', {
                    'title': 'Length',
                    'type': 'number',
                }),
                ('alive', {
                    'title': 'Alive',
                    'type': 'boolean',
                }),
                ('live_observation', {
                    '$ref': '#/definitions/LiveObservation'
                }),
                ('dead_observation', {
                    '$ref': '#/definitions/DeadObservation'
                }),
            ])),
            ('required', ['length']),
            ('oneOf', [  # require one and only one of these two relations
                OrderedDict([
                    ('properties', OrderedDict([
                        ('alive', {
                            'enum': [True]
                        }),
                        ('live_observation', {
                            '$ref': '#/definitions/LiveObservation'
                        }),
                    ])),
                    ('required', ['alive', 'live_observation']),
                ]),
                OrderedDict([
                    ('properties', OrderedDict([
                        ('alive', {
                            'enum': [False]
                        }),
                        ('dead_observation', {
                            '$ref': '#/definitions/DeadObservation'
                        }),
                    ])),
                    ('required', ['alive', 'dead_observation']),
                ]),
            ]),
            ('additionalProperties', False)
        ])),


        # Dead Observation definition
        ('DeadObservation', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('cause_of_death', {
                    'enum': ['stranding', 'bycatch']
                }),
                ('stranding', {
                    '$ref': '#/definitions/Stranding'
                }),
                ('bycatch', {
                    '$ref': '#/definitions/Bycatch'
                }),
            ])),
            ('oneOf', [
                OrderedDict([
                    ('properties', OrderedDict([
                        ('cause_of_death', {
                            'enum': ['stranding']
                        }),
                        ('stranding', {
                            '$ref': '#/definitions/Stranding'
                        }),
                     ])),
                    ('required', ['cause_of_death', 'stranding']),
                ]),
                OrderedDict([
                    ('properties', OrderedDict([
                        ('cause_of_death', {
                            'enum': ['bycatch']
                        }),
                        ('bycatch', {
                            '$ref': '#/definitions/Bycatch'
                        }),
                     ])),
                    ('required', ['cause_of_death', 'bycatch']),
                ]),
            ]),
            ('additionalProperties', False)
        ])),

        # Live Observation definition
        ('LiveObservation', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('live_observation_type', {
                    'enum': ['in-water', 'nesting']
                }),
            ])),
            ('required', ['live_observation_type']),
        ])),

        # Stranding definition
        ('Stranding', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('stranding_info', {
                    'type': 'string'
                }),
            ])),
        ])),

        # Bycatch definition
        ('Bycatch', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('fishing_gear', {
                    'type': 'string'
                }),
            ])),
        ])),


    ])),
    ('type', 'object'),
    ('properties', OrderedDict([
        ('observation', {'$ref': '#/definitions/Observation'}),
    ]))
])


class TestFABConditionalViews(TestCase):
    """
    A SQLAlchemy model with joined table inheritance with a view pointing to
    the base class and related views for the subclasses should result in a
    schema where there is a condition making the polymorphic column required
    and add a "oneOf" condition where only one of the related views for the
    polymorphic should be filled in, depending on the value of the polymorphic
    column. It allows us to create forms that change depending on previously
    filled in columns.
    """

    def setUp(self):
        self.converter = FABConverter()
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        self.db = db
        db.create_all()
        db.session.commit()
        db.session.flush()

    def tearDown(self):
        try:
            self.db.session.commit()
        except:
            pass
        db.drop_all()

    def test_oneOf(self):
        k, v = oneOf({
            StrandingView: {'cause_of_death': 'stranding'},
            BycatchView: {'cause_of_death': 'bycatch'}
        }).get_json_schema(DeadObservationView)
        self.assertEqual(k, 'oneOf')
        correct = observation_schema['definitions']['DeadObservation']['oneOf']
        self.assertEqual(v, correct)

    def test_full_conditional_view(self):
        schema = self.converter.convert(ObservationView)
        pprint(schema)
        pprint(observation_schema)
        self.assertEqual(schema, observation_schema)
        self.db.session.commit()
