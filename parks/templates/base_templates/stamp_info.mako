<%def name="stamps_table(stamps)">
    <table class="table table-striped table-condensed" name="stamps">
        <thead>
            <tr>
                <th class="stamp-text">Text</th>
                <th class="stamp-status">Status</th>
                <th class="stamp-last-seen">Last Seen</th>
                <th class="stamp-actions">Actions</th>
            </tr>
        </thead>
        % for stamp, _, most_recent_collection_time in stamps:
            ${stamp_row(stamp, most_recent_collection_time)}
        % endfor
    </table>
</%def>

<%def name="stamp_row(stamp, most_recent_collection_time)">
    <tr>
        ## This is a huge potential XSS attack. I'm not sure how to do this
        ## correctly, so... let's do a poor man's check.
        % if '<' not in stamp.text:
            <td class="stamp-text">${stamp.text.replace('\n', '<br>') | n}</th>
        % else:
            <td class="stamp-text">${stamp.text}</td>
        % endif

        <td>${stamp.status}</td>

        % if most_recent_collection_time is not None:
            <td>${most_recent_collection_time.strftime('%Y-%m-%d')}</td>
        % else:
            <td>Never</td>
        % endif

        <td>
            <a class="btn btn-small btn-primary" href="#" title="Add this stamp to your collection!">
                <i class="icon-ok icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary" href="#" title="Edit this stamp">
                <i class="icon-edit icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary" href="#" title="Report stamp as missing">
                <i class="icon-remove icon-white"></i>
            </a>
        </td>
    </tr>
</%def>
