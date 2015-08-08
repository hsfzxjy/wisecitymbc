define(['jquery', 'main', 'bootstrap'], function ($) {
    var $topNav = $("#top-nav"), $body = $("body"), $mainContainer = $("#mainContainer");

    function adjustBody () {
        var paddingTop = $topNav.offset().top + $topNav.outerHeight();

        $mainContainer.css({
            "padding-top": paddingTop
        })
    }

    $(window).on('resize', adjustBody);

    $(adjustBody);
    $("#main-content").on('show', function () {
        console.log('show')
    })
});