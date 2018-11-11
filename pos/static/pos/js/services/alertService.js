(function () {
    var alertService = angular.module("alertService", ['angularModalService']);

    alertService.factory("alertService", function (ModalService) {

        var o = {};


        o.showAlert = function (message,qty=0) {
            // if(qty!==0){
            //     $.get("/api/v1/play_audio?qty="+qty, function (data) {});
            // }
            ModalService.showModal({
                templateUrl: "/static/pos/templates/message_modal.html",
                controller: function ($scope, close, $element, message) {
                    $scope.closeM = function () {
                        $element.modal('hide');
                        close(false, 500);

                    };
                    $scope.confirm = function () {
                        window.location.href = '/users/otc_pos';
                    };
                    $scope.message = message;

                },
                inputs: {
                    message: message
                }
            }).then(function (modal) {
                modal.element.modal();

            });

        };


        return o;

    });

})();