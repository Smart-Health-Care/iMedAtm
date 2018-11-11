(function () {
    var app = angular.module("pos", ['routesModule', 'posServiceModule', 'angularModalService', 'billing_actions', 'storageService', 'alertService', 'transactions', 'preferenceService']);

    app.run(
        function (API) {

        }
    );
    app.controller('billingCtrl', function ($scope, $rootScope, $filter, ModalService, API, alertService, storage, preference) {
        var vm = this;

        vm.orders = [];

        function saveChanges() {
            storage.set("orders", vm.orders);
            storage.set("currentOrder", vm.currentOrder);
        }

        function notifyChange() {
            $rootScope.$broadcast('updateCurrentOrder', vm.orders[vm.currentOrder]);
            $rootScope.$broadcast('updateCurrentUser', vm.orders[vm.currentOrder].user);
        }


        function initiateNewOrder() {
            order = storage.getDefault('order');
            order.order_hash = sha256((new Date()).getTime() + '');
            vm.orders.push(order);
            vm.currentOrder = vm.orders.indexOf(order);
            notifyChange();
            saveChanges();
        }


        function initialize() {
            vm.orders = storage.get("orders");
            vm.currentOrder = storage.get("currentOrder");
            preference.refreshPreferences();
        }

        initialize();

        $scope.$on('productClicked', function (event, data) {
            console.log("product " + data.id);
            var products = $filter("filter")(vm.orders[vm.currentOrder].products, {id: data.id}, true);

            if (products.length == 0) {
                var copy = angular.copy(data);
                copy.qty = 1;
                vm.orders[vm.currentOrder].products.push(copy);
            }
            else {
                products[0].qty++;
            }
            $rootScope.$broadcast('updateCurrentOrder', vm.orders[vm.currentOrder]);
        });

        $scope.$on('updateCurrentOrder', function (event, data) {
            saveChanges();
        });

        vm.openCardModal = function () {
            ModalService.showModal({
                templateUrl: "/static/pos/templates/card_modal.html",
                controller: "cardModalCtrl",
                controllerAs: 'vm'
            }).then(function (modal) {
                modal.element.modal();
                modal.closed.then(function () {
                    console.log("test")
                });
                modal.close.then(function (result) {
                    if (result != '')
                        API.getUserInfo(result).then(
                            function (data) {
                                var user = data.data;
                                if (!user.error) {
                                    $rootScope.$broadcast('updateCurrentUser', user);
                                }
                                else {
                                    $rootScope.$broadcast('getUserFailed', user);
                                }
                            },
                            function () {
                            }
                        );
                });
            });
        };


        $scope.$on('updateCurrentUser', function (event, user) {
            var currentOrder = vm.orders[vm.currentOrder];
            currentOrder.user = user;
            if (currentOrder.status == 'userPending') {
                vm.finishBill();
                currentOrder.status = "userVerified"
            }
            saveChanges();

        });

        $scope.$on('getUserFailed', function (event, user) {
            var currentOrder = vm.orders[vm.currentOrder];
            currentOrder.user = null;
            if (currentOrder.status == 'userPending') {
                currentOrder.status = "userVerificationFailed"
            }
            alertService.showAlert("User authentication failed !!");
            saveChanges();

        });

        $scope.$on("clearCurrentUser", function (event) {
            vm.orders[vm.currentOrder].user = null;
            $rootScope.$broadcast("updateCurrentUser", null);
        });

        $scope.$on("reduce_item", function (event, product_id) {
            var products = vm.orders[vm.currentOrder].products;
            var product = $filter("filter")(vm.orders[vm.currentOrder].products, {id: product_id}, true)[0];
            product.qty--;
            if (product.qty == 0) {
                var position = products.indexOf(product);
                products.splice(position, 1);
            }
            $scope.$broadcast('updateCurrentOrder', vm.orders[vm.currentOrder]);


        });

        $scope.$on("change_qty", function (event, product_id,qty) {
            var products = vm.orders[vm.currentOrder].products;
            var product = $filter("filter")(vm.orders[vm.currentOrder].products, {id: product_id}, true)[0];
            product.qty=qty;
            if (product.qty == 0) {
                var position = products.indexOf(product);
                products.splice(position, 1);
            }
            $scope.$broadcast('updateCurrentOrder', vm.orders[vm.currentOrder]);


        });


        vm.createNewBill = function () {
            initiateNewOrder();
        };

        function countCompleted() {
            var count = 0;
            for (var i = 0; i < vm.orders.length; i++) {
                if (vm.orders[i].status != "completed") {
                    count++;
                }
            }
            return count;
        }

        vm.removeBill = function ($event, order) {
            $event.stopPropagation();
            if (countCompleted() != 1) {
                if (order.status != "completed") {
                    var position = vm.orders.indexOf(order);
                    if (position == vm.currentOrder) {
                        var nextOrder = position + 1;
                        while (nextOrder < vm.orders.length && vm.orders[nextOrder].status == "completed") {
                            nextOrder++;
                        }
                        if (nextOrder == vm.orders.length) {
                            nextOrder = position - 1;
                            while (nextOrder >= 0 && vm.orders[nextOrder].status == "completed") {
                                nextOrder--;
                            }
                        }

                        vm.currentOrder = nextOrder;
                    }

                    var currentOrder = vm.orders[vm.currentOrder];
                    vm.orders.splice(position, 1);
                    vm.currentOrder = vm.orders.indexOf(currentOrder);
                    notifyChange();
                    saveChanges();

                }
            }

        };

        vm.selectBill = function (order) {
            index = vm.orders.indexOf(order);
            vm.currentOrder = index;
            notifyChange();
        };

        vm.finishBill = function () {
            var currentOrder = vm.orders[vm.currentOrder];

            if (currentOrder.products.length != 0) {
                total = 0;
                angular.forEach(currentOrder.products, function (product, key) {
                    total = total + product.qty * product.price
                });
                // if (currentOrder.user != null) {
                    // total <= currentOrder.user.balance || currentOrder.user.is_staff ==
                    currentOrder.status = 'connecting';
                    // currentOrder.user_id = currentOrder.user.id;
                    // currentOrder.rfid = currentOrder.user.rfid;
                    API.finishBill(currentOrder).then(function (data) {
                        //    handle success here
                        var response = data.data;
                        if (response.status == "success") {
                            currentOrder.status = "completed";
                            $rootScope.$broadcast('OrderCompleted');
                            // initiateNewOrder();
                        }
                        else {
                            //dont know what to do
                        }
                        alertService.showAlert(response.message,response.qty);


                    }, function (data) {
                        alertService.showAlert("Server throwing error");
                    });
                // }
                // else {
                //     vm.openCardModal();
                //     currentOrder.status = 'userPending';
                //
                // }

            }
            else {
                alertService.showAlert("No products selected")
            }


        };

    });


    app.controller('orderItemsCtrl', function ($scope, $rootScope, API, $filter, storage) {
        var vm = this;

        vm.order = storage.get("orders")[storage.get("currentOrder")];

        $scope.$on("updateCurrentOrder", function (event, data) {
            angular.copy(data,vm.order);
        });

        vm.getOrderTotal = function () {
            var t = 0;
            angular.forEach(vm.order.products, function (product) {
                t = t + (product.price * product.qty);

            });
            return t;
        };

        vm.getItemTotal = function (item) {
            return item.price * item.qty;
        };
        vm.minus = function (product_id) {
            $rootScope.$broadcast("reduce_item", product_id);
        };
        vm.changeQty = function(product_id,qty,prevQty){
            if(qty)
                $rootScope.$broadcast("change_qty", product_id,parseInt(qty));
        };

    });


    app.directive('keypressEvents',

        function ($document, $rootScope) {
            return {
                restrict: 'A',
                link: function (scope, element, attrs) {

                    element.on('$destroy', function () {
                        $document.unbind('keypress');
                    });

                    console.log('linked');
                    $document.bind('keypress', function (e) {
                        $rootScope.$broadcast('keypress', e, String.fromCharCode(e.which));
                    });
                }
            }
        });


    app.controller('cardModalCtrl', function ($scope, $rootScope, close, $element) {

        var vm = this;
        $scope.key = "";
        $rootScope.$on('keypress', function (evt, obj, key) {

            if (obj.keyCode == 13) {
                vm.dismissModal($scope.key);
            }
            if (obj.keyCode == 27) {
                vm.dismissModal(false);
            }
            $scope.$apply(function () {
                $scope.key += key;
            });
        });
        vm.dismissModal = function (result) {
            $element.modal('hide');
            close(result, 500); // close, but give 500ms for bootstrap to animate
        };

    });

})();