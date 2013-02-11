goog.provide('parkStamper.addStampToLocation.init');

goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {
 *  parkInput: string
 *  stampLocationSelect: string,
 *  stampInput: string,
 *  stampSelect: string,
 *  parksJsonUrl: string,
 *  stampLocationsUrl: string,
 *  stampsUrl: string,
 *  csrfToken: string
 */
parkStamper.addStampToLocation.init = function(parameters) {
    'use strict';
    parkStamper.addStampToLocation.stampLocationSelect = $(parameters.stampLocationSelect);
    parkStamper.addStampToLocation.stampSelect = $(parameters.stampSelect);
    parkStamper.addStampToLocation.stampLocationsUrl = parameters.stampLocationsUrl;
    parkStamper.addStampToLocation.stampsUrl = parameters.stampsUrl;
    parkStamper.addStampToLocation.csrfToken = parameters.csrfToken;

    // The template should have this disabled by default, but if a user clicks
    // the back button, their browser will remember its enabled state, so make
    // sure that it's always disabled. Well, unless the park input is already
    // populated; then we just need to populate the stamp locations.
    parkStamper.addStampToLocation.parkInputElement = $(parameters.parkInput);
    if (parkStamper.addStampToLocation.parkInputElement[0].value === '') {
        parkStamper.addStampToLocation.stampLocationSelect.attr('disabled', '');
    } else {
        parkStamper.addStampToLocation.updateStampLocations(
            parkStamper.addStampToLocation.parkInputElement[0].value
        );
    }

    var stampInputElement = $(parameters.stampInput);
    if (stampInputElement[0].value === '') {
        parkStamper.addStampToLocation.stampSelect.attr('disabled', '');
    } else {
        parkStamper.addStampToLocation.updateStamps(
            {term: stampInputElement[0].value}  // Fake jQuery UI imput
        );
    }

    $.getJSON(
        parameters.parksJsonUrl,
        {csrf_token: parkStamper.addStampToLocation.csrfToken},
        parkStamper.addStampToLocation.loadParkJson
    );

    // I'm not using this as an autocomplete field, but rather as a delayed
    // input that triggers population of a select element. It's a hack, but I
    // don't know how to do this myself in a portable way in JS.
    stampInputElement.autocomplete({
        source: parkStamper.addStampToLocation.updateStamps,
        delay: 250,
        minLength: 4
    });

    // We need to call back on both select and change, because the user might
    // not use the autocomplete form
    parkStamper.addStampToLocation.parkInputElement.change(function(eventObject) {
        parkStamper.addStampToLocation.updateStampLocations(eventObject.target.value);
    });
    // We don't do the same thing with #stamp because it's a jQuery UI
    // Autocomplete element and it does its own updating
};


parkStamper.addStampToLocation.loadParkJson = function(data) {
    if (data.success) {
        parkStamper.addStampToLocation.parkInputElement.autocomplete({
            source: data.parkNames,
            delay: 100,
            minLength: 3,
            select: function(_, ui) {
                parkStamper.addStampToLocation.updateStampLocations(ui.item.value);
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
};


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
 * Sends a request for the stamps starting with a given string and updates the
 * stamp dropdown field.
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
            success: parkStamper.addStampToLocation.populateStampSelect,
            error: parkStamper.addStampToLocation.stampErrorCallback
        }
    );
    // The jQuery UI expects callback to be called, even though I'm not using
    // it as an autocomplete
    var undefined;
    if (callback !== undefined) {
        callback('');
    }
};


/**
 * Updates the options in the stamp select dropdown.
 * @param {success: boolean, stamps [{text: string, id: string}]} data Stamp
 *  information.
 */
parkStamper.addStampToLocation.populateStampSelect = function(data) {
    parkStamper.addStampToLocation.stampSelect.attr('disabled', '');

    function makeInput(text, value) {
        'use strict';
        return $('<option value="' + value + '">' + text + '</option>');
    }

    if (data.success === true) {
        // Remove any old data
        parkStamper.addStampToLocation.stampSelect.find('option').remove();

        for (var stampIndex in data.stamps) {
            var stamp = data.stamps[stampIndex];
            parkStamper.addStampToLocation.stampSelect.append(
                makeInput(stamp.text, stamp.id)
            );
        }

        parkStamper.addStampToLocation.stampSelect.removeAttr('disabled');

    } else {
        var undefined;
        var message;
        if (undefined !== data.error) {
            message = data.error;
        } else {
            message = textStatus;
        }
        parkStamper.util.message.popError('Unable to load stamps: ' + message);
    }
};