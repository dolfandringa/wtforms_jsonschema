import re


def _get_related_view_property(view, related_view, field):
    """
    Turn the field that defines the relation between a view and a related view
    into a property for jsonschema.
    """
    defin = {}
    if view.datamodel.is_relation_one_to_one(field):
        title = obj_name = _get_pretty_name(related_view, 'show')\
            .replace(' ', '')
        defin['$ref'] = '#/definitions/%s' % obj_name
    elif view.datamodel.is_relation_one_to_many(field):
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
