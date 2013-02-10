goog.provide('parkStamper.collectStamp.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{collectStampUrl: string, buttonSelector: string, csrfToken: string}}
 *  Initialization parameters.
 *   collectStampUrl - URL to send the stamp collection information to
 *   buttonSelector - CSS selector for the buttons to trigger stamp collection
 *    actions on
 *   csrfToken - string
 */
parkStamper.collectStamp.init = function(parameters) {
    'use strict';
    parkStamper.collectStamp.collectStampUrl = parameters.collectStampUrl;
    parkStamper.collectStamp.csrfToken = parameters.csrfToken;

    $(butttonClass).click(parkStamper.collectStamp.sendCollectionRequest);
};


parkStamper.collectStamp.sendCollectionRequest = function() {
    'use strict';
};
