<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="title">
% if stamp_location.description is None:
    ${base.title_string(park.name)}
% else:
    ${base.title_string(park.name + ' - ' + stamp_location.description)}
% endif
</%block>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('stamp_location.css')}">
</%block>

<%block name="content">
    <div id="description">
        <h1>${stamp_location.description}</h1>
    </div>
    <div id="park-name">
        <h2>${park.name}</h2>
    </div>

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
