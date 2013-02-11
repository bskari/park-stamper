goog.provide('parkStamper.collectStamp.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{collectStampUrl: string, buttonSelector: string, csrfToken: string,
 *  dateModalDialogSelector: string}} Initialization parameters.
 *   collectStampUrl - URL to send the stamp collection information to
 *   rowSelector- CSS selector for the stamp rows that have collection and
 *    edit buttons
 *   dateModalSelector - CSS selector for the date modal dialog
 *   csrfToken - string
 */
parkStamper.collectStamp.init = function(parameters) {
    'use strict';
    parkStamper.collectStamp.collectStampUrl = parameters.collectStampUrl;
    parkStamper.collectStamp.dateModalDialog = $(
        parameters.dateModalDialogSelector
    );
    parkStamper.collectStamp.csrfToken = parameters.csrfToken;

    $(parameters.rowSelector).each(parkStamper.collectStamp.setUpButtons);

    parkStamper.collectStamp.dateModalDialog.dialog({
        height: 100,
        modal: true,
        autoOpen: false
    });
    parkStamper.collectStamp.dateModalDialog.find(
        'input[type=text]'
    ).datepicker();
};


/**
 * Sets up the buttons in each stamp row.
 * @param {_: number} index.
 * @param {td: element} row element.
 */
parkStamper.collectStamp.setUpButtons = function(_, td) {
    'use strict';
    var jQueryTd = $(td);
    jQueryTd.find(
        'a.btn.collect-stamp'
    ).click(
        parkStamper.collectStamp.showDatePicker
    );
};


parkStamper.collectStamp.showDatePicker = function(eventObject) {
    'use strict';
    parkStamper.collectStamp.dateModalDialog.dialog('open');
    parkStamper.collectStamp.dateModalDialog.find('input[type=text]').datepicker();
};

foo = function() {
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
