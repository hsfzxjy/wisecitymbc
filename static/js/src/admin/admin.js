(function ($, window, undefined) {
    $(function () {
        var api = API.url('finance-year');

        $(['inc', 'reset']).each(function () {
            var $btn = $("#btn-"+this), action = this;
            $btn.on('click', function () {
                api.param({
                    action: action
                }).bindElements($btn).dialog().post();
            });
        });
    });
})(jQuery, window);
