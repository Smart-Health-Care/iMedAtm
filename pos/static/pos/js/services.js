(function () {
    var posService = angular.module("posServiceModule",[]);

    posService.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }]);

    posService.factory("API",
        function ($http) {

            var o = {};

            o.test = function () {

            };

            o.getInvoices = function () {
                return $http.get('/api/bills/');
            };

            o.getUserInfo = function(rfid_value){
                return $http.post('/api/get_user_info/',{rfid : rfid_value});
            };

            o.finishBill = function(bill_data)
            {
              return $http.post('/api/finish_bill/',bill_data)
            };


            o.getProducts = function () {
                return $http.get('/api/otc_medicine_list/');
            };

            o.getProductStock =function () {
                return $http.get('/api/products/stock/');
            };

            return o;
        }
    );


})();