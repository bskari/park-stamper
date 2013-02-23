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

def include_css(context=None, string=''):
    return _return_or_write(context, '<link rel="stylesheet" type="text/css" href="' + css_url(string=string) + '">"')

def css_lib_url(context=None, string=''):
    """Generate the URL for library CSS."""
    return _return_or_write(context, '/static/css/lib/' + string)

def include_css_lib(context=None, string=''):
    return _return_or_write(context, '<link rel="stylesheet" type="text/css" href="' + css_lib_url(string=string) + '">"')

def js_url(context=None, string=''):
    """Generate the URL for ParkStamper JS."""
    return _return_or_write(context, '/static/js/src/' + string)

def include_js(context=None, string=''):
    return _return_or_write(context, '<script type="text/javascript" src="' + js_url(string=string) + '"></script>')

def js_lib_url(context=None, string=''):
    """Generate the URL for library JS."""
    return _return_or_write(context, '/static/js/lib/' + string)

def hidden_value(context=None, id='', value=''):
    """Generates a hidden input with the given id and value."""
    return _return_or_write(context, '<input type="hidden" id="' + id + '" value="' + value + '">')

def title_string(context=None, string=''):
    return _return_or_write(context, string + ' - Park Stamper')

def blank_if_none(context=None, string=''):
    return _return_or_write(context, '' if string is None else string)
