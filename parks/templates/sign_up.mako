<%inherit file="base_templates/base.mako"/>
<%namespace file="/base_templates/base.mako" name="base"/>

<%block name="title">
${base.title_string('Sign up')}
</%block>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('park.css')}">
</%block>

<%block name="content">
    <form action="${url}" method="post">
        <input type="hidden" name="csrf_token" value="${csrf_token}">
        <input type="hidden" name="came_from" value="${came_from}">
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
