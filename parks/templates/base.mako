<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8">
        <!--[if lt IE 9]>
            <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
        <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
        <link rel="stylesheet" href="${css_url('custom.css')}">
        <link href="http://fonts.googleapis.com/css?family=Merriweather:bold" rel="stylesheet" type="text/css">
        <link href="http://fonts.googleapis.com/css?family=Open%20Sans" rel="stylesheet" type="text/css">
        <%block name="stylesheets"/>
        <title>
            <%block name="title">
                Park Stamper
            </%block>
        </title>
    </head>
    <body>
        <div class="navbar navbar-inverse navbar-fixed-top">
            <div class="navbar-inner">
                <div class="container">
                    <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </a>
                    <a class="brand" href="${request.application_url}">Park Stamper</a>
                    <div class="nav-collapse collapse">
                        <ul class="nav">
                            <li id="nav-li-all-parks"><a href="${request.application_url}/all-parks">All parks</a></li>
                            <li id="nav-li-nearby"><a href="${request.application_url}/nearby">Nearby</a></li>
                        </ul>
                        <ul class="nav actions">
                            % if user_id:
                                <li><a href="${request.application_url}/log-out">Log out</a></li>
                            % else:
                                <li><a href="${request.application_url}/log-in">Log in</a></li>
                                <li><a href="${request.application_url}/sign-up">Sign up</a></li>
                            % endif
                        </ul>
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>

        <div id="content" class="container-narrow">
            ## Error and warning alerts
            % if error:
                <div class="alert alert-error">
                    <button type="button" class="close" data-dismiss="alert">&times</button>
                    ${error}
                </div>
            % endif
            % if warning:
                <div class="alert">
                    <button type="button" class="close" data-dismiss="alert">&times</button>
                    ${warning}
                </div>
            % endif
            % if success:
                <div class="alert alert-success">
                    <button type="button" class="close" data-dismiss="alert">&times</button>
                    ${success}
                </div>
            % endif
            % if info:
                <div class="alert alert-info">
                    <button type="button" class="close" data-dismiss="alert">&times</button>
                    ${info}
                </div>
            % endif

            <%block name="content"/>
        </div>

        ${footer()}

        ## JS placed at the bottom for faster loading
        <script type="text/javascript" src="//ajax.aspnetcdn.com/ajax/jquery/jquery-1.8.2.min.js"></script>
        <script type="text/javascript" src="//ajax.aspnetcdn.com/ajax/jquery.ui/1.9.2/jquery-ui.min.js"></script>
        <script type="text/javascript" src="/static/bootstrap/js/bootstrap.js"></script>
        <script type="text/javascript" src="/static/js/lib/closure-library/closure/goog/base.js"></script>
        <script type="text/javascript" src="/static/js/deps.js"></script>
        <script type="text/javascript" src="/static/js/lib/jquery.backstretch.min.js"></script>
        <%block name="javascript_includes"/>
        <script type="text/javascript">
            $(document).ready(function() {
                ## Background
                $.backstretch('/static/images/winter.jpg');
                ## Highlight the page in navigation
                var navTab = document.getElementById('nav-li-' + '${request.matched_route.name}');
                if (null != navTab) {
                    navTab.setAttribute('class', 'active');
                }
                ## Email
                var email = '(gro.' + 'irzks' + '@nodnzrb)';
                document.getElementById('email-span').innerHTML = email.replace(/z/g, 'a');
                <%block name="inline_javascript"/>
            });
        </script>
    </body>
</html>

<%def name="footer()">
    <footer class="footer">
        <div class="container">
            <p>Built by <a href="http://www.skari.org">Brandon Skari</a>
                <span id="email-span" class="backwards">
                </span>
            </p>
        </div>
    </footer>
</%def>

<%def name="css_url(string)">/static/css/${string}</%def>
<%def name="css_lib_url(string)">/static/css/lib/${string}</%def>
<%def name="js_url(string)">/static/js/src/${string}</%def>
<%def name="js_lib_url(string)">/static/js/lib/${string}</%def>
