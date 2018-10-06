from collections import OrderedDict
from .utils import _get_related_view_property


class ViewCondition:
    """
    Base class for view conditions.
    """
    def __init__(self, conditions):
        self.conditions = conditions

    def get_json_schema(self, view):
        """Return the JSON Schema version of this condition."""
        raise NotImplementedError("get_json_schema is not implemented on {}"
                                  .format(self.__class__))


class oneOf(ViewCondition):
    """
    A wtforms version of the jsonschema oneOf attribute that allows you to
    specify that onlye one of a set of related views should be filled in, based
    on the values of other fields.

    It should receive a dictionary where the keys are related views
    and the value is a dictionary of property/value combinations that
    when satisfied, mean that related view should be required
    (and not the others).
    """

    def get_json_schema(self, view, converter):
        """Return the JSON Schema version of this condition."""
        schema = []
        for rel_view, condition in self.conditions.items():
            schema_cond = OrderedDict([('properties', OrderedDict()),
                                       ('required', [])])
            for fieldname, val in condition.items():
                field, req = converter.convert_field(getattr(view().add_form(),
                                                             fieldname))
                if not isinstance(val, list):
                    val = [val]
                if 'enum' in field.keys():
                    # convert val to the same format as the enum field
                    newvals = []
                    for v in val:
                        for c in field['enum']:
                            if isinstance(c, dict) and c['id'] == v:
                                newvals.append(c)
                            elif c == v:
                                newvals.append(c)
                    val = newvals
                schema_cond['properties'][fieldname] = {'enum': val}
                schema_cond['required'].append(fieldname)

            for field in rel_view.datamodel.get_related_fks([view]):
                defin = _get_related_view_property(view, rel_view, field)
                schema_cond['properties'][field] = defin
                schema_cond['required'].append(field)
            schema.append(schema_cond)
        return ('oneOf', schema)
