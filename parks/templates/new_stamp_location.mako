<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('New stamp location')}
</%block>

<%!
from parks.templates.base.functions import css_lib_url
stylesheet_files = [css_lib_url(string='jquery-ui.css')]

from parks.templates.base.functions import js_url
script_files = [js_url(string='new_stamp_location.js')]

inline_script = "\
    var parameters = {\
        parkInputSelector: '#park',\
        parksJsonUrlSelector: '#parks-json-url',\
        loadPositionSelector: '#load-position',\
        latitudeSelector: '#latitude',\
        longitudeSelector: '#longitude',\
        csrfTokenSelector: '#csrf-token'\
    };\
    parkStamper.newStampLocation.init(parameters);\
"
%>

<%block name="content">
    <input type="hidden" id="parks-json-url" value="${request.route_url('park-names-json')}">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

    <h1>New location</h1>
    <p>Found a place with stamps? Give me the skinny!</p>

    <form action="${post_url}" method="post">
        <label for="park">
            Park
        </label>
        <input type="text" name="park" id="park" required>
        <br>

        <label for="description">
            Description
        </label>
        <input type="text" name="description" id="description" required>
        <br>

        <label for="address">
            Address (optional)
        </label>
        <textarea name="address" id="address"></textarea>
        <br>

        <label for="latitude">
            Latitude (optional)
        </label>
        <input type="number" name="latitude" id="latitude">
        <br>

        <label for="longitude">
            Longitude (optional)
        </label>
        <input type="number" name="longitude" id="longitude">
        <br>

        ${base.show_if_mobile(
            request.user_agent,
            '<input type="submit" id="load-position" value="Fill in current location information" class="btn">'
            '<br>'
            '<br>'
        )}

        <input type="hidden" name="csrf-token" value="${csrf_token}">

        <input type="submit" name="new-stamp-location" value="Add Location" class="btn btn-primary">
    </form>
</%block>
