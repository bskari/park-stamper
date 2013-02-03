<%inherit file="base.mako"/>
<%namespace file="/base.mako" name="base"/>

<%block name="stylesheets">
<link rel="stylesheet" href="${base.css_url('home.css')}">
</%block>

<%block name="inline_javascript">
$('#park-carousel').carousel({'interval': 5000, 'cycle': true});
</%block>

<%block name="content">

    <div class="row">
        <div class="span12" style="text-align: center;">
            <h1>Track and find your NPS passport stamps</h1>
            <a class="btn btn-large btn-success" href="${urls['nearby']}">
                Find nearby stamps now!
            </a>
        </div>
    </div>

    <div class="row" style="margin-top: 20px;">
        <div class="span9">
            <div id="park-carousel" class="carousel slide" style="width: 640px; margin-left: auto; margin-right: auto;">
                <div class="carousel-inner">
                    % for num, (img_url, header, caption, url) in enumerate(carousel_information):
                        % if num == 0:
                            <div class="active item">
                        % else:
                            <div class="item">
                        % endif
                            <img src="${img_url}" alt="${caption}">
                            <a href="${url}">
                                <span class="carousel-caption">
                                    <h4>${header}</h4>
                                    <p>${caption}</p>
                                </span>
                            </a>
                        </div>
                    % endfor
                </div>
                <a class="carousel-control left" href="#park-carousel" data-slide="prev">&lsaquo;</a>
                <a class="carousel-control right" href="#park-carousel" data-slide="next">&rsaquo;</a>
            </div>
        </div>
        <div class="span3">
            <h3>Recent activity</h3>
            <ul class="recent-activity-list">
                % for item in recent:
                    ${recent_activity_li(item)}
                % endfor
            </ul>
        </div>
    </div>

    <div class="row">
        <div class="span4">
            <div class="inner">
                <strong>Track your progress</strong>
                <p>Register which stamps you have collected. Make sure you don't miss any, and keep track of new ones.</p>
            </div>
        </div>
        <div class="span4">
            <div class="inner">
                <strong>Stay up to date</strong>
                <p>Old stamps are continually being retired, and new stamps are being released. Keep track of the newest stamps to keep your collection up to date.</p>
            </div>
        </div>
        <div class="span4">
            <div class="inner">
                <strong>Share with friends</strong>
                <p>Show how many stamps you've collected. Update stamps listings instantly. Tell others when new stamps are added or old ones are removed.</p>
            </div>
        </div>
    </div>

</%block>


<%def name="recent_activity_li(recent_item)">
    <li class="recent-activity">
        <a class="url" href="${recent_item.username}">
            ## TODO(bskari|2013-02-02) Link to user profile
            ${recent_item.username}
        </a>
        collected a stamp from
        <a class="url" href="${request.route_url('park', park_url=recent_item.park_url)}">
            ${recent_item.park_name}
        </a>
    </li>
</%def>
