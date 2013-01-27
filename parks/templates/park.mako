<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
${base.title_string(${park.name})}
</%block>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('park.css')}">
</%block>

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
    <div id="stamp-info">
        <table class="table table-striped table-condensed" name="stamps">
            <thead>
                <tr>
                    <th class="stamp-text">Text</th>
                    <th>Last Seen</th>
                </tr>
            </thead>
            % for stamp, _, most_recent_collection_time in stamps:
                ${stamp_row(stamp, most_recent_collection_time)}
            % endfor
        </table>
    </div>
</%block>

<%def name="stamp_location_row(stamp_location, stamp_count)">
    <tr>
        <th class="stamp-location-description">${blank_if_none(stamp_location.description)}</th>
        <th class="stamp-location-address">${blank_if_none(stamp_location.address)}</th>
        <th class="stamp-location">${blank_if_none(stamp_location.latitude)} ${blank_if_none(stamp_location.longitude)}</th>
        <th class="stamp-location-count">${stamp_count}</th>
    </tr>
</%def>

<%def name="stamp_row(stamp, most_recent_collection_time)">
    <tr>
        ## This is a huge potential XSS attack. I'm not sure how to do this
        ## correctly, so... let's do a poor man's check.
        % if '<' not in stamp.text:
            <th class="stamp-text">${stamp.text.replace('\n', '<br>') | n}</th>
        % else:
            <th class="stamp-text">${stamp.text}</th>
        % endif

        % if most_recent_collection_time is not None:
            <th>${most_recent_collection_time.strftime('%Y-%m-%d')}</th>
        % else:
            <th>Never</th>
        % endif
    </tr>
</%def>

<%def name="blank_if_none(string)">
    % if string is None:
        &nbsp;
    % else:
        ${string}
    % endif
</%def>
