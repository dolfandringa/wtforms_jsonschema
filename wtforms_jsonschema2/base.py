from wtforms.form import FormMeta
from wtforms.fields.core import (StringField, IntegerField, DateTimeField,
                                 SelectField, DecimalField, FormField,
                                 BooleanField)
from wtforms.validators import (Required, InputRequired, NumberRange, Length,
                                Email, DataRequired)
from decimal import Decimal
import logging
from .exceptions import UnsupportedFieldException
from collections import OrderedDict
from wtforms.fields import TextAreaField

log = logging.getLogger(__name__)


def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func
    return _inner


class BaseConverter(object):
    """
    The FormConverter converts wtforms to JSONSchema which can be
    communicated with other applications, and turned back into forms there.
    """

    def __init__(self, skip_fields=['csrf_token']):
        self.converters = {}
        self.skip_fields = skip_fields
        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_converter_for'):
                for classname in obj._converter_for:
                    self.converters[classname] = obj

    def _is_required(self, vals):
        return InputRequired in vals.keys() or Required in vals.keys() or \
            DataRequired in vals.keys()

    @converts(TextAreaField)
    def convert_textarea_field(self, field):
        fieldtype = 'string'
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, {}, required

    @converts(BooleanField)
    def convert_boolean_field(self, field):
        fieldtype = 'boolean'
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, {}, required

    @converts(DateTimeField)
    def date_time_field(self, field):
        fieldtype = 'string'
        options = {'format': 'date-time'}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])

        required = self._is_required(vals)

        return fieldtype, options, required

    @converts(StringField)
    def string_field(self, field):
        fieldtype = 'string'
        options = {}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])

        if Email in vals.keys():
            options['format'] = 'email'
        required = self._is_required(vals)
        if Length in vals.keys():
            options['minLength'] = vals[Length].min
            options['maxLength'] = vals[Length].max
        elif 'format' not in options.keys():
            options['maxLength'] = 255

        return fieldtype, options, required

    @converts(DecimalField)
    def decimal_field(self, field):
        fieldtype = 'number'
        options = {}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])

        required = self._is_required(vals)
        if NumberRange in vals.keys():
            options['minimum'] = vals[NumberRange].min
            options['maximum'] = vals[NumberRange].max

        return fieldtype, options, required

    @converts(IntegerField)
    def integer_field(self, field):
        fieldtype = 'integer'
        options = {}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])

        required = self._is_required(vals)
        if NumberRange in vals.keys():
            options['minimum'] = vals[NumberRange].min
            options['maximum'] = vals[NumberRange].max

        return fieldtype, options, required

    @converts(SelectField)
    def select_field(self, field):
        choices = field.choices
        if all([isinstance(c, int) for c in choices]):
            fieldtype = 'integer'
        elif all([isinstance(c, (float, Decimal, int)) for c in choices]):
            fieldtype = 'number'
        else:
            fieldtype = 'string'
        options = {'enum': choices}
        required = False
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required

    def convert_field(self, field):
        """
        Convert a field to its json schema version.
        """
        cls = field.__class__
        if cls not in self.converters.keys():
            raise UnsupportedFieldException(cls)
        d = {}
        log.debug('Using converter %s' % self.converters[cls])
        fieldtype, attrs, req = self.converters[cls](field)
        log.debug('fieldtype, attrs, req: %s, %s, %s' % (fieldtype, attrs,
                                                         req))
        if fieldtype is not None:
            d['type'] = fieldtype
        for k, v in attrs.items():
            d[k] = v
        d['title'] = field.label.text
        if field.description != '':
            d['description'] = field.description
        return d, req

    def convert(self, form):
        """
        Convert a Form to JSON Schema.
        """
        log.info("Converting form %s to JSON Schema" % form)
        if isinstance(form, FormMeta):
            form = form()
        fields = OrderedDict([(f.name, f) for f in form
                              if f.name not in self.skip_fields])
        schema = OrderedDict([
            ("type", "object"),
            ("properties", OrderedDict())
        ])
        required = []

        for key, field in fields.items():
            cls = field.__class__
            log.debug('Converting field %s of type %s' % (key, cls))
            log.debug('Supported fields: {}'.format(self.converters.keys()))
            if cls == FormField:
                log.debug("Subform: {}".format(field.form_class))
                subform = self.convert(field.form_class)
                log.debug("Converted: {}".format(subform))
                schema['properties'][key] = subform
                subform['title'] = field.label.text
                continue
            field_schema, req = self.convert_field(field)
            schema['properties'][key] = field_schema
            if req:
                required.append(key)
        if len(required) > 0:
            schema['required'] = required
        return schema
