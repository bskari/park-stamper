<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base" />

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('park.css')}" />
</%block>

<%block name="content">
    <p>${park.name}</p>
    <p>${state.name}</p>
    <div id="stamp-info">
        <table class="table table-striped table-condensed" name="stamps">
            <thead>
                <tr>
                    <th>Text</th>
                    <th>Location</th>
                    <th>GPS Coordinates</th>
                    <th>Last Seen</th>
                </tr>
            </thead>
            % for stamp, location, most_recent_collection_time in stamps:
                ${stamp_row(stamp, location, most_recent_collection_time)}
            % endfor
        </table>
    </div>
</%block>

<%def name="stamp_row(stamp, location, most_recent_collection_time)">
    <tr>
        ## This is a huge potential XSS attack. I'm not sure how to do this
        ## correctly, so... let's do a poor man's check.
        % if '<' not in stamp.text:
            <th class="stamp-text">${stamp.text.replace('\n', '<br />') | n}</th>
        % else:
            <th class="stamp-text">${stamp.text}</th>
        % endif
        <th>${blank_if_none(location.address)}</th>
        <th>${blank_if_none(location.latitude)} ${blank_if_none(location.longitude)}</th>

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
