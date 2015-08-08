(function () {
    
    var _paths = {
            _admin: 'admin/admin',
            _jquery: 'lib/jquery/jquery-1.11.1.min',
            bootstrap: '//libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min',
            _statusDetail: 'articles/status-detail',
            _main: 'common/main',
            _chart: 'common/chart',
            highcharts: '//code.highcharts.com/stock/highstock',
            ckeditor: 'ckeditor/ckeditor',
            plupload: 'plupload/plupload.full.min',
            _qiniu: 'files/qiniu.min',
            _uploadUtils: 'files/upload',
            _toastr: 'lib/toastr.min',
            _chatUtils: 'chat/chat',
            _chatDisplayUtils: 'chat/chat-display',
            saeChannel: '//channel.sinaapp.com/api',
            _channelUtils: 'chat/channel',
            _pinyin: 'chat/pinyin'
        }, path_prefix = debug ? 'src/' : 'build/', paths = {};

        for (var pkg in _paths) {
            if (!_paths.hasOwnProperty(pkg)) continue;
            if (pkg[0] !== '_') {
                paths[pkg] = _paths[pkg];
            } else {
                var _pkg = pkg.slice(1);
                paths[_pkg] = path_prefix+_paths[pkg];
            }
        }

    require.config({
        waitSeconds: 0,
        baseUrl: '/static',
        paths: paths,
        shim: {
            bootstrap: {
                deps: ['jquery']
            },
            main: {
                deps: ['jquery', 'bootstrap', 'toastr']
            },
            highcharts: {
                deps: ['jquery']
            },
            chart: {
                deps: ['jquery', 'main', 'highcharts'],
                exports: 'ChartDataLoader'
            },
            ckeditor: {
                exports: 'CKEDITOR'
            },
            plupload: {
                exports: 'plupload'
            },
            qiniu: {
                deps: ['plupload'],
                exports: 'Qiniu'
            },
            uploadUtils: {
                deps: ['jquery', 'main'],
                exports: 'FileUpload'
            },
            toastr: {
                deps: ['jquery'],
                exports: 'toastr'
            },
            channelUtils: {
                deps: ['jquery', 'saeChannel', 'main']
            },
            chatUtils: {
                deps: ['jquery', 'main', 'channelUtils', 'pinyin', 'chatDisplayUtils']
            },
            statusDetail: {
                deps: ['jquery', 'main', 'bootstrap']
            },
            admin: {
                deps: ['jquery', 'main']
            }
        }
    });
})();