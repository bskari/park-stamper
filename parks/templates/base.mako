<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:tal="http://xml.zope.org/namespaces/tal">
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.css" />
        <style type="text/css">
            body {
                padding-top: 60px;
                padding-bottom: 40px;
            }
        </style>
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
                    <a class="brand" href="#">Park Stamper</a>
                    <div class="nav-collapse collapse">
                        <ul class="nav">
                            <li><a href="/">Home</a></li>
                            ##<li class="dropdown">
                            ##    <a href="#" class="dropdown-toggle" data-toggle="dropdown">Dropdown <b class="caret"></b></a>
                            ##    <ul class="dropdown-menu">
                            ##        <li><a href="#">Action</a></li>
                            ##        <li class="divider"></li>
                            ##        <li class="nav-header">Nav header</li>
                            ##        <li><a href="#">Separated</a></li>
                            ##    </ul>
                            ##</li>
                        </ul>
                        <ul class="nav actions">
                            <li><a data-target="#login-modal" data-link="modal" href="/login">Log In</a>
                            <li><a data-target="#signup-modal" data-link="modal" href="/login">Sign Up</a>
                        </ul>
                        ##<form class="navbar-form pull-right">
                        ##    <input class="span3" type="text" placeholder="Email">
                        ##    <input class="span3" type="password" placeholder="Password">
                        ##    <button type="submit" class="btn">Sign in</button>
                        ##</form>
                    </div><!--/.nav-collapse -->
                </div>
            </div>
        </div>

        <div class="container">
            <%block name="content" />
        </div>

        ## JS placed at the bottom for faster loading
        <script src="//ajax.aspnetcdn.com/ajax/jquery/jquery-1.8.2.min.js" type="text/javascript"></script>
        <script src="/static/bootstrap/js/bootstrap.js"></script>
    </body>
</html>
