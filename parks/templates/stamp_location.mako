<%inherit file="base_templates/base.mako"/>
<%namespace file="/base_templates/base.mako" name="base"/>
<%namespace file="/base_templates/stamp_info.mako" name="stamp_info"/>

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

    <div class="row">
        <div id="stamp-info" class="span9">
            ${stamp_info.stamps_table(stamps)}
        </div>
</%block>
