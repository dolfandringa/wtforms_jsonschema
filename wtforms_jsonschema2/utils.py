import re
import logging


log = logging.getLogger(__name__)


def _get_related_view_property(view, related_view, field):
    """
    Turn the field that defines the relation between a view and a related view
    into a property for jsonschema.
    """
    defin = {}
    log.debug('Checking view {}, related view {} and field {}'
              .format(view, related_view, field))
    if view.datamodel.is_relation_one_to_one(field):
        log.debug('Got a one-to-one relation')
        title = obj_name = _get_pretty_name(related_view, 'show')\
            .replace(' ', '')
        defin['$ref'] = '#/definitions/%s' % obj_name
    elif view.datamodel.is_relation_one_to_many(field):
        log.debug('Got a one-to-many relation')
        title = _get_pretty_name(related_view, 'list')
        obj_name = _get_pretty_name(related_view, 'show').replace(' ', '')
        ref = '#/definitions/%s' % obj_name
        defin['type'] = 'array'
        defin['title'] = title
        defin['items'] = [{'$ref': ref}]
    else:
        title = obj_name = _get_pretty_name(related_view, 'show')\
            .replace(' ', '')
        defin['$ref'] = '#/definitions/%s' % obj_name
    return defin


def _is_parent_related_view_property(view, parent_view, field):
    log.debug('Checking parent related property for {}, parent {} and field {}'
              .format(view, parent_view, field))
    if view.datamodel.is_relation(field):
        parent_properties = parent_view.datamodel.get_related_fks([view])
        log.debug('parent properties: {}'.format(parent_properties))
        return field in parent_properties
    else:
        return False


def _get_view_name(view):
    return _get_pretty_name(view, 'show').replace(' ', '')


def _get_pretty_name(view, form_type):
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
