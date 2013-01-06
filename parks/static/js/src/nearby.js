goog.provide('parkStamper.nearby.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


/**
 * Initialization function.
 * @param {{tableBody: Object, loadingElement: Object, nearbyUrl: string,
 *  csrfToken: string}} Initialization parameters.
 *   tableBody - jQuery tbody to add the stamp rows to
 *   loadingElement - jQuery element to hide after data are loaded
 *   nearbyUrl - string URL to load the stamp data from
 *   csrfToken - string
 */
parkStamper.nearby.init = function(parameters) {
    'use strict';
    parkStamper.nearby.tableBody = parameters.tableBody;
    parkStamper.nearby.loadingElement = parameters.loadingElement;
    parkStamper.nearby.nearbyUrl = parameters.nearbyUrl;
    parkStamper.nearby.csrfToken = parameters.csrfToken;
    parkStamper.nearby.distance = parameters.distance;

    parkStamper.util.geolocation.requestLocation(
        parkStamper.nearby.geoLocationCallback,
        function(error) {
            parkStamper.util.message.popError('Unable to determine your position, sorry!');
            if (console && console.log) {
                console.log('Geolocation failed: ' + error);
            }
            parkStamper.nearby.loadingElement.hide();
        }
    );

    // Disable the distance selector while we're waiting on stamp data
    parkStamper.nearby.distance.attr('disabled', '');
    parkStamper.nearby.distance.change(parkStamper.nearby.loadNearbyStampInformation);
};


/**
 * Callback function to send position information back from.
 * @param {{coords: {latitude: number, longitude: number}}} position
 */
parkStamper.nearby.geoLocationCallback = function(position) {
    'use strict';
    parkStamper.nearby.latitude = position.coords.latitude;
    parkStamper.nearby.longitude = position.coords.longitude;

    parkStamper.nearby.loadNearbyStampInformation();
};


/**
 * Ajaxy load stamp information.
 */
parkStamper.nearby.loadNearbyStampInformation = function() {
    'use strict';
    parkStamper.nearby.distance.attr('disabled', '');
    parkStamper.nearby.loadingElement.show();
    // Clear out the old data
    parkStamper.nearby.tableBody.find('tr').remove();
    // Hide it so that we can animate it appearing
    parkStamper.nearby.tableBody.hide();

    var data = {
        'latitude': parkStamper.nearby.latitude,
        'longitude': parkStamper.nearby.longitude,
        'distance': parkStamper.nearby.distance.val(),
        'csrf_token': parkStamper.nearby.csrfToken
    };
    $.ajax(
        parkStamper.nearby.nearbyUrl,
        {
            'data': data,
            'datatype': 'json',
            'success': parkStamper.nearby.createStampRows,
            'error': parkStamper.nearby.nearbyErrorCallback
        }
    );
};


/**
 * Success callback for Ajax request for nearby stamp information.
 * @param {{
 *  park: string,
 *  url: string,
 *  text: string,
 *  location: string,
 *  coordinates: {latitude: number, longitude: number},
 *  distance: number,
 *  last_seen: string,
 *  direction: string
 * }} data Stamp information.
 * @param {string} textStatus Status of the Ajax request.
 */
parkStamper.nearby.createStampRows = function(data, textStatus) {
    'use strict';
    function makeCell(message) {
        'use strict';
        return $('<td>' + message + '</td>');
    }
    /**
     * Rounds a number to a certain number of digits.
     * @param {number} number The number to round.
     * @param {number} digits The number of digits to round to (defaults to 1).
     */
    function round(number, digits) {
        'use strict';
        var undefined;
        if (digits === undefined) {
            digits = 1;
        }
        var power = Math.pow(10, digits);
        return Math.round(number * power) / power;
    }

    if (data.success === true) {
        if (data.stamps.length === 0) {
            var errorMessage = "Looks like there aren't any stamps within " +
                parkStamper.nearby.distance.val() +
                ' miles of you.';
            if (parkStamper.nearby.distance.val() < 100) {
                errorMessage += ' Try increasing the search distance.';
            } else {
                errorMessage += ' Want to see a list of <a href="/all-parks">all parks</a> instead?';
            }
            parkStamper.util.message.popError(errorMessage);
        }
        for (var stampIndex in data.stamps) {
            var stamp = data.stamps[stampIndex];
            var row = $('<tr></tr>');

            var stampText = stamp.text.replace('\n', '<br />');

            // Park, Text, Location, GPS, Distance, Last Seen
            row.append(makeCell('<a href=' + stamp.url + '>' + stamp.park));
            row.append(makeCell(stampText));
            row.append(makeCell(stamp.location));
            row.append(makeCell(stamp.coordinates.latitude + ' ' + stamp.coordinates.longitude));
            row.append(makeCell(round(stamp.distance, 3) + ' miles ' + stamp.direction));
            row.append(makeCell(stamp.last_seen));
            parkStamper.nearby.tableBody.append(row);
        }
        parkStamper.nearby.loadingElement.hide();
        parkStamper.nearby.tableBody.show(1000);

        // Reenable the distance selector
        parkStamper.nearby.distance.removeAttr('disabled');
    } else {
        parkStamper.util.message.popError('Unable to load nearby stamps: ' + textStatus);
        parkStamper.nearby.loadingElement.hide();
    }
};


/**
 * Error callback for Ajax request for nearby stamp information.
 * @param {Object} jqXHR
 * @param {string} textStatus Status of the Ajax request.
 * @param {string} errorThrown Description of the request error.
 */
parkStamper.nearby.nearbyErrorCallback = function(jqXHR, textStatus, errorThrown) {
    'use strict';
    console.log('XHR failed: ' + textStatus + ' ' + errorThrown);
    parkStamper.util.message.popError('Unable to load nearby stamps: ' + textStatus + ' ' + errorThrown);
    parkStamper.nearby.loadingElement.hide();
};
