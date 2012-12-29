goog.provide('parkstamper.nearby');
goog.provide('parkstamper.nearby.geoLocationCallback');

goog.require('parkstamper.util.geolocation.requestLocation');

parkstamper.nearby.geoLocationCallback = function(position) {
    var latLong = position.coords;
    var content = 'Location ' + latLong.latitude + ':' + latLong.longitude;
    parkstamper.nearby.element.append('<div>' + content + '</div>');
};

parkstamper.nearby.init = function(element) {
    parkstamper.nearby.element = element;
    parkstamper.util.geolocation.requestLocation(parkstamper.nearby.geoLocationCallback);
};

