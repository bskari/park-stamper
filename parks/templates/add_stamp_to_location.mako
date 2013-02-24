<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('Add stamp to location')}
</%block>

<%!
from parks.templates.base.functions import css_lib_url
from parks.templates.base.functions import css_url
stylesheet_files = [
    css_lib_url(string='jquery-ui.css'),
    css_lib_url(string='jquery.multiselect.css'),
    css_url(string='add_stamp_to_location.css'),
]

from parks.templates.base.functions import js_lib_url
from parks.templates.base.functions import js_url
script_files = [
    js_lib_url(string='jquery.multiselect.min.js'),
    js_url(string='add_stamp_to_location.js'),
]

inline_script = "\
    var parameters = {\
        parkInputSelector: '#park',\
        stampLocationSelector: '#location',\
        stampInputSelector: '#stamp-text',\
        stampSelector: '#stamp',\
        parksJsonUrlSelector: '#parks-json-url',\
        stampLocationsUrlSelector: '#stamp-locations-url',\
        stampsUrlSelector: '#stamps-url',\
        stampLocationIdSelector: '#stamp-location-id',\
        csrfTokenSelector: '#csrf-token'\
    };\
    parkStamper.addStampToLocation.init(parameters);\
";
%>

<%block name="content">
    <input type="hidden" id="parks-json-url" value="${request.route_url('park-names-json')}">
    <input type="hidden" id="stamp-locations-url" value="${stamp_locations_url}">
    <input type="hidden" id="stamps-url" value="${stamps_url}">
    <input type="hidden" id="stamp-location-id" value="${stamp_location_id}">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

    <h1>Add stamps to location</h1>
    <p>Found a stamp at a location?</p>

    <label for="park">
        Park
    </label>
    % if park_name is None:
        <input type="text" name="park" id="park">
    % else:
        <input type="text" name="park" id="park" value="${park_name}">
    % endif
    <br>

    <form action="${add_stamp_to_location_post_url}" method="post">
        <input type="hidden" name="csrf-token" value="${csrf_token}">

        <label for="location">
            Stamp location
        </label>
        <select name="location" id="location" disabled>
        </select>
        <br>

        <label for="stamp-text">
            Stamp
        </label>
        <input type="text" name="stamp-text" id="stamp-text" placeholder="Start typing stamp text here">
        <br>
        <select name="stamp" id="stamp" multiple="multiple"></select>
        <br>

        <input type="submit" name="add-stamp-to-location" value="Add Stamps to Location" class="btn">
    </form>
</%block>
