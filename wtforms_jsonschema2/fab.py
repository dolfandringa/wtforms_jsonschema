from flask_appbuilder.fields import (QuerySelectField,
                                     QuerySelectMultipleField, EnumField)
from flask_appbuilder.upload import ImageUploadField
from collections import OrderedDict
import logging
from .base import BaseConverter, converts
from .utils import (_get_pretty_name, _get_related_view_property,
                    _is_parent_related_view_property, _get_view_name)
from wtforms.form import Form


log = logging.getLogger(__name__)


class FABConverter(BaseConverter):
    """
    The FABConverter extends BaseConverter with functioality for
    flask appbuilder.
    """

    @converts(EnumField)
    def convert_enum_field(self, field):
        fieldtype = 'object'
        options = {'enum': [{'id': c[0], 'label': str(c[1])}
                            for c in field.iter_choices()]}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

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

    def convert_view(self, view, form_type='add', parentView=None):
        schema = OrderedDict([
            ('type', 'object'),
            ('definitions', OrderedDict([])),
            ('properties', OrderedDict([]))
        ])
        # name = _get_pretty_name(view, 'show').replace(' ', '')
        name = _get_view_name(view)
        view_definition = super().convert(
            self._get_form(view,  form_type))
        schema['definitions'][name] = view_definition
        if parentView is not None:
            # Remove references to ParientView
            for propkey in view_definition['properties'].keys():
                if _is_parent_related_view_property(view, parentView, propkey):
                    log.debug('removing {}'.format(propkey))
                    del view_definition['properties'][propkey]
                    if propkey in view_definition['required']:
                        view_definition['required'].remove(propkey)
                else:
                    log.debug('Keeping {}'.format(propkey))
        view_definition['title'] = _get_pretty_name(view, 'show')
        schema['properties'][name] = {'$ref': '#/definitions/%s' % name}
        conditions = []
        if hasattr(view, '_conditional_relations'):
            conditions = view._conditional_relations
            for condition in conditions:
                ckey, cval = condition.get_json_schema(view, self)
                schema['definitions'][name][ckey] = cval
        conditional_views = [cv for cond in conditions
                             for cv in cond.affected_views]
        if view.related_views is not None:
            for v in view.related_views:
                rel_name, rel_schema = self.convert_view(v, form_type,
                                                         parentView=view)
                for defin_k, defin in rel_schema['definitions'].items():
                    schema['definitions'][defin_k] = defin
                if v in conditional_views:
                    # Related view is conditional so don't add to properties
                    continue
                for f in v.datamodel.get_related_fks([view]):
                    defin = _get_related_view_property(view, v, f)
                    schema['definitions'][name]['properties'][f] = defin
        return name, schema

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
            name, view_schema = self.convert_view(view, form_type)
            for k, v in view_schema['definitions'].items():
                schema['definitions'][k] = v
            for k, v in view_schema['properties'].items():
                schema['properties'][k] = v
        return schema
