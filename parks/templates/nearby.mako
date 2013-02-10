<%inherit file="base_templates/base.mako"/>
<%namespace module="parks.templates.base_templates.functions" name="base"/>

<%block name="title">
${base.title_string('Nearby stamps')}
</%block>

<%!
from parks.templates.base_templates.functions import css_url
from parks.templates.base_templates.functions import css_lib_url
stylesheet_files = [
    css_url(string='nearby.css'),
    css_lib_url(string='tablesorter.css'),
]

from parks.templates.base_templates.functions import js_url
from parks.templates.base_templates.functions import js_lib_url
script_files = [
    js_url(string='nearby.js'),
    js_lib_url(string='jquery.tablesorter.min.js'),
]

inline_script = "\
    var parameters = {\
        'table': $('#stamps-table'),\
        'loadingElement': $('#loading-stamps'),\
        'nearbyUrl': 'nearby.json',\
        'distance': $('#distance'),\
        'csrfToken': $('#csrf-token')[0].value\
    };\
    parkStamper.nearby.init(parameters);\
"
%>

<%block name="content">
    <input type="hidden" id="csrf-token" value="${csrf_token}">

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
            <table class="table table-striped table-condensed tablesorter" id="stamps-table">
                <thead>
                    <tr style="border-top: 1px solid black;">
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
                <hr>
                <p>Loading, please wait</p>
            </div>
        </div>
    </div>
</%block>
