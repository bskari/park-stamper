<%inherit file="base.mako"/>
<%block name="content">
    <p>${park.name}</p>
    <p>${state.name}</p>
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
</%block>

<%def name="stamp_row(stamp, location, most_recent_collection_time)">
    <tr>
        <th width="200px" style="text-align: center;">${stamp.text.replace('\n', '<br />') | n}</th>
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
