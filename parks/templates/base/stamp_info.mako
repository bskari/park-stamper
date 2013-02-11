<%namespace module="parks.templates.base.functions" name="functions"/>

<%def name="stamps_table(stamps, request)">
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
            ${_stamp_row(stamp, most_recent_collection_time)}
        % endfor
    </table>
</%def>

<%def name="inline_script()">
var parameters = {
    'collectStampUrl': 'test',
    'rowSelector': 'table[name=stamps] tbody tr',
    'csrfToken': $('#csrf-token')[0].value
};
parkStamper.collectStamp.init(parameters);
</%def>

<%def name="script_files()">
${functions.include_js('collect_stamp.js')}
</%def>

<%def name="_stamp_row(stamp, most_recent_collection_time)">
    <tr>
        ## This is a huge potential XSS attack. I'm not sure how to do this
        ## correctly, so... let's do a poor man's check.
        <td class="stamp-text">
            % if '<' not in stamp.text:
                ${stamp.text.replace('\n', '<br>') | n}
            % else:
                ${stamp.text}
            % endif
        </td>

        <td>${stamp.status}</td>

        % if most_recent_collection_time is not None:
            <td>${most_recent_collection_time.strftime('%Y-%m-%d')}</td>
        % else:
            <td>Never</td>
        % endif

        <td>
            <input type="hidden" value="${stamp.id}">
            <a class="btn btn-small btn-primary collect-stamp" href="#" title="Add this stamp to your collection!">
                <i class="icon-ok icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary edit-stamp" href="#" title="Edit this stamp">
                <i class="icon-edit icon-white"></i>
            </a>
            <a class="btn btn-small btn-primary report-stamp" href="#" title="Report stamp as missing">
                <i class="icon-remove icon-white"></i>
            </a>
        </td>
    </tr>
</%def>