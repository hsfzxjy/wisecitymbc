(function ($, window, undefined) {

    var extraFieldsMap = {}, loaded = false;

    $('body').on('click ', 'svg *', function (e) {
        e.originalEvent.cancelable = false;
        e.originalEvent.cancelBubble = false;
        e.originalEvent.bubbles = true;
    });

    Highcharts.setOptions({
        global: {
            timezoneOffset: -8 * 60
        }
    })

    function DataLoader (config) {
        var self = this;

        if (! loaded) {
            API.url('finance-extra-fields').get().ok(function (data) {
                extraFieldsMap = data;
            })
            .always(function () {
                loaded = true;
                self._initializeConfig(config);
                self._initialize();
            })
        } else {
            self._initializeConfig(config);
            self._initialize();
        }
    }

    DataLoader.prototype = {

        _setAPI: function (api) {
            this.api = 
            this.previousAPI = 
            this.nextAPI = api;
        },

        _initialize: function () {
            this._initializeComponents();
            this._initializeChart();
            this.loadPrevious();
        },

        _initializeConfig: function (config) {

            var defaultConfig = {
                title: "",
                extraFields: extraFieldsMap[config.category] || [],
                navigator: false
            },  defaultFields = [
                ["price", "价格", "line"]
            ];

            config = $.extend(defaultConfig, config);
            this.$container = config.$container = $(config.$container);

            defaultFields = defaultFields.concat(config.extraFields);
            this._fields = defaultFields;

            this._setAPI(
                config.api ||
                API.url(config.category).url(config.id).url('logs').param({limit:20})
            );

            this._first = true;
            this._loading = false;
            this._config = config;
        },

        _initializeComponents: function () {
            var $container = this._config.$container, self = this;

            $container.addClass("highcharts");
            this.$loader = $("<button/>")
                .text("加载更早的数据")
                .addClass("chart-loader btn btn-default")
                .prependTo($container)
                .on("click", function () {
                    self.loadPrevious();
                });

            this.api.bindElements(this.$loader);

            this.$chartContainer = $("<div/>")
                .addClass("chart-container")
                .prependTo($container);
        },

        _initializeSeries: function () {
            var series = [], i, fieldsInfo;
            this._seriesMap = {};
            this._dataArray = [];

            for (i = 0; i < this._fields.length; ++i) {
                fieldsInfo = this._fields[i];

                this._seriesMap[fieldsInfo[0]] = i;
                this._dataArray.push([]);
                series.push({
                    type: fieldsInfo[2],
                    name: fieldsInfo[1],
                    data: [],
                    yAxis: i,
                    tooltip: {
                        valueDecimals: 2
                    }
                });
            }

            return series;
        },

        _initializeYAxis: function () {
            var self = this, result = [], height = 100.0 / this._fields.length;

            $(this._fields).each(function (i) {
                result.push({
                    height: height + '%',
                    top:    i * height +'%',
                    lineWidth: 0,
                    offset: 0
                });
            });

            return result;
        },

        _initializeChart: function () {
            var series = this._initializeSeries();

            this.$chartContainer.highcharts('StockChart', {
                chart: {
                    backgroundColor: "transparent"
                },
                colors: ['#7cb5ec'],
                rangeSelector: {
                    enabled: false
                },
                scrollbar: {
                    enabled: this._config.navigator
                },
                navigator: {
                    enabled: this._config.navigator
                },
                title: {
                    style: {
                        color: "#FFF"
                    },
                    text: this._config.title
                },
                credits: {
                    enabled: false
                },
                series: series,
                yAxis: this._initializeYAxis()
            });

            console.log(this._getChart().container.onclick);
            this._getChart().container.onclick = null;
        },

        _getChart: function () {
            return this.$chartContainer.highcharts();
        },

        _adjustExtremes: function (chart) {
            var xAxis = chart.xAxis[0], extremes = xAxis.getExtremes();
            xAxis.setExtremes(extremes.dataMin, extremes.dataMax);
        },

        processData: function (action, data) {

            function pushData (arr, data) {
                switch (action) {
                    case "append": 
                        arr.push(data);
                        break;
                    case "prepend":
                        arr.unshift(data);
                        break;
                }
            }

            function parseData (data, fieldName) {
                return [data.timestamp, parseFloat(data[fieldName])];
            }

            var self = this;

            data = data.results;
            if (!data.length) return;
            if (action === "append") data = data.reverse();

            $(data).each(function () {
                var _obj = this, fieldName, index;
                _obj.timestamp *= 1000;

                for (fieldName in _obj) {
                    index = self._seriesMap[fieldName];
                    if (index === undefined) continue;
                    pushData(
                        self._dataArray[index],
                        parseData(
                            _obj,
                            fieldName
                        )
                    );
                }
            });

            this.placeData();
        },

        _setChartEmpty: function (chart, isEmpty) {
            if (isEmpty) {
                chart.showLoading('No data');
            } else {
                chart.hideLoading();
            }
        },

        placeData: function () {
            var chart = this._getChart(), notEmpty = true, arr;
            for (var i = 0; i < this._dataArray.length; i++) {
                arr = this._dataArray[i];
                chart.series[i].setData(arr);
                notEmpty = notEmpty && arr.length;
            }
            this._setChartEmpty(chart, !notEmpty);
            this._adjustExtremes(chart);
        },

        loadPrevious: function () {
            if (this._loading) return;
            var self = this;

            this._loading = true;
            this.previousAPI.get()
                .ok(function (data) {
                    self.processData("prepend", data);
                    if (self._first) {
                        self._first = false;
                        self.nextAPI = API.raw(data.since);
                    }
                    self.previousAPI = API.raw(data.before);
                }).always(function () {
                    self._loading = false;
                });
        },

        loadNext: function () {
            if (this._loading) return;
            var self = this;

            this._loading = true;
            this.nextAPI.get()
                .ok(function (data) {
                    self.processData("append", data);
                    self.nextAPI = API.raw(data.next);
                }).always(function () {
                    self._loading = false;
                });
        }

    };

    window.ChartDataLoader = DataLoader;

})(jQuery, window);
