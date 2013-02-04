<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
${base.title_string('Add stamp to location')}
</%block>

<%block name="stylesheets">
##<link rel="stylesheet" href="${base.css_url('new_stamp.css')}">
    <link rel="stylesheet" href="${base.css_lib_url('jquery-ui.css')}">
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('add_stamp_to_location.js')}"></script>
</%block>

<%block name="inline_javascript">
    var parameters = {
        parkInputElement: $('#park'),
        stampInputElement: $('#stamp'),
        stampLocationSelect: $('#location'),
        parks: '${parks_json_string | n}',
        stampLocationsUrl: "${stamp_locations_url}",
        stampsUrl: "${stamps_url}",
        csrfToken: "${csrf_token}"
    };
    parkStamper.addStampToLocation.init(parameters);
</%block>

<%block name="content">
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
            Stamp text
        </label>
        <input type="text" name="stamp" id="stamp">
        <br>

        <input type="submit" name="form.submitted" value="Add Location" class="btn">
    </form>
</%block>
