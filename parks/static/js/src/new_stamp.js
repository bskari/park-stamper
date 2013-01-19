goog.provide('parkStamper.newStamp.init');

goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{
 *  parkInput: Object,
 *  stampLocationSelect: Object,
 *  parks: string,
 *  stampLocationsUrl: string,
 *  csrfToken: string
 * }} Initialization parameters.
 *   parkInputElement - jQuery element that the user will type park name into
 *   parks - JSON string of park names
 *   stampLocationsUrl - URL to load the stamp locations from
 *   csrfToken - string
 */
parkStamper.newStamp.init = function(parameters) {
    'use strict';
    parkStamper.newStamp.parkInput = parameters.parkInputElement;
    parkStamper.newStamp.stampLocationSelect = parameters.stampLocationSelect;
    parkStamper.newStamp.stampLocationsUrl = parameters.stampLocationsUrl;
    parkStamper.newStamp.csrfToken = parameters.csrfToken;

    // TODO(bskari|2013-01-18) This should be loaded asynchronously to speed
    // initial page loading
    var parks = JSON.parse(parameters.parks);
    parkStamper.newStamp.parkInput.autocomplete({
        source: parks,
        delay: 100
    });

    parkStamper.newStamp.parkInput.change(function(eventObject) {
        var data = {
            park: eventObject.target.value,
            csrf_token: parkStamper.newStamp.csrfToken
        }
        $.ajax(
            parkStamper.newStamp.stampLocationsUrl,
            {
                data: data,
                datatype: 'json',
                success: parkStamper.newStamp.populateStampLocations,
                error: parkStamper.newStamp.stampLocationErrorCallback
            }
        );
    });
};


/**
 * Success callback for Ajax request for nearby stamp information.
 * @param {
 *  success: boolean,
 *  stampLocations: {
 *   location: string,
 *   id: number
 *  }
 * } data Stamp location information.
 * @param {string} textStatus Status of the Ajax request.
 */
parkStamper.newStamp.populateStampLocations = function(data, textStatus) {
    'use strict';

    function makeInput(text, value) {
        'use strict';
        return $('<option value="' + value + '">' + text + '</option>');
    }

    parkStamper.newStamp.stampLocationSelect.attr('disabled', '');

    if (data.success === true) {
        // Remove any old data
        parkStamper.newStamp.stampLocationSelect.find('option').remove();

        for (var stampLocationIndex in data.stampLocations) {
            var stampLocation = data.stampLocations[stampLocationIndex];
            parkStamper.newStamp.stampLocationSelect.append(
                makeInput(stampLocation.location, stampLocation.id)
            );
        }

        parkStamper.newStamp.stampLocationSelect.removeAttr('disabled');
    } else {
        parkStamper.util.message.popError(
            'Unable to load stamp locations: ' + textStatus
        );
    }
};


/**
 * Error callback for Ajax request for stamp location information.
 * @param {Object} jqXHR
 * @param {string} textStatus Status of the Ajax request.
 * @param {string} errorThrown Description of the request error.
 */
parkStamper.newStamp.stampLocationErrorCallback = function(
    jqXHR,
    textStatus,
    errorThrown
) {
    'use strict';
    console.log('XHR failed: ' + textStatus + ' ' + errorThrown);
    parkStamper.util.message.popError(
        'Unable to load stamp locations: ' + textStatus + ' ' + errorThrown
    );
};
