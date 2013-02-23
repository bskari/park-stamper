goog.provide('parkStamper.collectStamp.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{collectStampUrl: string, rowSelector: string,
 *  dateModalDialogSelector: string, loadingSelector: string,
 *  parkIdSelector: string, csrfToken: string}} Initialization parameters.
 *   collectStampUrl - URL to send the stamp collection information to
 *   rowSelector- CSS selector for the stamp rows that have collection and
 *    edit buttons
 *   dateModalDialogSelector - CSS selector for the date modal dialog
 *   loadingSelector - CSS selector for the date modal dialog
 *   parkIdSelector - CSS selector for hidden input with the park's ID
 *   csrfToken - string
 */
parkStamper.collectStamp.init = function(parameters) {
    'use strict';
    parkStamper.collectStamp.collectStampUrl = parameters.collectStampUrl;
    parkStamper.collectStamp.dateModalDialog = $(
        parameters.dateModalDialogSelector
    );
    parkStamper.collectStamp.loadingSelector = parameters.loadingSelector;
    var parkIdInputs = $(parameters.parkIdSelector);
    if (parkIdInputs.length !== 0) {
        parkStamper.collectStamp.parkId = parkIdInputs[0].value;
    }
    parkStamper.collectStamp.csrfToken = parameters.csrfToken;

    $(parameters.rowSelector).each(parkStamper.collectStamp.setUpButtons);

    parkStamper.collectStamp.dateModalDialog.dialog({
        height: 100,
        autoOpen: false
    });
    var datePicker = parkStamper.collectStamp.dateModalDialog.find(
        'input[type=text]'
    );
    datePicker.datepicker({
        onSelect: parkStamper.collectStamp.sendCollectStampRequest,
        dateFormat: 'yy-mm-dd',
        maxDate: 0 // 0 => today
    });
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


/**
 * Show the date picker dialog modal.
 */
parkStamper.collectStamp.showDatePicker = function(eventObject) {
    'use strict';
    eventObject.preventDefault();

    // Don't let the user get too click happy
    if (parkStamper.collectStamp.sendingRequest) {
        return;
    }

    parkStamper.collectStamp.dateModalDialog.dialog('open');

    // Save the stamp ID so that we can send it once the user selects a date
    var cell = $(eventObject.currentTarget).parent();
    parkStamper.collectStamp.stampId = cell.find('input[type=hidden]')[0].value;

    // Save the button so we can disable it on success
    parkStamper.collectStamp.clickedButton = $(eventObject.currentTarget);
};


/**
 * Sends the stamp collection request to the server.
 */
parkStamper.collectStamp.sendCollectStampRequest = function(dateText) {
    'use strict';

    var undefined;
    // This might happen if the inheriting template doesn't call the template
    // function to create the table (and the hidden input with the park ID),
    // but the client still manages to somehow send a stamp collection request
    if (parkStamper.collectStamp.parkId === undefined) {
        parkStamper.util.message.popError(
            'There was an error on my end processing your request; sorry'
            + ' about that.'
        );
        return;
    }

    parkStamper.collectStamp.sendingRequest = true;

    parkStamper.collectStamp.dateModalDialog.dialog('close');
    parkStamper.collectStamp.clickedButton.hide();
    var throbber = parkStamper.collectStamp.clickedButton.parent().find(
        parkStamper.collectStamp.loadingSelector
    );
    throbber.css('display', 'inline-block');

    var data = {
        stampId: parkStamper.collectStamp.stampId,
        parkId: parkStamper.collectStamp.parkId,
        date: dateText,
        csrfToken: parkStamper.collectStamp.csrfToken
    };

    $.ajax({
        type: 'POST',
        url: parkStamper.collectStamp.collectStampUrl,
        data: data,
        success: parkStamper.collectStamp.sendCollectStampRequestSuccess,
        error: function(_1, _2, errorThrown) {
            if (errorThrown == 'Unauthorized') {
                parkStamper.util.message.popError(
                    'Sorry, you need to logged in collect stamps.'
                );
            } else {
                parkStamper.util.message.popError(
                    'There was an error receiving your request. Please try again later.'
                );
                console.log(_1 + ':' + _2 + ':' + errorThrown);
            }
        },
        dataType: 'json'
    }).always(function() {
            parkStamper.collectStamp.clickedButton.show();
            throbber.hide();
            parkStamper.collectStamp.sendingRequest = false;
        }
    );
};


/**
 * Called when the stamp collection POST request succeeds.
 */
parkStamper.collectStamp.sendCollectStampRequestSuccess = function(
    data,
    textStatus,
    jqXHR
) {
    if (data.success === false) {
        parkStamper.util.message.popError(data.error);
    } else {
        parkStamper.collectStamp.clickedButton.removeClass('btn-primary');
        parkStamper.collectStamp.clickedButton.addClass('btn-disabled');
        parkStamper.collectStamp.clickedButton.off('click');
        parkStamper.collectStamp.clickedButton.attr('title', 'Stamp marked as collected!');
    }
};
