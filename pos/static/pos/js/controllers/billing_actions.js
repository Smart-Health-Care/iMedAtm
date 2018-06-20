(function () {
        var app = angular.module("billing_actions", ['posServiceModule', 'angularModalService','storageService']);

        app.controller('billing_actions', function ($scope,$rootScope, API , storage) {
            var vm = this;
            vm.user = storage.get("orders")[storage.get("currentOrder")].user;

            $scope.$on('updateCurrentUser', function (event, user) {
                vm.user = user;

            });

            $scope.$on('clearCurrentUser',function (event, user) {

               vm.user = null;
            });


            $scope.$on('getUserFailed',function (event, user) {

               vm.user = null;
            });

            vm.clearCurrentUser = function () {
                $rootScope.$broadcast('clearCurrentUser',vm.user);
            };




        });

    })();