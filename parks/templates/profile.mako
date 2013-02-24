<%inherit file="base/base.mako"/>
<%namespace module="parks.templates.base.functions" name="functions"/>

<%block name="title">
${functions.title_string('Profile')}
</%block>

<%def name="stylesheet_files()">
##${functions.include_css('profile.css')}
</%def>

<%block name="content">
    <div class="row">
        % if personal_profile:
            <h1>Your profile</h1>
        % else:
            <h1>${username}&apos;s profile</h1>
        % endif
    </div>
    <div class="row">
        <div class="span9">
            % if personal_profile:
                <h2>Your collections (last ${days} days)</h2>
            % else:
                <h2>${username}&apos;s collections (last ${days} days)</h2>
            % endif
            ${collection_table(stamp_collections)}
            <hr>

            % if personal_profile:
                <h2>Your information</h2>
            % endif
        </div>
    </div>
</%block>


<%def name="collection_table(collections)">
    <table class="table table-striped table-condensed" name="collections">
        <thead>
            <tr>
                <th>Stamp</th>
                <th>Park</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            % for collection in collections:
                <tr>
                    <td>
                        % if '<' not in collection.Stamp.text:
                            ${collection.Stamp.text.replace("\n", '<br>') | n}
                        % else:
                            ${collection.Stamp.text}
                        % endif
                    </td>
                    <td>
                        <a href="${request.route_url('park', park_url=collection.Park.url)}">
                            ${collection.Park.name}
                        </a>
                    </td>
                    <td>${collection.StampCollection.date_collected}</td>
                </tr>
            % endfor
        </tbody>
    </table>
</%def>
