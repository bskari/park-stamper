<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="stylesheets">
    <link rel="stylesheet" href="${base.css_url('nearby.css')}" />
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('nearby.js')}"></script>
</%block>

<%block name="inline_javascript">
    var parameters = {
        'table': $('#stamp-info .table'),
        'loadingElement': $('#loading-stamps'),
        'nearbyUrl': 'nearby.json',
        'csrfToken': '${csrf_token}'
    };
    parkStamper.nearby.init(parameters);
</%block>

<%block name="content">
    <div id="stamp-info">
        <table class="table table-striped table-condensed">
            <thead>
                <tr>
                    <th>Park</th>
                    <th class="stamp-text">Text</th>
                    <th>Location</th>
                    <th>GPS Coordinates</th>
                    <th>Distance</th>
                    <th>Last Seen</th>
                </tr>
            </thead>
        </table>
        <div id="loading-stamps">
            <hr />
            <p>Loading, please wait</p>
        </div>
    </div>
</%block>
