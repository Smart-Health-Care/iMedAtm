(function () {
    var SS = angular.module("storageService",[]);

    SS.factory("storage", function () {
        var o = {};

        var defaultValues = {};


        defaultValues.user = null;

        defaultValues.currentOrder = 0;

        defaultValues.order = {
            products: [],
            user: defaultValues.user,
            status: ''
        };

        defaultValues.orders = [defaultValues.order];


        var data = {};
        o.getDefault = function (key) {
            if(key == 'order' || key == 'orders')
            {
                defaultValues.order.order_hash = sha256((new Date()).getTime()+'');
                defaultValues.orders = [defaultValues.order];
            }
            return JSON.parse(JSON.stringify(defaultValues[key]));

        };


        o.get = function (key) {
            if (data[key])
                return JSON.parse(JSON.stringify(data[key]));
            else
                return o.getDefault(key);
        };

        o.set = function (key, value) {
            data[key] = JSON.parse(JSON.stringify(value));
        };

        return o;
    });

})();