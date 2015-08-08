(function ($, window, undefined) {

    "use strict";

    var csrftoken = $.getCookie('csrftoken'), validMethods = /^(GET|HEAD|OPTIONS|TRACE)$/;
    function csrfSafeMethod(method) {
        return (validMethods.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function buildEmptyXHR () {
        var emptyXhr = $.Deferred();
        emptyXhr.statusCode = $.emptyFunc;
        emptyXhr.always = $.autoInvokeFunc;
        return emptyXhr;
    }

    function requestUrl (url, data, method) {
        if (!url || url === '/api/') return buildEmptyXHR();

        if ($.isPlainObject(data)) data = $.encodeJSON(data);
        return $.ajax({
            url: url,
            type: method,
            contentType:"application/json",
            data: data,
            dataType: 'json'
        });
    }

    function API(name, _url, type, params) {
        this._showDialog = false;
        this._dialogOptions = {
            notFound: "啊哦，该操作并不存在耶～～",
            ok: "哈哈，操作成功了！",
            forbidden: "嘿，这样做是不允许的哟～～",
            serverError: "哎呀，好像有错误发生了T_T 耐心等待一下好么，我们会尽快修复的。。。"
        };
        this.type = type || 'action';
        this.isEmpty = !_url && !name;
        this._url = _url || '/api/';
        this.name = name;
        this.params = $.extend({}, params);
        this._initialize();
    }

    API.prototype = {

        _initialize: function () {
            if (this.name) this._url += this.name + '/';
            this._elements = $();
            this._bindMethods();
        },

        _buildUrl: function () {
            var url = this._url;

            if (this.type !== 'raw') {
                url += '?' + $.param(this.params);
            }

            return url;
        },

        _forceElementsState: function (state) {
            $(this._elements).each(function () {
                var $this = $(this);
                $this.button && $this.button(state);
            });
        },

        _bindMethod: function (method) {
            var self = this, statusCodes = {
                404: "notFound", 
                403: "forbidden", 
                400:"paramError", 
                405:"methodNotAllowed", 
                420:"captchaError",
                200: "ok",
                500: "serverError"
            };

            // A closure is needed to ensure the `method` has been properly bound to prototype.
            (function (method) {
                API.prototype[method] = function (data) {
                    var callbacks = {}, statusActions = {}, defered, code, callback;

                    if (method === 'remove') method = 'delete';

                    for (code in statusCodes) {
                        (function (code) { 
                            statusActions[code] = function (xhr) {
                                var data = xhr.responseText;

                                try {
                                    data = $.decodeJSON(data);
                                } catch (error) {

                                }

                                callbacks[code].fire(data);
                            };
                        })(code);
                    }

                    self._forceElementsState('loading');
                    defered = requestUrl(this._buildUrl(), data, method);
                    for (code in statusCodes) {
                        callback = callbacks[code] = $.Callbacks("once memory");
                        defered[statusCodes[code]] = callback.add;
                    }

                    defered
                        .always(function () {
                            self._forceElementsState('reset');
                        })
                        .done(function (data) {
                            callbacks[200].fire(data);
                        })
                        .statusCode(statusActions);

                    if (self._showDialog) {
                        defered.ok(function () {
                            toastr.success(self._dialogOptions.ok);
                        }).serverError(function () {
                            toastr.error(self._dialogOptions.serverError);
                        }).forbidden(function () {
                            toastr.warning(self._dialogOptions.forbidden);
                        }).notFound(function () {
                            toastr.info(self._dialogOptions.notFound);
                        })
                    }

                    return defered;
                };
            })(method);
        },

        _bindMethods: function () {
            var i, methods = ['get', 'post', 'remove', 'patch'];

            for (var i = 0; i < methods.length; i++) {
                this._bindMethod(methods[i]);
            }
        },

        param: function () {
            var params = {};
            if (arguments.length === 1) {
                params = arguments[0];
            } else {
                params[arguments[0]] = arguments[1];
            }

            if ($.isPlainObject(params)) $.extend(this.params, params);
            return this;
        },

        hasParam: function (name) {
            return this.params[name] !== undefined;
        },

        url: function (name) {
            return new API(name, this._url, 'action', this.params);
        },

        id: function (id) {
            return new API(id, this._url, 'id', this.params);
        },

        bindElements: function (elements) {
            this._elements = this._elements.add(elements);
            return this;
        },

        dialog: function (options) {
            this._showDialog = true;
            if (options) $.extend(this._dialogOptions, options);
            return this;
        }
    };

    window.API = {

        url: function (name) {
            return new API(name);
        },

        raw: function (url) {
            return new API('', url, 'raw');
        },

        empty: function () {
            return new API('', '', 'raw');
        }
    };

})(jQuery, window);
