goog.provide('parkStamper.newStampLocation.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{
 *  parkInputSelector: string,
 *  parksJsonUrlSelector: string,
 *  loadPositionSelector: string,
 *  latitudeSelector: string,
 *  longitudeSelector: string,
 *  csrfTokenSelector: string
 * }} parameters Initialization parameters.
 *   parkInputSelector - jQuery selector for the input that the user
 *    will type park name into
 *   parksJsonUrlSelector - jQuery selector for the input with the value of
 *    the URL from where to load JSON string of park names
 *   loadPositionSelector - jQuery selector for button to load position
 *   latitudeSelector - jQuery selector for latitude input
 *   longitudeSelector - jQuery selector for longitude input
 *   csrfTokenSelector - jQuery selector for the input with the value of the
 *    CSRF token
 */
parkStamper.newStampLocation.init = function(parameters) {
    'use strict';
    parkStamper.newStampLocation.parkInput =
        $(parameters.parkInputSelector);
    parkStamper.newStampLocation.csrfToken =
        $(parameters.csrfTokenSelector)[0].value;
    parkStamper.newStampLocation.latitude = $(parameters.latitudeSelector);
    parkStamper.newStampLocation.longitude = $(parameters.longitudeSelector);

    $(parameters.loadPositionSelector).click(function(eventObject) {
        'use strict';
        eventObject.preventDefault();
        parkStamper.util.geolocation.requestLocation(
            parkStamper.newStampLocation.fillLatitudeLongitude,
            function(error) {
                parkStamper.util.message.popError('Unable to determine your position, sorry!');
                if (console && console.log) {
                    console.log('Geolocation failed: ' + error);
                }
            }
        );
    });

    var parksJsonUrl = $(parameters.parksJsonUrlSelector)[0].value;
    $.getJSON(
        parksJsonUrl,
        {csrfToken: parkStamper.newStampLocation.csrfToken},
        parkStamper.newStampLocation.loadParkJson
    );
};


/**
 * Callback function for loading park names JSON.
 * @param {{success: boolean, parkNames: Array.<string>}} data List of park
 *  names.
 */
parkStamper.newStampLocation.loadParkJson = function(data) {
    'use strict';
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


/**
 * Callback function to load the latitude and longitude fields.
 * @param {{coords: {latitude: number, longitude: number}}} position
 */
parkStamper.newStampLocation.fillLatitudeLongitude = function(position) {
    'use strict';
    parkStamper.newStampLocation.latitude.val(position.coords.latitude);
    parkStamper.newStampLocation.longitude.val(position.coords.longitude);
};
