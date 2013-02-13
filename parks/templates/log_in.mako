<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('Log in')}
</%block>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('park.css')}">
</%block>

<%!
from parks.templates.base.functions import css_url
stylesheet_files = [css_url(string='park.css')]
%>

<%block name="content">
    <form action="${url}" method="post">
        <input type="hidden" name="csrf-token" value="${csrf_token}">
        <input type="hidden" name="came-from" value="${came_from}">
        <label for="login">
            Username or email address
        </label>
        <input type="text" name="login" id="login" value="${login}"><br>
        <label for="password">
            Password
        </label>
        <input type="password" name="password" value="${login}"><br>
        <input type="submit" name="form.submitted" value="Log In" class="btn">
    </form>
</%block>
