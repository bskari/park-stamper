<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base" />

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('parks.css')}" />
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
        <th>${park.name}</th>
        <th>${park.region}</th>
        <th>${blank_if_none(park.latitude)} ${blank_if_none(park.longitude)}</th>
    </tr>
</%def>

<%def name="blank_if_none(string)">
    % if string is None:
        &nbsp;
    % else:
        ${string}
    % endif
</%def>
