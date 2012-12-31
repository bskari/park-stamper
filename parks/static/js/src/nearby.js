goog.provide('parkStamper.nearby.init');

goog.require('parkStamper.util.geolocation.requestLocation');
goog.require('parkStamper.util.message.popError');


parkStamper.nearby.init = function(parameters) {
    'use strict;';
    parkStamper.nearby.table = parameters.table;
    parkStamper.nearby.loadingElement = parameters.loadingElement;
    parkStamper.nearby.nearbyUrl = parameters.nearbyUrl;
    parkStamper.nearby.csrfToken = parameters.csrfToken;

    parkStamper.util.geolocation.requestLocation(parkStamper.nearby.geoLocationCallback);
};

parkStamper.nearby.geoLocationCallback = function(position) {
    'use strict;';
    var data = {
        'latitude': position.coords.latitude,
        'longitude': position.coords.longitude,
        'csrf_token': parkStamper.nearby.csrfToken
    };
    console.log('XHR to ' + parkStamper.nearby.nearbyUrl);
    $.ajax(
        parkStamper.nearby.nearbyUrl,
        {
            'data': data,
            'datatype': 'json',
            'success': parkStamper.nearby.nearbySuccessCallback,
            'error': parkStamper.nearby.nearbyErrorCallback
        }
    );
};

parkStamper.nearby.nearbySuccessCallback = function(data, textStatus, jqXHR) {
    'use strict;';
    parkStamper.nearby.loadingElement.hide();

    if (data.success === true) {

        function makeCell(message) {
            if (message === 'null') {
                message = '';
            }
            return $('<td>' + message + '</td>');
        }

        for (var stampIndex in data.stamps) {
            var stamp = data.stamps[stampIndex];
            var row = $('<tr></tr>');

            var stampText = stamp['text'].replace('\n', '<br />');

            // Park, Text, Location, GPS, Distance, Last Seen
            row.append(makeCell('<a href=' + stamp['url'] + '>' + stamp['park']));
            row.append(makeCell(stampText));
            row.append(makeCell(stamp['location']));
            row.append(makeCell(stamp['coordinates']['latitude'] + ' ' + stamp['coordinates']['longitude']));
            row.append(makeCell(stamp['distance']));
            row.append(makeCell(stamp['last_seen']));
            parkStamper.nearby.table.append(row);
        }
    } else {
        parkStamper.util.message.popError('Unable to load nearby stamps: ' + textStatus);
        parkStamper.nearby.loadingElement.hide();
    }
};

parkStamper.nearby.nearbyErrorCallback = function(jqXHR, textStatus, errorThrown) {
    'use strict;';
    console.log('XHR failed: ' + textStatus + ' ' + errorThrown);
    parkStamper.util.message.popError('Unable to load nearby stamps: ' + textStatus + ' ' + errorThrown);
    parkStamper.nearby.loadingElement.hide();
};
