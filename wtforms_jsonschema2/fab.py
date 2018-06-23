from flask_appbuilder.fields import (QuerySelectField,
                                     QuerySelectMultipleField)
from flask_appbuilder.upload import ImageUploadField
from collections import OrderedDict
import logging
from .base import BaseConverter, converts
import re
from wtforms.form import Form


log = logging.getLogger(__name__)


class FABConverter(BaseConverter):
    """
    The FABConverter extends BaseConverter with functioality for
    flask appbuilder.
    """

    @converts(ImageUploadField)
    def convert_image_field(self, field):
        fieldtype = 'string'
        options = {'contentEncoding': 'base64',
                   'contentMediaType': 'image/jpeg'}
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    @converts(QuerySelectField)
    def query_select_field(self, field):
        choices = [c for c in field.iter_choices() if c[0] != '__None']
        fieldtype = 'object'
        options = {'enum': [{'id': c[0], 'label': str(c[1])} for c in choices]}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    @converts(QuerySelectMultipleField)
    def query_select_multiple_field(self, field):
        fieldtype = 'array'
        choices = [c for c in field.iter_choices() if c[0] != '__None']

        options = {'items': [{
            'type': 'object',
            'enum': [{'id': c[0], 'label': c[1]} for c in choices]
        }]}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    def _get_form(self, view, form_type):
        if isinstance(view, type):
            # Instantiate the view if not done already
            view = view()
        if form_type == 'add':
            return view.add_form
        if form_type == 'edit':
            return view.edit_form

    def _get_pretty_name(self, view, form_type):
        """
        Get the pretty name of a view. If defined view._pretty_name will be
        used, else the name will be derived from the view name by taking the
        class name and removing  View from the name.
        """
        if isinstance(view, type):
            # Instantiate the view if not done already
            view = view()
        if form_type == 'add' and view.add_title != '':
            return view.add_title
        elif form_type == 'show' and view.show_title != '':
            return view.show_title
        elif form_type == 'list' and view.list_title != '':
            return view.list_title
        elif form_type == 'edit' and view.edit_title != '':
            return view.edit_title
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
            list_title = 'Pictures'
            add_title = 'Add Picture'
            edit_title = 'Edit Picture'
            show_title = 'Picture'
            datamodel = Picture
            add_columns = ['picture']

        class PersonView(ModelView):
            show_title = 'Person'
            edit_title = 'Edit Person'
            add_title = 'Add Person'
            list_title = 'People'
            datamodel = Person
            related_views = [PictureView]
            add_columns = ['name']

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
                            "title": "Pictures",
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
        if not isinstance(views, list) and (isinstance(views, Form)
                                            or issubclass(views, Form)):
            return super().convert(views)
        try:
            iter(views)
        except TypeError:
            views = [views]
        schema = OrderedDict([
            ('type', 'object'),
            ('definitions', OrderedDict([])),
            ('properties', OrderedDict([]))
        ])
        for view in views:
            name = self._get_pretty_name(view, 'show')
            schema['definitions'][name] = super().convert(
                self._get_form(view,  form_type))
            schema['properties'][name] = {'$ref': '#/definitions/%s' % name}
            if view.related_views is None:
                continue
            for v in view.related_views:
                for f in v.datamodel.get_related_fks([view]):
                    defin = {}
                    schema['definitions'][name]['properties'][f] = defin
                    if view.datamodel.is_relation_one_to_many(f):
                        title = self._get_pretty_name(v, 'list')
                        obj_name = self._get_pretty_name(v, 'show')
                        ref = '#/definitions/%s' % obj_name
                        defin['type'] = 'array'
                        defin['title'] = title
                        defin['items'] = [{'$ref': ref}]
                    else:
                        title = obj_name = self._get_pretty_name(v, 'show')
                        defin['$ref'] = '#/definitions/%s' % obj_name
                    schema['definitions'][obj_name] = super().convert(
                        self._get_form(v, form_type))
        return schema
