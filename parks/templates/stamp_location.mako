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
            ${stamp_info.stamps_table(stamps, park.id, request)}
        </div>
    </div>
</%block>
