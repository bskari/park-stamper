<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('New stamp')}
</%block>

<%!
from parks.templates.base.functions import css_lib_url
stylesheet_files = [css_lib_url(string='jquery-ui.css')]

from parks.templates.base.functions import js_url
script_files = [js_url(string='new_stamp.js')]

inline_script = "\
    var parameters = {\
        parkInputElement: $('#park'),\
        stampLocationSelect: $('#location'),\
        parksJsonUrl: $('#parks-json-url')[0].value,\
        stampLocationsUrl: $('#stamp-locations-url')[0].value,\
        csrfToken: $('#csrf-token')[0].value\
    };\
    parkStamper.newStamp.init(parameters);\
"
%>

<%block name="content">
    <input type="hidden" id="parks-json-url" value="${request.route_url('park-names-json')}">
    <input type="hidden" id="stamp-locations-url" value="${request.route_url('stamp-locations-json')}">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

    <h1>New stamp</h1>
    <p>Found a new stamp, eh? Tell me more!</p>

    <label for="park">
        Park
    </label>
    <input type="text" name="park" id="park">
    <br>

    <form action="${post_url}" method="post">
        <input type="hidden" name="csrf-token" value="${csrf_token}">

        <label for="location">
            Stamp location
        </label>
        <select name="location" id="location" disabled>
        </select>
        <br>

        <label for="text">
            Stamp text
        </label>
        <textarea rows="2" name="text" id="text"></textarea>
        <br>

        <input type="submit" name="form.submitted" value="Add Stamp" class="btn">
    </form>
</%block>
