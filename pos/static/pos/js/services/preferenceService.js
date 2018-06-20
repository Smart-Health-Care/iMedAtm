(function () {
    var app = angular.module("preferenceService", []);

    app.factory("preference", function ($http) {

        var o = {};

        var preference = {};

        o.refreshPreferences = function () {
            $http.get("/api/preferences/").then(function (response) {
               preference = response.data;

            },function () {

            });
        };

        return o;

    });


})();