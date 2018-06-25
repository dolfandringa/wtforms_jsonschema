import logging
from .base import converts
from .fab import FABConverter
from wtforms.form import Form
from wtforms.fields import FormField
from fab_geoalchemy import PointField
from copy import deepcopy


log = logging.getLogger(__name__)


class GeoFABConverter(FABConverter):
    """
    Extends the FABConverter with GeoAlchemy2 support for geographic data.
    """

    def convert(self, views, form_type='add'):
        log.debug("Calling GeoFABConverter.convert")
        if isinstance(views, Form) or issubclass(views, Form):
            return super(FABConverter, self).convert(views)
        newviews = []
        try:
            iter(views)
        except TypeError:
            views = [views]
        for view in views:
            if isinstance(view, Form):
                form = view
                newviews.append(view)
            else:
                view = view()
                newviews.append(view)
                form = self._get_form(view, form_type)
            for fname in dir(form):
                if fname.startswith('_'):
                    continue
                field = getattr(form, fname)
                if fname in self.skip_fields:
                    continue
                log.debug('Checking field {}'.format(fname))
                if hasattr(field, 'field_class') and \
                        field.field_class == PointField:
                    log.debug("{} is a pointfield".format(fname))
                    delattr(form, fname)
                    latfield = deepcopy(field)
                    latfield.args = ['Latitude']+list(field.args)[1:]
                    latfield.kwargs['coordinate_type'] = 'latitude'
                    lonfield = deepcopy(field)
                    lonfield.args = ['Longitude']+list(field.args)[1:]
                    lonfield.kwargs['coordinate_type'] = 'longitude'

                    class subform(Form):
                        pass
                    subform.lat = latfield
                    subform.lon = lonfield
                    setattr(form, fname, FormField(subform))
        return super().convert(newviews, form_type)

    @converts(PointField)
    def convert_point_field(self, field):
        fieldtype = 'string'
        options = {'format': 'coordinate_point_{}'.format(
            field.coordinate_type)}
        vals = dict([(v.__class__, v) for v in field.validators])
        required = self._is_required(vals)

        return fieldtype, options, required
