(function ($, window, undefined) {
    var PAGE = 'page', 
        WATERFALL = 'waterfall',
        SINCE_FIELD = 'since', 
        BEFORE_FIELD = 'before',
        NEXT_FIELD = 'next',
        PREVIOUS_FIELD = 'previous';

    var emptyTemplate = '<div class="col-xs-12 display-none post empty-template empty load-list-item-empty"><h2>暂无数据</h2></div>';

    var baseConfig = {
            loading: false,
            nextAPI: null,
            previousAPI: null,
            hasNextPage: true,
            emptyTemplateId: '',
            emptyTemplate: emptyTemplate,
            preprocessor: $.emptyFunc,   
            listType: PAGE
        },
        waterfallConfig = {
            nextField: BEFORE_FIELD,
            previousField: SINCE_FIELD,
            reverse: true,        // Whether to reverse the data list
            firstTrigger: false,  // Whether to load the list after creating
            scroll: true,         // Whether to update while scrolling to the bottom
            autoLoad: false,      // Whether to update automatically
            autoLoadInterval: 30000,
            maxCount: -1          // The maximum items to display
        },
        pageConfig = {
            $nextButton: $({}),
            $previousButton: $({})
        },
        loadingConfig = {
            previous: {
                position: 'front'
            },
            next: {
                position: 'back'
            }
        };

    var $window = $(window), $document = $(document);

    function updateAPI (type, url, defaultAPI) {
        var fieldName = type+'API', triggeredFieldName = '_'+type+'Triggered';
        if (defaultAPI === undefined) defaultAPI = this._config.api;

        if (url) {
            this._config[fieldName] = API.raw(url);
        } else if (!this[triggeredFieldName]) {
            this._config[fieldName] = defaultAPI;
        }
    }

    /**
     * Get configure information by `listType`.
     * @param  {string} listType [`PAGE` or `WATERFALL`]
     * @return {void}
     */
    function getConfig (listType) {
        var config = $.extend({}, baseConfig);

        if (listType === PAGE) {
            config = $.extend(config, pageConfig);
        } else if (listType === WATERFALL) {
            config = $.extend(config, waterfallConfig);
        }

        return config;
    }

    /**
     * Initialize the config object.
     * `this` should be given as an `List` instance.
     * @param  {object} config [configuration object given by user]
     * @return {void}
     */
    function preprocessConfig (config) {
        this._nextTriggered = this._previousTriggered = false;

        this._config = $.extend(getConfig(config.listType), config);
        this._config.$container = $(this._config.$container);
        if (!this._config.template && this._config.templateId)
            this._config.template = $.getScript(this._config.templateId);
        this._config.emptyTemplate = $.getScript(this._config.emptyTemplateId) || emptyTemplate;
        this._config.nextAPI = this._config.api;
        this._config.previousAPI = this._config.api;
    }

    /**
     * @constructor
     * @param {object} config [configuration object given by user]
     */
    function PageList (config) {
        this._initialize(config);
    }

    PageList.prototype = {

        _initialize: function (config) {
            preprocessConfig.call(this, config);
            this._config.$nextButton = $(this._config.$nextButton);
            this._config.$previousButton = $(this._config.$previousButton);
            this._toggleClass();
            this._bindEvents();
            this._callAPI(this._config.api);
        },

        /**
         * Bind events to buttons.
         * @return {void} 
         */
        _bindEvents: function () {
            var self = this;

            this._config.$nextButton.on("click", function () {
                self.loadNext();
            });
            this._config.$previousButton.on("click", function () {
                self.loadPrevious();
            })
        },

        /**
         * A core function which call API directly.
         * @param  {API} api [The api to be called.]
         * @return {void}
         */
        _callAPI: function (api) {
            if (this._config.loading || !api) 
                api = API.empty();

            this._config.loading = true;
            //this._config.$container.loading(loadingConfig[type]);

            return this._render(api.get());
        },

        /**
         * Render the data retrieve from API.
         * @param  {API} api 
         * @return {void}     
         */
        _render: function (api) {
            var config = $.extend({
                    operation: 'clear'
                }, this._config), self = this;

            return api.ok(function (data) {
                $.renderAndInsert($.extend({
                    data: data.results
                }, config), function () {
                    self._config.loading = false;
                });

                updateAPI.call(self, 'next', data.next, null);
                updateAPI.call(self, 'previous', data.previous, null);

                self._toggleClass();
            }).always(function (_, __, xhr) {
                if (xhr.status !== 200) 
                    self._config.loading = false;
            });
        },

        /**
         * Toggle class of buttons according to the `nextAPI` and `previousAPI` field.
         * @return {void}
         */
        _toggleClass: function () {
            this._config.$nextButton.parent().toggleClass("disabled", !this._config.nextAPI);
            this._config.$previousButton.parent().toggleClass("disabled", !this._config.previousAPI);
        },

        /**
         * Load next data.
         * @return {void} 
         */
        loadNext: function () {
            var self = this;

            this._callAPI(this._config.nextAPI)
            .ok(function (data) {
                self._nextTriggered = true;
            });
        },

        /**
         * Load previous data.
         * @return {void} 
         */
        loadPrevious: function () {
            var self = this;

            return this._callAPI(this._config.previousAPI)
            .ok(function (data) {
                self._previousTriggered = true;
            });
        }

    };

    /**
     * @constructor
     * @param {object} config [configuration object given by user]
     */
    function WaterfallList (config) {
        this._initialize(config);
    }

    WaterfallList.prototype = {

        /**
         * Initialize.
         * @param  {object} config 
         * @return {void}
         */
        _initialize: function (config) {
            preprocessConfig.call(this, config);

            if (this._config.reverse) {
                this._config.nextField = BEFORE_FIELD;
                this._config.previousField = SINCE_FIELD;
            } else {
                this._config.nextField = SINCE_FIELD;
                this._config.previousField = BEFORE_FIELD;
            }

            if (this._config.firstTrigger) this.loadNext();

            this.configScrollEvent();
            this._autoLoad();
        },

        _autoLoad: function () {
            var self = this;

            setTimeout(function () {
                if (self._config.autoLoad) {
                    self.loadPrevious().always(function () {
                        self._autoLoad();
                    });
                    return;
                }

                self._autoLoad();
                
            }, this._config.autoLoadInterval)
        },

        /**
         * To call API.
         * @param  {string} type ['next' or 'previous']
         * @return {API}      [The API that called.]
         */
        _callAPI: function (type) {
            var api = (this._config.loading) ? API.empty() : this._config[type+'API'];

            this._config.loading = true;
            api = api.get();
            return this._render(api, type);
        },

        _triggeredAPI: function (type, data) {
            var otherType = (type === 'next' ? 'previous' : 'next');
            this['_'+type+'Triggered'] = true;
            updateAPI.call(this, type, data[this._config[type+'Field']]);
            updateAPI.call(this, otherType, data[this._config[otherType+'Field']]);
	        this._config.loading=false;
        },

        /**
         * To decrease items if it's number is greater than `maxCount`
         * @type {void}
         */
        _adjustItems: function () {
            if (this._config.maxCount < 0) return;

            var children = this._config.$container.children(), count = this._config.maxCount;

            if (children.length <= count) return;

            children = children.slice(count);
            children.fadeOut("normal", function () {
                children.remove();
            });
        },


        /**
         * Remove the empty div if data is not empty.
         * @param  {list} data 
         * @return {void}    
         */
        _toggleEmpty: function (data) {
            var $container = this._config.$container,
                $empty = $(".empty", this._config.$container),
                data = data.results;

            if (data.length) {
                $empty.remove();
            } else if (!$empty.length && !$container.children().length) {
                $.showHtml($(this._config.emptyTemplate).appendTo($container));
            }
        },

        /**
         * To render the data retrieved.
         * @param  {API} api [The API object called]
         * @return {API}     
         */
        _render: function (api, type) {
            var config = $.extend({
                    operation: (type === 'next' ? 'append' : 'prepend')
                }, this._config), self = this;

            return api.ok(function (data) {
                self._toggleEmpty(data);
                $.renderAndInsert($.extend({
                    data: data.results
                }, config));
                self._adjustItems();
            }).always(function (_, __, xhr) {

                if (xhr && xhr.status !== 200) 
                    self._config.loading = false;
            });
        },

        /**
         * Initialize the scroll events.
         * @return {void} 
         */
        configScrollEvent: function () {
            if (!this._config.scroll) return;
            var self = this;

            $window.on('scroll mousewheel', function () {
                if ($document.scrollTop() + $window.height() > $document.height() - 20) 
                    self.loadNext();
            });
        },

        /**
         * To load previous data.
         * @return {void} 
         */
        loadPrevious: function () {
            var self = this;

            return this._callAPI('previous')
            .ok(function (data) {
                self._triggeredAPI('previous', data);
            });

        },

        /**
         * To load next data.
         * @return {void} 
         */
        loadNext: function () {
            var self = this;

            if (!this._config.hasNextPage) return;

            var a = this._callAPI('next');
            a.ok(function (data) {
                self._triggeredAPI('next', data);
                self._config.hasNextPage = data.next !== null;
            });
        }
    };

    window.LIST = {

        /**
         * To create a list.
         * @param  {object} config [The `listType` field must be included.]
         * @return {List}        [The list that created.]
         */
        createList: function (config) {
            var classType;

            switch (config.listType) {
                case WATERFALL:
                    classType = WaterfallList;
                    break;
                case PAGE:
                    classType = PageList;
                    break;
            }

            return new classType(config);
        }
    };

})(jQuery, window);
