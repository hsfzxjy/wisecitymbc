define(['jquery', 'qiniu'], function ($, Qiniu) {
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

        Qiniu.uploader({
                        runtimes: 'html5,flash,html4',
                        browse_button: 'uploadMap',
                        uptoken_url: '/storage/uptoken/',
                        domain: 'http://7xkade.dl1.z0.glb.clouddn.com',
                        max_file_size: '50mb',
                        flash_swf_url: '/static/plupload/Moxie.swf',
                        max_retries: 3,
                        dragdrop: false,
                        chuck_size: '4mb',
                        auto_start: true,
                        init: {
                            Key: function () {
                                return 'map';
                            },
                            FileUploaded: function () {
                                toastr.info('OK'); 
                            }
                        }
                    });
    });
}); 
