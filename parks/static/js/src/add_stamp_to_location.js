goog.provide('parkStamper.addStampToLocation.init');

goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {
 *  parkInputElement: Object,
 *  stampInputElement: Object,
 *  stampLocationSelect: Object,
 *  parks: string,
 *  stampLocationsUrl: string,
 *  stampsUrl: string,
 *  csrfToken: string
 */
parkStamper.addStampToLocation.init = function(parameters) {
    'use strict';
    parkStamper.addStampToLocation.stampLocationSelect = parameters.stampLocationSelect;
    parkStamper.addStampToLocation.stampLocationsUrl = parameters.stampLocationsUrl;
    parkStamper.addStampToLocation.stampsUrl = parameters.stampsUrl;
    parkStamper.addStampToLocation.csrfToken = parameters.csrfToken;

    // The template should have this disabled by default, but if a user clicks
    // the back button, their browser will remember its enabled state, so make
    // sure that it's always disabled. Well, unless the park input is already
    // populated; then we just need to populate the stamp locations.
    if (parameters.parkInputElement[0].value === '') {
        parkStamper.addStampToLocation.stampLocationSelect.attr('disabled', '');
    } else {
        parkStamper.addStampToLocation.updateStampLocations(
            parameters.parkInputElement[0].value
        );
    }

    // TODO(bskari|2013-02-03) This should be loaded asynchronously to speed
    // initial page loading
    var parks = JSON.parse(parameters.parks);
    parameters.parkInputElement.autocomplete({
        source: parks,
        delay: 100,
        minLength: 3,
        select: function(_, ui) {
            parkStamper.addStampToLocation.updateStampLocations(ui.item.value);
        }
    });

    parameters.stampInputElement.autocomplete({
        source: parkStamper.addStampToLocation.updateStamps,
        delay: 250,
        minLength: 4
    });

    // We need to call back on both select and change, because the user might
    // not use the autocomplete form
    parameters.parkInputElement.change(function(eventObject) {
        parkStamper.addStampToLocation.updateStampLocations(eventObject.target.value);
    });
    // We don't do the same thing with #stamp because it's a jQuery UI
    // Autocomplete element and it does its own updating
};


/**
 * Sends a request for the stamp locations at a given park.
 * @param {string} parkName Canonical name of the park.
 */
parkStamper.addStampToLocation.updateStampLocations = function(parkName) {
    'use strict';
    // There are multiple callbacks that might call this with the same value;
    // if we've already updated a park name, just ignore it
    if (parkStamper.addStampToLocation.updateStampLocations.lastUpdateName === parkName) {
        return;
    }
    parkStamper.addStampToLocation.updateStampLocations.lastUpdateName = parkName;

    var data = {
        park: parkName,
        csrf_token: parkStamper.addStampToLocation.csrfToken
    };
    $.ajax(
        parkStamper.addStampToLocation.stampLocationsUrl,
        {
            data: data,
            datatype: 'json',
            success: parkStamper.addStampToLocation.populateStampLocations,
            error: parkStamper.addStampToLocation.stampLocationErrorCallback
        }
    );
}


/**
 * Loads a request for the stamp locations at a given park.
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
parkStamper.addStampToLocation.populateStampLocations = function(data, textStatus) {
    'use strict';

    function makeInput(text, value) {
        'use strict';
        return $('<option value="' + value + '">' + text + '</option>');
    }

    parkStamper.addStampToLocation.stampLocationSelect.attr('disabled', '');

    if (data.success === true) {
        // Remove any old data
        parkStamper.addStampToLocation.stampLocationSelect.find('option').remove();

        for (var stampLocationIndex in data.stampLocations) {
            var stampLocation = data.stampLocations[stampLocationIndex];
            parkStamper.addStampToLocation.stampLocationSelect.append(
                makeInput(stampLocation.location, stampLocation.id)
            );
        }

        parkStamper.addStampToLocation.stampLocationSelect.removeAttr('disabled');
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
parkStamper.addStampToLocation.stampLocationErrorCallback = function(
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


/**
 * Error callback for Ajax request for stamp location information.
 * @param {Object} jqXHR
 * @param {string} textStatus Status of the Ajax request.
 * @param {string} errorThrown Description of the request error.
 */
parkStamper.addStampToLocation.stampErrorCallback = function(
    jqXHR,
    textStatus,
    errorThrown
) {
    'use strict';
    console.log('XHR failed: ' + textStatus + ' ' + errorThrown);
    parkStamper.util.message.popError(
        'Unable to load stamps: ' + textStatus + ' ' + errorThrown
    );
};


/**
 * Sends a request for the stamps starting with a given string.
 * @param {request: {term: string}} Start of the stamp's text.
 */
parkStamper.addStampToLocation.updateStamps = function(request, callback) {
    'use strict';
    var stampText = request.term;
    // There are multiple callbacks that might call this with the same value;
    // if we've already updated a park name, just ignore it
    if (parkStamper.addStampToLocation.updateStamps.lastUpdateName === stampText) {
        return;
    }
    parkStamper.addStampToLocation.updateStamps.lastUpdateName = stampText;

    var data = {
        stamp_text: request.term,
        csrf_token: parkStamper.addStampToLocation.csrfToken
    };
    $.ajax(
        parkStamper.addStampToLocation.stampsUrl,
        {
            data: data,
            datatype: 'json',
            success: function(data, textStatus) {
                if (data.success === true) {
                    callback(data.stamps);
                } else {
                    var undefined;
                    parkStamper.addStampToLocation.stampErrorCallback(
                        undefined, // jqXhr
                        textStatus,
                        data.error // Might be undefined; that's fine
                    );
                    // The jQuery UI component expects callback to be called,
                    // even on failure
                    callback('[]');
                }
            },
            error: parkStamper.addStampToLocation.stampErrorCallback
        }
    );
}
