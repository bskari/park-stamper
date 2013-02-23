<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('All parks')}
</%block>

<%block name="content">
    <div id="park-name">
        <h1>All parks</h1>
    </div>
    <div id="park-info">
        <table class="table table-striped table-condensed" name="stamps">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Region</th>
                    <th>GPS Coordinates</th>
                </tr>
            </thead>
            % for park in parks:
                ${park_row(park)}
            % endfor
        </table>
    </div>
</%block>

<%def name="park_row(park)">
    <tr>
        <th><a href="${request.route_url('park', park_url=park.url)}">${park.name}</th>
        <th>${park.region}</th>
        <th>${base.blank_if_none(park.latitude)} ${base.blank_if_none(park.longitude)}</th>
    </tr>
</%def>
