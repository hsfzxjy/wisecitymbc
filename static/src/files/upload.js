(function ($, window, undefined) {

    function makeLink (data) {
        var isPicture = /\.(jpg|png|gif|bmp)$/;
        if (isPicture.test(data.name)) {
            return '<img src="{url}" class="width-100"></img>'.render(data)
        } else {
            return '<a href="{url}">{name}</a>'.render(data);
        }
    }

    function getWellDiv ($element) {
        return $element.parents('.well-file');
    }

    $('body').on('click', '.file-delete', function () {
        var $this = $(this), $well = getWellDiv($this), id = $well.data('id');

        API.url('storage').url('files').url(id).remove().ok(function (){
            $well.remove();
            FileUpload.events.trigger('file.remove', ['', id]);
        });
    }).on('click', '.file-insert', function () {
        FileUpload.events.trigger('file.insert-link', ['', makeLink(getWellDiv($(this)).data())]);
    });

    function File (config) {
        this._initialize(config);
    }

    $.extend(File.prototype, {
        _initializeEvents: function () {
            var self = this;
            $('.file-cancel', this.$FileDiv).on('click', function (){
                self.$FileDiv.remove();
                self._config.uploader.removeFile(self._config.file);
                self._config.uploader.stop();
                self._config.uploader.start();
            });
        },

        _initializeFileDiv: function () {
            var template = $.getScript(this._config.$container.data("template")||"defaultUploadTemplate");

            this.$FileDiv = $(template.render({
                name: this._config.filename
            })).prependTo(this._config.$container);
            this.$progressDiv  = this.$FileDiv.find('.file-progress');
            this.$progressSpan = this.$FileDiv.find('.file-progress-value');
            this.$operationDiv = this.$FileDiv.find('div.file-operation');

            this._initializeEvents();
        },

        _initializeConfig: function (config) {
            this._config = {};
            $.extend(this._config, config);
        },

        _initialize: function (config) {
            this._initializeConfig(config);
            this._initializeFileDiv();
        },

        setMode: function (mode) {
            if (mode === 'upload') {
                this.$progressDiv.removeClass('hidden');
                this.$operationDiv.addClass('hidden');
            } else if (mode === 'operation' && this._config.id) {
                this.$progressDiv.addClass('hidden');
                this.$operationDiv.removeClass('hidden');
                FileUpload.events.trigger('file.upload-done', [this._config.hash, this._config.id]);
            }
        },

        setProgressValue: function (value) {
            this.$progressSpan.text(value+'%');
        },

        setData: function (data) {
            this.$FileDiv.data(data);
        },

        done: function () {
            var self = this;

            API.url('storage').url('files').post({
                name: this._config.name
            }).ok(function (data) {
                $.extend(self._config, data);
                self.setData(data)
                self.setMode('operation');
            });
        }
    });

    function Uploader ($container, hash) {
        var self = this, fileList = {};

        this.$container = $($container);
        this.hash = hash;

        this.init = {

            FilesAdded: function (up, files) {
                $(files).each(function () {
                    fileList[this.key] = new File({
                        $container: self.$container,
                        name: this.key,
                        filename: this.name,
                        hash: self.hash,
                        file: this,
                        uploader: up
                    });
                });
                FileUpload.events.trigger('file.added', [self.hash]);
            },

            UploadProgress: function (up, file) {
                var fileObject = fileList[file.key];
                fileObject.setProgressValue(file.percent);
            },

            FileUploaded: function (up, file, info) {
                var data = $.decodeJSON(info);
                fileList[data.key].done();
            },

            Key: function (up, file) {
                return file.key = Number(new Date())+'/'+file.name;
            }
        };
    }

    window.FileUpload = {
        Uploader: Uploader,
        events: $({}),
        init: {}
    };
})(jQuery, window);
