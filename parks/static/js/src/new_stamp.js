goog.provide('parkStamper.newStamp.init');

//goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{parkInputElement: Object, parks: string, csrfToken: string}}
 *  Initialization parameters.
 *   parkInputElement - jQuery element that the user will type park name into
 *   parks - JSON string of park names.
 *   csrfToken - string
 */
parkStamper.newStamp.init = function(parameters) {
    'use strict';
    parkStamper.newStamp.parkInput = parameters.parkInputElement;
    parkStamper.newStamp.csrfToken = parameters.csrfToken;

    // TODO(bskari|2013-01-18) This should be loaded asynchronously to speed
    // initial page loading
    var parks = JSON.parse(parameters.parks);
    parkStamper.newStamp.parkInput.autocomplete({source: parks});

    parkStamper.newStamp.parkInput.change(function(eventObject) {
        alert('Changed');
    });
};
