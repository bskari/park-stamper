<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
New Stamp - Park Stamper
</%block>

<%block name="stylesheets">
##<link rel="stylesheet" href="${base.css_url('new_stamp.css')}">
    <link rel="stylesheet" href="${base.css_lib_url('jquery-ui.css')}">
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('new_stamp.js')}"></script>
</%block>

<%block name="inline_javascript">
    var parameters = {
        parkInputElement: $('#park'),
        stampLocationSelect: $('#location'),
        parks: '${parks_json_string | n}',
        stampLocationsUrl: "${request.route_url('stamp-locations-json')}",
        csrfToken: '${csrf_token}'
    };
    parkStamper.newStamp.init(parameters);
</%block>

<%block name="content">
    <h1>New stamp</h1>
    <p>Found a new stamp, eh? Tell me more!</p>

    <label for="park">
        Park
    </label>
    <input type="text" name="park" id="park">
    <br>

    <form action="${url}" method="post">
        <input type="hidden" name="csrf_token" value="${csrf_token}">

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