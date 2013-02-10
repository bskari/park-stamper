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
 *   parksJsonUrl - URL from where to load JSON string of park names
 *   stampLocationsUrl - URL to load the stamp locations from
 *   csrfToken - string
 */
parkStamper.newStamp.init = function(parameters) {
    'use strict';
    parkStamper.newStamp.parkInput = parameters.parkInputElement;
    parkStamper.newStamp.stampLocationSelect = parameters.stampLocationSelect;
    parkStamper.newStamp.stampLocationsUrl = parameters.stampLocationsUrl;
    parkStamper.newStamp.csrfToken = parameters.csrfToken;

    // The template should have this disabled by default, but if a user clicks
    // the back button, their browser will remember its enabled state, so make
    // sure that it's always disabled. Well, unless the park input is already
    // populated; then we just need to populate the stamp locations.
    if (parkStamper.newStamp.parkInput[0].value === '') {
        parkStamper.newStamp.stampLocationSelect.attr('disabled', '');
    } else {
        parkStamper.newStamp.updateStampLocations(
            parkStamper.newStamp.parkInput[0].value
        );
    }

    $.getJSON(
        parameters.parksJsonUrl,
        {csrf_token: parkStamper.newStamp.csrfToken},
        parkStamper.newStamp.loadParkJson
    );

    // We need to call back on both select and change, because the user might
    // not use the autocomplete form
    parkStamper.newStamp.parkInput.change(function(eventObject) {
        parkStamper.newStamp.updateStampLocations(eventObject.target.value);
    });
};


parkStamper.newStamp.loadParkJson = function(data) {
    if (data.success) {
       parkStamper.newStamp.parkInput.autocomplete({
            source: data.parkNames,
            delay: 100,
            minLength: 3,
            select: function(_, ui) {
                parkStamper.newStamp.updateStampLocations(ui.item.value);
            }
        });
    } else {
        parkStamper.util.message.popError('Unable to load park name suggestions');
    }
};


/**
 * Sends a request for the stamp locations at a given park.
 * @param {string} parkName Canonical name of the park.
 */
parkStamper.newStamp.updateStampLocations = function(parkName) {
    // There are multiple callbacks that might call this with the same value;
    // if we've already updated a park name, just ignore it
    if (parkStamper.newStamp.updateStampLocations.lastUpdateName === parkName) {
        return;
    }
    parkStamper.newStamp.updateStampLocations.lastUpdateName = parkName;

    var data = {
        park: parkName,
        csrf_token: parkStamper.newStamp.csrfToken
    };
    $.ajax(
        parkStamper.newStamp.stampLocationsUrl,
        {
            data: data,
            datatype: 'json',
            success: parkStamper.newStamp.populateStampLocations,
            error: parkStamper.newStamp.stampLocationErrorCallback
        }
    );
}


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
        var undefined;
        var message;
        if (undefined !== data.error) {
            message = data.error;
        } else {
            message = textStatus;
        }
        parkStamper.util.message.popError(
            'Unable to load stamp locations: ' + message
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
