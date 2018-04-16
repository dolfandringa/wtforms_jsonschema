from flask_appbuilder.fields import QuerySelectField
import logging
from .base import BaseConverter, converts
from decimal import Decimal

log = logging.getLogger(__name__)


class FABConverter(BaseConverter):
    """
    The FABConverter extends BaseConverter with functioality for
    flask appbuilder.
    """

    @converts(QuerySelectField)
    def query_select_field(self, field):
        choices = field.query_func()
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
