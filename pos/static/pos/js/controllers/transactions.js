(
    function () {
        var transactionsCtrl = angular.module("transactions",["posServiceModule"]);

        transactionsCtrl.controller("transactionsCtrl",function ($scope,$rootScope,API) {
            var vm = this;
            vm.transactions = [];

            API.getInvoices().then(function (data) {
                vm.transactions = data.data.results;
            },function () {
            });

        });


    }

)();