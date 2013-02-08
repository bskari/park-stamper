<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
${base.title_string(park.name)}
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
    <div class="row">
        <div id="stamp-info" class="span9">
            ## TODO(bskari|2013-02-08) This table is identical to the one on
            ## the stamp location page - factor out this functionality.
            <table class="table table-striped table-condensed" name="stamps">
                <thead>
                    <tr>
                        <th class="stamp-text">Text</th>
                        <th class="stamp-status">Status</th>
                        <th class="stamp-last-seen">Last Seen</th>
                        <th class="stamp-actions">Actions</th>
                    </tr>
                </thead>
                % for stamp, _, most_recent_collection_time in stamps:
                    ${stamp_row(stamp, most_recent_collection_time)}
                % endfor
            </table>
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
                ${stamp_location.address.replace('\n', '<br>') | n}</th>
            % else:
                ${blank_if_none(stamp_location.address)}</th>
            %endif
        </th>
        <th class="stamp-location">${blank_if_none(stamp_location.latitude)} ${blank_if_none(stamp_location.longitude)}</th>
        <th class="stamp-location-count">${stamp_count}</th>
    </tr>
</%def>

<%def name="stamp_row(stamp, most_recent_collection_time)">
    <tr>
        ## This is a huge potential XSS attack. I'm not sure how to do this
        ## correctly, so... let's do a poor man's check.
        % if '<' not in stamp.text:
            <td class="stamp-text">${stamp.text.replace('\n', '<br>') | n}</th>
        % else:
            <td class="stamp-text">${stamp.text}</td>
        % endif

        <td>${stamp.status}</td>

        % if most_recent_collection_time is not None:
            <td>${most_recent_collection_time.strftime('%Y-%m-%d')}</td>
        % else:
            <td>Never</td>
        % endif

        <td>
            <a class="btn btn-small btn-primary" href="#" title="Add this stamp to your collection!">
                <i class="icon-ok icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary" href="#" title="Edit this stamp">
                <i class="icon-edit icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary" href="#" title="Report stamp as missing">
                <i class="icon-remove icon-white"></i>
            </a>
        </td>
    </tr>
</%def>

<%def name="blank_if_none(string)">
    % if string is None:
        &nbsp;
    % else:
        ${string}
    % endif
</%def>
