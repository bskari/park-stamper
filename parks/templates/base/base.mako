<%! script_files = [] %>
<%! inline_script = '' %>
<%! stylesheet_files = [] %>
<%namespace module="parks.templates.base.functions" name="functions"/>
<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8">
        <!--[if lt IE 9]>
            <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
        <![endif]-->
        <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
        <link rel="stylesheet" href="${functions.css_url('custom.css')}">
        <link rel="stylesheet" href="//ajax.aspnetcdn.com/ajax/jquery.ui/1.10.0/themes/redmond/jquery-ui.css">
##        <link href="http://fonts.googleapis.com/css?family=Merriweather:bold" rel="stylesheet" type="text/css">
##        <link href="http://fonts.googleapis.com/css?family=Open%20Sans" rel="stylesheet" type="text/css">
        ${insert_stylesheet_files()}
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
                    <a class="brand" href="${request.route_url('home')}">Park Stamper</a>
                    <div class="nav-collapse">
                        <ul class="nav">
                            <li id="nav-li-all-parks">
                                <a href="${request.route_url('all-parks')}">All parks</a>
                            </li>
                            <li id="nav-li-nearby">
                                <a href="${request.route_url('nearby')}">Nearby</a>
                            </li>
                            <li class="dropdown" id="nav-li-new-menu">
                                <a id="new-menu" href="#nav-li-new-menu" role="button" class="dropdown-toggle" data-toggle="dropdown">New<b class="caret"></b></a>
                                <ul class="dropdown-menu" role="menu" aria-labelledby="new-menu">
                                    <li>
                                        <a href="${request.route_url('new-stamp')}">Stamp</a>
                                    </li>
                                    <li>
                                        <a href="${request.route_url('new-stamp-location')}">Location</a>
                                    </li>
                                    <li>
                                        <a href="${request.route_url('add-stamp-to-location')}">Add stamp to location</a>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                        <ul class="nav actions">
                            % if user_id:
                                <li>
                                    <a href="${request.route_url('log-out')}">Log out</a>
                                </li>
                            % else:
                                <li>
                                    <a href="${request.route_url('log-in')}">Log in</a>
                                </li>
                                <li>
                                    <a href="${request.route_url('sign-up')}">Sign up</a>
                                </li>
                            % endif
                        </ul>
                    ## close nav-collapse div
                    </div>
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

            ${functions.hidden_value(id='csrf-token', value=csrf_token)}

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
        ${self.insert_script_files()}
        <script type="text/javascript">
            $(document).ready(function() {
                ## Background
                // Loading this seemed slow on mobile 3G, so skip it. Or maybe
                // my phone's browser is just slow. Whatever.
                if (!/Android|webOS|iPhone|BlackBerry/i.test(navigator.userAgent)) {
                    $.backstretch('/static/images/winter.jpg');
                }
                ## Highlight the page in navigation
                var navTab = document.getElementById('nav-li-' + '${request.matched_route.name}');
                if (null != navTab) {
                    navTab.setAttribute('class', 'active');
                }
                ## Email
                var email = '(gro.' + 'irzks' + '@nodnzrb)';
                document.getElementById('email-span').innerHTML = email.replace(/z/g, 'a');
                ${self.insert_inline_script()}
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


<%def name="insert_inline_script()">
## Iterate over the namespaces that aren't in the inheritance hierarchy
% for ns in context.namespaces.values():
    % if hasattr(ns, 'inline_script'):
        ${ns.inline_script()}
    % endif
% endfor
## Iterate over files in the inheritance hierarchy
<%
    all_inline_script = ''
    t = self
    ## Traverse the inheritance tree to get all the inline script definitions
    while t:
        all_inline_script += getattr(t.module, 'inline_script', '') + '\n'
        t = t.inherits
%>
${all_inline_script | n}
</%def>


<%def name="insert_script_files()">
## Iterate over the namespaces that aren't in the inheritance hierarchy
% for ns in context.namespaces.values():
    % if hasattr(ns, 'script_files'):
        ${ns.script_files()}
    % endif
% endfor
## Iterate over files in the inheritance hierarchy
<%
    all_script_files = []
    t = self
    ## Traverse the inheritance tree to get all the inline script definitions
    while t:
        all_script_files += getattr(t.module, 'script_files', [])
        t = t.inherits
%>
% for script_file in all_script_files:
    <script src="${script_file}" type="text/javascript"></script>
% endfor
</%def>


<%def name="insert_stylesheet_files()">
## Iterate over the namespaces that aren't in the inheritance hierarchy
% for ns in context.namespaces.values():
    % if hasattr(ns, 'stylesheet_files'):
        ${ns.stylesheet_files()}
    % endif
% endfor
## Iterate over files in the inheritance hierarchy
<%
    all_stylesheet_files = []
    t = self
    ## Traverse the inheritance tree to get all the inline script definitions
    while t:
        all_stylesheet_files += getattr(t.module, 'stylesheet_files', [])
        t = t.inherits
%>
% for stylesheet_file in all_stylesheet_files:
    <link rel="stylesheet" href="${stylesheet_file}">
% endfor
</%def>
