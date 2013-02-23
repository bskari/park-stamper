<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>
<%namespace file="/base/stamp_info.mako" name="stamp_info"/>

<%block name="title">
% if stamp_location.description is None:
    ${base.title_string(park.name)}
% else:
    ${base.title_string(park.name + ' - ' + stamp_location.description)}
% endif
</%block>

<%!
from parks.templates.base.functions import css_url
stylesheet_files = [css_url(string='stamp_location.css')]
%>

<%block name="content">
    <div id="description">
        <h1>${stamp_location.description}</h1>
    </div>
    <div id="park-name">
        <h2>${park.name}</h2>
    </div>

    <div class="row">
        <div id="stamp-info" class="span9">
            % if len(stamps) == 0:
                <p>
                    There doesn't seem to be any stamps here. Would you like to
                    <a href="${request.route_url(
                        'add-stamp-to-location',
                        _query={'stamp-location-id': stamp_location.id}
                    )}">add some stamps to this location</a>?
                </p>
            % else:
                ${stamp_info.stamps_table(stamps, park.id, request)}
            % endif
        </div>
    </div>
</%block>
