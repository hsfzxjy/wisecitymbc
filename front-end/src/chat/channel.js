;(function (window, $, undefined) {

    var channelUrl = '', connected = false, updating = false, ht = false;
    window.saeChannel = null;

    /**
     * class `Channel` in Singleton mode.
     */
    function Channel() {
        var self = this;

        this.events = $({});
        //this.connect();
        this.getChannelUrl().ok(function (data) {
            self.channelData = data;
        })
        if (hasLogined && !debug) this.setupTimer();
    }

    Channel.prototype = {

        needToUpdateChannel: function () {
            return  (!connected) ||
                    (this.channelData.expired_time && this.channelData.expired_time < $.now() / 1000) ||
                    (saeChannel && saeChannel.readyState === 3);
        },

        setupHeartBeatTimer: function () {
            var self = this;
            setTimeout(function () {
                if (connected && saeChannel && navigator.onLine) {
                    ht = false;
                    saeChannel.send('ht');
                    setTimeout(function () {
                        if (!ht) connected = false;
                        ht = false;
                    }, 5000);
                }

            self.setupHeartBeatTimer();
            }, 15000);
        },

        setupExpireTimer: function () {
            var self = this;

            setTimeout(function () {
                if (!updating && navigator.onLine) {
                    if (!window.sae) {
                        self.getScript();
                    } else if (self.needToUpdateChannel()) {
                        self.connect();
                    }
                }

                self.setupExpireTimer();
            }, 1000);

        },

        setupTimer: function () {
            var self = this;
            this.setupHeartBeatTimer();
            this.setupExpireTimer();
        },

        getScript: function () {
            updating = true;

            $.ajax({
                url: "http://channel.sinaapp.com/api.js",
                crossDomain: true,
                dataType: "script",
                cache: true
            }).always(function () {
                updating = false;
            })
        },

        /**
         * Get channel URL from server.
         * @return {Promise} The promise object.
         */
        getChannelUrl: function () {
            var self = this;

            return API.url('channel-url').get();
        },

        sendMessage: function (message) {
            saeChannel && saeChannel.send(message);
        },

        /**
         * Connect to the server.
         * @return {void} 
         */
        connect: function () {
            var self = this;

            if (!hasLogined) return;

            saeChannel && saeChannel.close();
            updating = true;

            this.getChannelUrl().ok(function (data) {
                if (saeChannel !== null) {
                    //if (self.channelData.channel.url === data.channel.url) return;
                    saeChannel.close();
                }

                self.channelData = data;
                saeChannel = new sae.Channel(data.channel.url);
                connected = true;
                self.bindEvents();
            })
            .always(function () {
                updating = false;
            });
        },

        /**
         * Bind events for `saeChannel` object.
         * @return {void} 
         */
        bindEvents: function () {
            var self = this;

            function eventWrapper (eventName, argsProcessor) {

                return function () {
                    if (!argsProcessor || argsProcessor && argsProcessor(arguments))
                        return self.events.trigger(eventName, $.argumentsToArray(arguments));
                }
            }

            if (!saeChannel) return;

            saeChannel.onopen = eventWrapper('channel.open');
            saeChannel.onclose = eventWrapper('channel.close');
            saeChannel.onerror = eventWrapper('channel.error');
            saeChannel.onmessage = eventWrapper('channel.message', function (args) {
                var data = args[0].data;
                if (data === 'ht') {
                    ht = true;
                    return false;
                }
                console.log(data);
                if (args[0].data === 'close') return false;
                args[0] = $.decodeJSON(data);
                return true;
            });
        }
    };
        
    $(function () {
        window.channel = new Channel();
        window.channel.events.on('open', function () {
            console.log(arguments);
        });
    });

})(window, jQuery);