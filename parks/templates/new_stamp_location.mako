<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
${base.title_string('New stamp location')}
</%block>

<%block name="stylesheets">
##<link rel="stylesheet" href="${base.css_url('new_stamp.css')}">
    <link rel="stylesheet" href="${base.css_lib_url('jquery-ui.css')}">
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('new_stamp_location.js')}"></script>
</%block>

<%block name="inline_javascript">
    var parameters = {
        parkInputElement: $('#park'),
        parks: '${parks_json_string | n}',
        csrfToken: '${csrf_token}'
    };
    parkStamper.newStampLocation.init(parameters);
</%block>

<%block name="content">
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
            Address
        </label>
        <input type="text" name="address" id="address">
        <br>

        <label for="latitude">
            Latitude
        </label>
        <input type="number" name="latitude" id="latitude">
        <br>

        <label for="longitude">
            Longitude
        </label>
        <input type="number" name="longitude" id="longitude">
        <br>

        <input type="hidden" name="csrf_token" value="${csrf_token}">

        <input type="submit" name="form.submitted" value="Add Location" class="btn">
    </form>
</%block>
