(function () {
    var routesModule = angular.module("routesModule", ['ngRoute']);

    routesModule.config(
        function ($routeProvider,$locationProvider) {
            $routeProvider
                .when("/", {
                    templateUrl: "/static/pos/templates/main.html",
                    controller: "billingCtrl",
                    controllerAs: "bill"

                })
                .when("/transactions", {
                    templateUrl: "/static/pos/templates/transactions.html",
                    controller: "transactionsCtrl",
                    controllerAs: "trans"

                });


        }
    );


})();