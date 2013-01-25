goog.provide('parkStamper.newStampLocation.init');

goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{
 *  parkInputElement: Object,
 *  parks: string,
 *  csrfToken: string
 * }} Initialization parameters.
 *   parkInputElement - jQuery element that the user will type park name into
 *   parks - JSON string of park names
 *   csrfToken - string
 */
parkStamper.newStampLocation.init = function(parameters) {
    'use strict';
    parkStamper.newStampLocation.parkInput = parameters.parkInputElement;
    parkStamper.newStampLocation.csrfToken = parameters.csrfToken;

    // TODO(bskari|2013-01-18) This should be loaded asynchronously to speed
    // initial page loading
    var parks = JSON.parse(parameters.parks);
    parkStamper.newStampLocation.parkInput.autocomplete({
        source: parks,
        delay: 100,
        minLength: 3
    });
};
