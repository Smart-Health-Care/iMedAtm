(function () {
    var app = angular.module("pos");
    app.controller('productsController', function ($scope, $rootScope, API) {

        var vm = this;

        vm.products = [];
        API.getProducts().then(function (data) {
            vm.products = data.data;
        }, function (data) {
            console.log(data);
        });
        vm.addToBill = function (product) {
            if (product.stock > 0) {
                $rootScope.$broadcast('productClicked', product);
            }
        };

        $scope.$on("OrderCompleted", function (event, data) {
            vm.updateProductStock();
        });

        vm.updateProductStock = function () {
            API.getProductStock().then(
                function (response) {
                    var products = response.data;

                    angular.forEach(products, function (product) {

                        angular.forEach(vm.products, function (pr) {
                            if (pr.id === product.id) {
                                pr.stock = product.stock;
                            }
                        });

                    });

                },
                function (response) {

                }
            );

        };

    });

})();