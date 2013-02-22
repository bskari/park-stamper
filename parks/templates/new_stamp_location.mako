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
        parkInputElement: $('#park'),\
        parksJsonUrl: $('#parks-json-url')[0].value,\
        csrfToken: $('#csrf-token')[0].value\
    };\
    parkStamper.newStampLocation.init(parameters);\
"
%>

<%block name="content">
    <input type="hidden" id="parks-json-url" value="${request.route_url('park-names-json')}">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

    <h1>New location</h1>
    <p>Found a place with stamps? Give me the skinny!</p>

    <form action="${url}" method="post">
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
        <input type="text" name="address" id="address">
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

        <input type="hidden" name="csrf-token" value="${csrf_token}">

        <input type="submit" name="form.submitted" value="Add Location" class="btn">
    </form>
</%block>
