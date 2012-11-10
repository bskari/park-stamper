<%inherit file="base.mako"/>
<%block name="content">
    <p>Hello, world!</p>
    <p>${park.name}</p>
    <p>${park.state_id}</p>
    <table class="table table-striped table-condensed" name="stamps">
        <thead>
            <tr>
                <th>Text</th>
                <th>Location</th>
                <th>GPS Coordinates</th>
                <th>Last Collection Time</th>
            </tr>
        </thead>
        % for stamp, most_recent_collection_time in stamps:
            ${stamp_row(stamp, most_recent_collection_time)}
        % endfor
    </table>
</%block>

<%def name="stamp_row(stamp, most_recent_collection_time)">
    <tr>
        <th>${stamp.text.replace('\n', '<br />') | n}</th>
        <th>${blank_if_none(stamp.location)}</th>
        <th>${blank_if_none(stamp.latitude)} ${blank_if_none(stamp.longitude)}</th>

        % if most_recent_collection_time is not None:
            <th>${most_recent_collection_time}</th>
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
