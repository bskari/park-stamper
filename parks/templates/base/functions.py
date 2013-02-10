"""Functions for use in templates."""

def _return_or_write(context, string):
    """Helper function so that these functions can be called from either Mako
    Python blocks, or from Mako templates themselves.
    """
    if context is None:
        return string
    else:
        context.write(string)
        return ''

def css_url(context=None, string=''):
    """Generate the URL for ParkStamper CSS."""
    return _return_or_write(context, '/static/css/' + string)

def css_lib_url(context=None, string=''):
    """Generate the URL for library CSS."""
    return _return_or_write(context, '/static/css/lib/' + string)

def js_url(context=None, string=''):
    """Generate the URL for ParkStamper JS."""
    return _return_or_write(context, 'static/js/src/' + string)

def js_lib_url(context=None, string=''):
    """Generate the URL for library JS."""
    return _return_or_write(context, '/static/js/lib/' + string)

def title_string(context=None, string=''):
    return _return_or_write(context, string + ' - Park Stamper')
