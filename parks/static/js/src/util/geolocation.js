/**
 * Geolocation using the HTML5 API with fallback to Google's Ajax geolocation API.
 */

goog.provide('parkStamper.util.geolocation.requestLocation');

/**
 * Grabs the user's location asynchronously and calls the callback function
 * with an object that looks like:
 * {
 *  'coords': {
 *   'latitude': 37.774929,
 *   'longitude': -122.419415
 *  }
 * }
 * @param {function({coords: {latitude: number, longitude: number}})} callback
 * @param {?function({code: number, message: string})} errorCallback
 */
parkStamper.util.geolocation.requestLocation = function(callback, errorCallback) {
    'use strict';
    if (navigator && navigator.geolocation) {
        // HTML5 geolocation
        navigator.geolocation.getCurrentPosition(callback, errorCallback);
    } else {
        // Fallback to Google Ajax API
        $.getScript('//www.google.com/jsapi').done(
            function() {
                if ((typeof google == 'object') && google.loader && google.loader.ClientLocation) {
                    callback({
                        'coords': {
                            'latitude': google.loader.ClientLocation.latitude,
                            'longitude': google.loader.ClientLocation.longitude
                        }
                    });
                }
            }
        ).fail(
            function() {
                if (errorCallback !== undefined) {
                    errorCallback({'code': 0, 'message': 'Geolocation not supported'});
                } else {
                    alert('Unable to find your location. Sorry!');
            }
        });
    }
};
