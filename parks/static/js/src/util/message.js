goog.provide('parkStamper.util.message.popError');
goog.provide('parkStamper.util.message.popWarning');


parkStamper.util.message.popError = function(errorMessage, container) {
    "use strict;";
    var undefined;
    if (container === undefined) {
        container = $('#content');
    }

    var messageDiv = $('<div>' + errorMessage + '</div>');
    /* I can't get this to work when combined with the above jQuery call */
    messageDiv.addClass('alert');
    messageDiv.addClass('alert-error');

    var button = $('<button>&times;</button>', {'class': 'close', 'data-dismiss': 'alert'});
    button.addClass('close');
    button.attr('data-dismiss', 'alert');
    messageDiv.append(button);

    container.prepend(messageDiv);
};

parkStamper.util.message.popWarning = function(warningMessage, container) {
    "use strict;";
    var undefined;
    if (container === undefined) {
        container = $('#content');
    }

    var messageDiv = $('<div>' + errorMessage + '</div>');
    /* I can't get this to work when combined with the above jQuery call */
    messageDiv.addClass('alert');

    var button = $('<button>&times;</button>');
    button.addClass('close');
    button.attr('data-dismiss', 'alert');
    messageDiv.append(button);

    container.prepend(messageDiv);

    messageDiv.addClass('alert');
};
