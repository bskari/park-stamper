goog.provide('parkStamper.newStampLocation.init');

goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{
 *  parkInputElement: Object,
 *  parksJsonUrl: string,
 *  csrfToken: string
 * }} Initialization parameters.
 *   parkInputElement - jQuery element that the user will type park name into
 *   parksJsonUrl - URL from where to load JSON string of park names
 *   csrfToken - string
 */
parkStamper.newStampLocation.init = function(parameters) {
    'use strict';
    parkStamper.newStampLocation.parkInput = parameters.parkInputElement;
    parkStamper.newStampLocation.csrfToken = parameters.csrfToken;

    $.getJSON(
        parameters.parksJsonUrl,
        {csrfToken: parkStamper.newStampLocation.csrfToken},
        parkStamper.newStampLocation.loadParkJson
    );
};


parkStamper.newStampLocation.loadParkJson = function(data) {
    if (data.success) {
        parkStamper.newStampLocation.parkInput.autocomplete({
            source: data.parkNames,
            delay: 100,
            minLength: 3
        });
    } else {
        parkStamper.util.message.popError('Unable to load park name suggestions');
    }
};
