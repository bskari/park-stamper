<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="functions"/>
<%namespace file="/base/stamp_info.mako" name="stamp_info"/>

<%block name="title">
${functions.title_string(park.name)}
</%block>

<%def name="stylesheet_files()">
${functions.include_css('park.css')}
</%def>

<%block name="content">
    <div id="park-name">
        <h1>${park.name}</h1>
    </div>
    <div id="state">
        <h2>${state.name}</h2>
    </div>

    <h3>Stamp locations</h3>
    <div id="stamp-location-info">
        <table class="table table-striped table-condensed" name="stamp-locations">
            <thead>
                <tr>
                    <th class="stamp-location-description">Description</th>
                    <th class="stamp-location-address">Address</th>
                    <th class="stamp-location">Location</th>
                    <th class="stamp-location-count">Stamps</th>
                </tr>
            </thead>
            % for stamp_location, stamp_count in stamp_locations:
                ${stamp_location_row(stamp_location, stamp_count)}
            % endfor
        </table>
    </div>

    <h3>Stamps</h3>
    <div class="row">
        <div id="stamp-info" class="span9">
            ${stamp_info.stamps_table(stamps, park.id, request)}
        </div>
    </div>
</%block>

<%def name="stamp_location_row(stamp_location, stamp_count)">
    <tr>
        <th class="stamp-location-description">
            <a href="${request.route_url('stamp-location', id=stamp_location.id, park=park.name)}">
                ${stamp_location.description}
            </a>
        </th>
        <th class="stamp-location-address">
            ## This is a huge potential XSS attack. I'm not sure how to do this
            ## correctly, so... let's do a poor man's check.
            % if stamp_location.address is not None and '<' not in stamp_location.address:
                ${stamp_location.address.replace('\n', '<br>') | n}
            % else:
                ${blank_if_none(stamp_location.address)}
            %endif
        </th>
        <th class="stamp-location">${blank_if_none(stamp_location.latitude)} ${blank_if_none(stamp_location.longitude)}</th>
        <th class="stamp-location-count">${stamp_count}</th>
    </tr>
</%def>

<%def name="blank_if_none(string)">
    % if string is None:
        &nbsp;
    % else:
        ${string}
    % endif
</%def>
