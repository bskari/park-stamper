<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="stylesheets">
    <link rel="stylesheet" href="${base.css_url('nearby.css')}" />
</%block>

<%block name="javascript_includes">
    <script type="text/javascript" src="${base.js_url('nearby.js')}"></script>
</%block>

<%block name="inline_javascript">
    parkstamper.nearby.init($('#location'));
</%block>

<%block name="content">
    <div id="location"></div>
</%block>
