from flask_appbuilder.fields import QuerySelectField, QuerySelectMultipleField
from collections import OrderedDict
import logging
from .base import BaseConverter, converts
from decimal import Decimal
import re

log = logging.getLogger(__name__)


class FABConverter(BaseConverter):
    """
    The FABConverter extends BaseConverter with functioality for
    flask appbuilder.
    """

    @converts(QuerySelectField)
    def query_select_field(self, field):
        choices = list(field.iter_choices())
        fieldtype = 'object'
        options = {'enum': [{'id': c[0], 'label': str(c[1])} for c in choices]}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    @converts(QuerySelectMultipleField)
    def query_select_multiple_field(self, field):
        fieldtype = 'array'
        choices = list(field.iter_choices())

        options = {'items': [{
            'type': 'object',
            'enum': [{'id': c[0], 'label': c[1]} for c in choices]
        }]}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    def _get_form(self, view, form_type):
        if form_type == 'add':
            return view().add_form
        if form_type == 'edit':
            return view().edit_form

    def _get_pretty_name(self, view):
        """
        Get the pretty name of a view. If defined view._pretty_name will be
        used, else the name will be derived from the view name by taking the
        class name and removing  View from the name.
        """
        if hasattr(view, '_pretty_name'):
            return view._pretty_name
        else:
            return re.sub('[Vv]iew', '', view.__class__.__name__)

    def convert(self, views, form_type='add'):
        """
        Convert a list of Flask Appbuilder ModelViews to JSON Schema.
        If the ModelView has the optional _pretty_name property, it will be
        used to refer to the view.

        Each view will be it's own JSON Schema Defition, and referred to by
        it's pretty name in the properties section.

        Related views are also added as additional definitions and referred to
        from the "parent" view, but not added to the "properties" part of the
        schema.

        The idea is that each property in the "properties" section becomes a
        form in the comsuming application, while defintions that aren't in the
        properties section are sub-forms to a parent form. This is useful
        where related views are used to add items in a one-to-many
        relationship.

        Example:
        The following model and views

        class Person(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String)

        class Picture(Model):
            id = Column(Integer, primary_key=True)
            picture = Column(Text)
            person_id = Column(Integer, ForeignKey(person.id), nullable=False)
            person = relationship(Person, backref="pictures")

        class PictureView(ModelView):
            _pretty_name = 'Picture'
            datamodel = Picture
            add_columns = ['picture']

        class PersonView(ModelView):
            _pretty_name = 'Person'
            datamodel = Person
            related_views = [PictureView]
            add_columns = ['name', 'pictures']

        converter.convert({'Person': PersonView})

        should result in the following schema:


        {
            "type": "object",
            "definitions": {
                "Person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "pictures": {
                            "type": "array",
                            "items": [
                                {"$ref": "#/definitions/Picture"}
                            ]
                        }
                    }
                },
                "Picture": {
                    "type": "object",
                    "properties": {
                        "picture: {"type": "string"}
                    }
                }
            },
            "properties": {
                "Person": {"$ref": "#/definitions/Person"}
            }
        }

        """
        schema = OrderedDict([
            ('type', 'object'),
            ('definitions', OrderedDict([])),
            ('properties', OrderedDict([]))
        ])
        try:
            iter(views)
        except TypeError:
            views = [views]
        for view in views:
            name = self._get_pretty_name(view)
            schema['definitions'][name] = super().convert(
                self._get_form(view,  form_type))
            schema['properties'][name] = {'$ref': '#/definitions/%s' % name}

            for v in view.related_views:
                name2 = self._get_pretty_name(v)
                schema['definitions'][name2] = super().convert(
                    self._get_form(v, form_type))
        return schema
