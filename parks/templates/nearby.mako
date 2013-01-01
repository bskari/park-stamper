<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
Nearby stamps - Park Stamper
</%block>

<%block name="stylesheets">
    <link rel="stylesheet" href="${base.css_url('nearby.css')}" />
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('nearby.js')}"></script>
</%block>

<%block name="inline_javascript">
    var parameters = {
        'tableBody': $('#stamp-info table tbody'),
        'loadingElement': $('#loading-stamps'),
        'nearbyUrl': 'nearby.json',
        'distance': $('#distance'),
        'csrfToken': '${csrf_token}'
    };
    parkStamper.nearby.init(parameters);
</%block>

<%block name="content">
    <h1>Nearby stamps</h1>

    <div class="row">
        <div class="span12" style="text-align: center;">
            Find stamps within:
            <select id="distance">
                <option value="10">10</option>
                <option value="25" selected>25</option>
                <option value="50">50</option>
                <option value="100">100</option>
            </select>
            miles
        </div>
    </div>

    <div class="row">
        <div class="span12" id="stamp-info">
            <table class="table table-striped table-condensed">
                <thead>
                    <tr>
                        <th>Park</th>
                        <th class="stamp-text">Text</th>
                        <th>Location</th>
                        <th>GPS Coordinates</th>
                        <th>Direction</th>
                        <th>Last Seen</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            <div id="loading-stamps">
                <hr />
                <p>Loading, please wait</p>
            </div>
        </div>
    </div>
</%block>
