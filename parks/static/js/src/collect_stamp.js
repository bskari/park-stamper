goog.provide('parkStamper.collectStamp.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{collectStampUrl: string, buttonSelector: string, csrfToken: string}}
 *  Initialization parameters.
 *   collectStampUrl - URL to send the stamp collection information to
 *   rowSelector- CSS selector for the stamp rows that have collection and
 *    edit buttons
 *   csrfToken - string
 */
parkStamper.collectStamp.init = function(parameters) {
    'use strict';
    parkStamper.collectStamp.collectStampUrl = parameters.collectStampUrl;
    parkStamper.collectStamp.csrfToken = parameters.csrfToken;

    $(parameters.rowSelector).each(parkStamper.collectStamp.setUpButtons);
};


parkStamper.collectStamp.setUpButtons = function(_, td) {
    'use strict';
    var jQueryTd = $(td);
    jQueryTd.find(
        'a.btn.collect-stamp'
    ).click(
        parkStamper.collectStamp.sendCollectStampRequest
    );
};


parkStamper.collectStamp.sendCollectStampRequest = function(eventObject) {
    'use strict';
    var cell = $(eventObject.currentTarget).parent();
    var stampId = cell.find('input[type=hidden]')[0].value;
    var data = {stampId: stampId};
    // TODO make the endpoint of this POST
    alert('POSTing ' + JSON.stringify(data) + ' to ' + parkStamper.collectStamp.collectStampUrl);
    return;
    $.post(
        parkStamper.collectStamp.collectStampUrl,
        data,
        parkStamper.collectStamp.sendCollectStampRequestSuccess
    );
};

parkStamper.collectStamp.sendCollectStampRequestSuccess = function(
    data,
    textStatus,
    jqXHR
) {
    alert('Success');
};
