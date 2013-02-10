<%inherit file="base_templates/base.mako"/>
<%namespace module="parks.templates.base_templates.functions" name="base"/>

<%block name="title">
${base.title_string('Add stamp to location')}
</%block>

<%!
from parks.templates.base_templates.functions import css_lib_url
stylesheet_files = [css_lib_url(string='jquery-ui.css')]

from parks.templates.base_templates.functions import js_url
script_files = [js_url(string='add_stamp_to_location.js')]

inline_script = "\
    var parameters = {\
        parkInput: '#park',\
        stampLocationSelect: '#location',\
        stampInput: '#stamp-text',\
        stampSelect: '#stamp',\
        parksJsonUrl: $('#parks-json-url')[0].value,\
        stampLocationsUrl: $('#stamp-locations-url')[0].value,\
        stampsUrl: $('#stamps-url')[0].value,\
        csrfToken: $('#csrf-token')[0].value\
    };\
    parkStamper.addStampToLocation.init(parameters);\
";
%>

<%block name="content">
    <input type="hidden" id="parks-json-url" value="${request.route_url('park-names-json')}">
    <input type="hidden" id="stamp-locations-url" value="${stamp_locations_url}">
    <input type="hidden" id="stamps-url" value="${stamps_url}">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

    <h1>Add stamp to location</h1>
    <p>Found a stamp at a location?</p>

    <label for="park">
        Park
    </label>
    <input type="text" name="park" id="park">
    <br>

    <form action="${add_stamp_to_location_post_url}" method="post">
        <input type="hidden" name="csrf_token" value="${csrf_token}">

        <label for="location">
            Stamp location
        </label>
        <select name="location" id="location" disabled>
        </select>
        <br>

        <label for="stamp">
            Stamp
        </label>
        <input type="text" name="stamp-text" id="stamp-text" placeholder="Start typing stamp here">
        <br>
        <select name="stamp" id="stamp"></select>
        <br>

        <input type="submit" name="form.submitted" value="Add Stamp to Location" class="btn">
    </form>
</%block>
