<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="base"/>

<%block name="title">
${base.title_string('Edit stamp')}
</%block>

<%!
from parks.templates.base.functions import css_url
stylesheet_files = [css_url(string='edit_stamp.css')]
%>

<%block name="content">
    <h1>Edit stamp</h1>

    <form action="${post_url}" method="post">
        <input type="hidden" name="csrf-token" value="${csrf_token}">
        <input type="hidden" name="stamp-id" value="${stamp.id}">

        <label for="text">Text</label>
        <textarea rows="2" name="text" id="text">${stamp.text}</textarea>
        <br>

        <label for="type">Type</label>
        % for type in type_values:
            <input type="radio" name="type" value="${type}"
                % if type == stamp.type:
                    checked="checked"
                % endif
            id="type-${type}" class="checked"></input>
            <label for="type-${type}" class="checkbox">${type}</label>
        % endfor
        <br>
        <br>

        <label for="status">Status</label>
        % for status in status_values:
            <input type="radio" name="status" value="${status}"
                % if status == stamp.status:
                    checked="checked"
                % endif
            id="status-${status}"></input>
            <label for="status-${status}" class="checkbox">${status}</label>
        % endfor
        <br>
        <br>

        <input type="submit" name="form.submitted" value="Save" class="btn">
    </form>
</%block>
