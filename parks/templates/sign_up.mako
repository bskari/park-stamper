<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('Sign up')}
</%block>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('park.css')}">
</%block>

<%!
from parks.templates.base.functions import css_url
stylesheet_files = [css_url(string='park.css')]
%>

<%block name="content">
    <form action="${post_url}" method="post">
        <input type="hidden" name="came-from" value="${came_from}">
        <label for="username">
            Username
        </label>
        <input type="text" name="username" id="username"><br>
        <label for="email">
            Email address
        </label>
        <input type="email" name="email" id="email"><br>
        <label for="password">
            Password
        </label>
        <input type="password" name="password"><br>
        <input type="submit" name="form.submitted" value="Sign Up" class="btn">
    </form>
</%block>
