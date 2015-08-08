(function ($, window, undefined) {
    function Levenshtein_Distance(s,t){
        var n=s.length;// length of s
        var m=t.length;// length of t
        var d=[];// matrix
        var i;// iterates through s
        var j;// iterates through t
        var s_i;// ith character of s
        var t_j;// jth character of t
        var cost;// cost

        // Step 1

        if (n == 0) return m;
        if (m == 0) return n;

        // Step 2

        for (i = 0; i <= n; i++) {
            d[i]=[];
            d[i][0] = i;
        }

        for (j = 0; j <= m; j++) {
            d[0][j] = j;
        }

        // Step 3

        for (i = 1; i <= n; i++) {

            s_i = s.charAt (i - 1);
            
            // Step 4
            
            for (j = 1; j <= m; j++) {

                t_j = t.charAt (j - 1);

                // Step 5

                if (s_i == t_j) {
                    cost = 0;
                }else{
                    cost = 1;
                }

                // Step 6
                
                d[i][j] = Math.min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1] + cost);
            }
        }

        // Step 7

        return d[n][m];
    }

    //求两个字符串的相似度,返回相似度百分比
    function Levenshtein_Distance_Percent(s,t){
        var l=s.length>t.length?s.length:t.length;
        var d=Levenshtein_Distance(s,t);
        return (1-d/l);
    }

    window.compare = Levenshtein_Distance_Percent;
})(jQuery, window);

(function($, window, undefined){

    var CHAT = {
        isMobile: function () {
            return $("body").width() <= 991;
        },

        toggle: function () {
            $chatWindow.removeClass('hidden');
            $contentContainerDiv.trigger('adjust-height');
            if (!this.isMobile()) return;
            $("#sidebar,#main-content").toggleClass('mobile-hidden','slow');
            $contentContainerDiv.trigger('adjust-height');
        },

        showInfo: function (text) {
            $infoMessage.removeClass('hidden');
            $contentContainerDiv.trigger('adjust-height');
            $infoMessageText.text(text);
        },

        hideInfo: function () {
            $infoMessage.addClass('hidden');
            $contentContainerDiv.trigger('adjust-height');
        },

        loading: false,

        loadAPI: function (api) {
            var self = this;

            if (this.loading || !api) return API.empty().get();

            this.loading = true;

            return api.get();
        }
    }, Message = {

        /**
         * Process the message sent by private chat.
         * @param  {object} message Message received.
         * @return {void}         
         */
        _processUserMessage: function (message) {
            var contextId;

            if (message.receiver.id == userid) {
                contextId = message.sender.id;
            } else {
                contextId = message.receiver.id;
                message.class_name = 'current-user';
            }

            message.uniqueId = message.type+contextId;
        },

        /**
         * Process the message sent through a discussion.
         * @param  {object} message Message received.
         * @return {void}         
         */
        _processDiscussionMessage: function (message) {
            message.class_name = (message.sender.id==userid?'current-user':'');

            message.uniqueId = message.type+message.discussion.id;
        },

        _processMessage: function (message) {

            function getAttachmentsContent () {
                var html = [];

                $(message.attachments).each(function () {
                    html.push(templates.attachment.render(this));
                });

                return html.join('');
            }

            message.type = (message.discussion?'discussion':'user');
            message.attachments_content = getAttachmentsContent();

            if (message.type === 'discussion') {
                this._processDiscussionMessage(message);
            } else {
                this._processUserMessage(message);
            }
        },

        processMessage: function (message) {
            var self = this;

            if (message.results || $.isArray(message)) {
                $(message.results || message).each(function () {
                    self._processMessage(this);
                });
            } else {
                this._processMessage(message);
            }            
        },

        messagesCount: {
            discussion: 0,
            user: 0
        },

        setMessagesCount: function (type, count) {
            if (count < 0) count = 0;
            this.messagesCount[type] = count;
            var $icon = $(type === 'user' ? '.fa-user' : '.fa-group');
            count ? $icon.addClass('highlight') : $icon.removeClass('highlight');
        },

        incMessagesCount: function (type, count) {
            this.setMessagesCount(type, this.messagesCount[type]+count);
        },

        decMessagesCount: function (type, count) {
            this.setMessagesCount(type, this.messagesCount[type]-count);
        }
    };

    var $window = $(window), $document = $(document), pinyin = new Pinyin(),
        dataList = {}, chatWithUniqueId = $.getUrlParam('chatwith'),
        apiUsers = API.url('users').param({limit: 1000}),
        apiDiscussions = API.url('discussions').url('joined').param({limit: 1000}), templates,
        $userList, $discussionList, $discussionContactList,
        $userContactList, $chatWriteForm, $chatWriteEditor, $contentContainer,
        $contentParent, $chatWindow, $sideBar, $contentContainerDiv,
        $infoMessage, $infoMessageText, $more;

    /*********************************************/
    /* Definition of tool functions. */
    /*********************************************/

    function preprocessData(data) {
        data.type = (data.nickname !== undefined?'user':'discussion');
        data.uniqueId = '{type}{id}'.render(data);
    }

    function scrollTo (height) {
        $contentParent.scrollTop = height;
    }

    function scrollToBottom () {
        scrollTo($contentParent.scrollHeight);
    }

    function updateContent(text, opertaion) {

        var $text = $(text), oldHeight = $contentParent.scrollHeight;

        if (!text) CHAT.loading = false;

        if (opertaion === 'append') {
            $text.appendTo($contentContainer);
        } else if (opertaion === 'prepend') {
            $text.prependTo($contentContainer);
        }

        $text.fadeIn({
            duration: 'slow',
            progress: function () {
                if (opertaion === 'append') {
                    scrollToBottom();
                } else {
                    scrollTo($contentParent.scrollHeight - oldHeight);
                }
            },
            done: function () {
                CHAT.loading = false;
            }
        });
    }

    /********************************************/
    /* Definition of class `ChatContext` */
    /** Each `ChatContext` instance stores data of a chat status, user-to-user or
        a discussion.
    */
    /********************************************/

    //Constructor
    function ChatContext(data) {
        this._data = data;
        this._receivedMessages = {};
        this._first = true;
        this._activated = false;
        this._context = '';
        this._unreadCount = 0;
        this._firstId = null;
        this._preprocessData();
        this._initializeAPI();
        this._getSideBarElement();
    }

    // prototype
    ChatContext.prototype = {

        _initializeAPI: function () {
            if (this._data.type === 'user') {
                this._API = API.url('chat').param({partner: this._data.id});
            } else {
                this._API = API.url('discussions').url(this._data.id).url('messages');
            }
            this._historyAPI = this._API.param({limit: 10});
            this._unreadAPI = this._API.url('unread');
            this._syncAPI = API.url('synctime');
        },

        /**
            Add fundamental fields into `_data` member.
        */
        _preprocessData: function () {
            preprocessData(this._data);
        },

        _getSideBarElement: function () {
            var self = this, $parent = (this._data.type === 'user' ? $userList : $discussionList);

            $parent = $parent.filter(function () {
                return $(this).hasClass('show');
            })

            this._$sidebarElement = $('li', $parent).filter(function () {
                return $('a', this).data('id') === self._data.uniqueId;
            });
        },

        /**
            Insert text to the context.
            @param operation: `append` or `prepend`, defaults to `append`.
        */
        _insertText: function (text, operation) {
            operation = operation || 'append';

            if (operation === 'append') {
                this._context += text;
            } else if (operation === 'prepend') {
                this._context = text + this._context;
            }
        },

        _render: function (message) {

            function render(message) {
                return templates.message.render(message);
            }

            if (message.results || $.isArray(message)) {
                var html = [];
                $(message.results || message).each(function () {
                    html.push(render(this));
                });
                return html.join('');
            } else {
                return render(message);
            }
        },

        _toggleMore: function () {
            if (this._historyAPI.isEmpty) {
                $more.hide();
            } else {
                $more.show();
            }
        },

        loadHistory: function () {
            var self = this;

            if (!this._historyAPI.hasParam('beforeid') && this._firstId)
                this._historyAPI.param({
                    beforeid: this._firstId
                })

            CHAT.loadAPI(this._historyAPI).ok(function (data) {
                var message = data.results.reverse();

                Message.processMessage(message);
                self.updateContext(message, 'prepend');
                self._historyAPI = data.before ? API.raw(data.before) : API.empty();
                self._toggleMore();
            });
        },

        syncTime: function () {
            //channel.sendMessage(this._data.uniqueId);
            this._syncAPI.post({
                unique_id: this._data.uniqueId
            });
            this.setUnreadCount(0);
        },

        loadUnread: function () {
            var self = this;

            CHAT.loadAPI(this._unreadAPI).ok(function (data) {
                var message = data.results.reverse();

                if (data.results.length) self._historyAPI.param({
                    beforeid: data.results[0].id
                });

                Message.processMessage(message);
                self.updateContext(message, 'append');
                self.syncTime();
            });
        },

        /**
            A proxy method for context data management.
        */
        updateContext: function (message, operation) {
            var text = this._render(message);
            operation = operation || 'append';

            this._insertText(text, operation);
            if (this._activated) {
                updateContent(text, operation);
            }
        },

        _received: function (message) {
            if (message.id in this._receivedMessages) {
                delete this._receivedMessages[message.id];
                return true;
            }

            return false;
        },

        /**
            What to do when a message is handled.
        */
        handleMessage: function (message) {
            if (!this._activated) this.notify(message);
            if (this._first) return;
            if (this._received(message)) return;
            this._receivedMessages[message.id] = 1;
            if (!this._firstId) this._firstId = message.id;
            this.updateContext(message, 'append');
            if (this._activated) this.syncTime();
        },

        notify: function (message) {
            this.setUnread(this._unreadCount+1);
        },

        setUnread: function (count) {
            this.setUnreadCount(count);
            count && this._$sidebarElement.prependTo(this._$sidebarElement.parent());
        },

        setUnreadCount: function (count) {
            Message.incMessagesCount(this._data.type, count - this._unreadCount);
            this._unreadCount = count;
            this.updateBadge(count);
        },

        updateBadge: function (count) {
            if (!count) count = '';
            $('.badge', this._$sidebarElement).html(count);
        },

        /**
         * Set the header of chat window.
         */
        setHeader: function () {
            $("#chat-header").html('{a_tag}{name}'.render(this._data));
        },

        /**
            Activate the context.
        */
        activate: function () {
            if (this._first) {
                this._first = false;
                this.loadUnread();
            } else {
                this.syncTime();
            }

            this._activated = true;
            this.setHeader();
            this._toggleMore();
            updateContent(this._context, 'append');
            if (this._data.type === 'user') {
                $("input[name='receiver']", $chatWriteForm).val(this._data.id);
            } else {
                $("input[name='discussion']", $chatWriteForm).val(this._data.id);
            }
        },

        /**
            Deactivate the context.
        */
        deactivate: function () {
            this._activated = false;
            this._context = $contentContainer.html();
            $contentContainer.html('');
        },

        /**
            Compare the data with this._data so as to locate the window.
            @param data: the data to be compared.
        */
        compareData: function(uniqueId) {
            return (this._data.uniqueId === uniqueId);
        },

        equals: function (context) {
            return (context instanceof ChatContext) && (this.compareData(context._data.uniqueId));
        },
    };

    /****************************************************/
    /* Definition of object `ChatContextManager` */
    /* This guy plays an role of `proxy` in the system. */
    /****************************************************/

    var ChatContextManager = chatContextManager = (function () {
        var _contextList = {}, currentContext = null, currentSidebar = null;

        function getBySidebar (userCase, discussionCase) {
            return (currentSidebar === $userContactList) ? userCase : discussionCase;
        }

        return {
            /**
             * Load sidebar data
             */
            loadSidebar: function () {
                var self = this;

                function arrayToObject(data, results) {
                    $(data).each(function(){
                        results[this.uniqueId] = this;
                    });
                    return results;
                }

                function preprocess (data) {
                    preprocessData(data);
                    data.display_name = (data.type === 'user' ? data.nickname : data.name).toLowerCase();
                    data.pinyin = pinyin.getFullChars(data.display_name);
                    data.pinyin_camel = pinyin.getCamelChars(data.display_name).toLowerCase();
                }

                function loadData(api, template, $container, list) {
                    return api.get().ok(function(data){
                        $.renderAndInsert({
                            $container: $container,
                            template: template,
                            data: data.results,
                            preprocessor: preprocess
                        });

                        $.extend(list, arrayToObject(data.results, list));
                    });
                }

                $.when(
                    loadData(apiUsers, templates.user, $userList, dataList),
                    loadData(apiDiscussions, templates.discussion, $discussionList, dataList)
                ).done(function () {
                    self.loadUnread();
                    self.activate(chatWithUniqueId);
                })
            },

            bindSidebarEvents: function () {
                var self = this;

                $('#userContactList, #discussionContactList').on('click', 'a', function(){
                    var $this = $(this), context = self.activate($this.data('id'));
                });
            },

            /**
             * What to do when a context wants to be activated.
             * @param  {string|ChatContext} context The context to be activated.
             * @return {context}    
             */
            activate: function (context) {
                if (context) CHAT.toggle();

                currentContext && currentContext.deactivate();

                context = (context !== null) && this.getContext(context, true);
                context && context.activate();
                if (context && context.equals(this._contextToCheck)) CHAT.hideInfo();
                currentContext = context;

                return context;
            },

            /**
             * What to do when a message is received.
             * @param  {object} message The message data received.
             * @return {void}         
             */
            _handleMessage: function (message) {
                var context;

                context = this.getContext(message.uniqueId, true);
                context.handleMessage(message);

                if (context.equals(currentContext)) return;

                this._info(message, context);
            },

            _info: function (message, context) {

                function generateTips (message) {
                    return '{sender.nickname}: {content}'.render(message);
                }

                this._contextToCheck = context;
                CHAT.showInfo(generateTips(message));
            },

            handleMessage: function (message) {
                var self = this;

                Message.processMessage(message);

                if (message.results || $.isArray(message)) {
                    $(message.results || message).each(function () {
                        self._handleMessage(this);
                    });
                } else {
                    this._handleMessage(message);
                }
            },

            checkMessage: function (message) {
                this.activate(this._contextToCheck);
            },

            search: function (val, $container) {
                if (this.processingSearch) return;

                var results = {},
                    listItems = $("li", $container).get();
                this.processingSearch = true;
                val = val.toLowerCase();

                for (var uniqueId in dataList) {
                    var item = dataList[uniqueId];
                    results[uniqueId] = Math.max(
                        compare(item.display_name, val),
                        compare(item.pinyin, val),
                        compare(item.pinyin_camel, val)
                    );
                }

                listItems.sort(function (a, b) {
                    return results[$('a', b).data('id')]-results[$('a', a).data('id')];;
                });

                $container.html('');
                $(listItems).each(function () {
                    $(this).appendTo($container);
                });

                this.processingSearch = false;
            },

            /**
             * Initialize some global variables.
             * @return {void}
             */
            initialize: function () {
                var self = this;

                channel.events.on('channel.message', function (e, message) {
                    self.handleMessage(message);
                });

                templates = {
                    user: $.getScript("chatUserTemplate"),
                    message: $.getScript("chatMessageTemplate"),
                    discussion: $.getScript("chatDiscussionTemplate"),
                    attachment: $.getScript("chatAttachmentTemplate")
                },  $userList = $(".userList"),
                    $discussionList = $(".discussionList"),
                    $userContactList = $("#userContactList"),
                    $discussionContactList = $("#discussionContactList"),
                    $contentContainerDiv = $("#contentContainer").autoHeight(),
                    $contentContainer = $("ul", $contentContainerDiv),
                    $contentParent = $("#contentContainer")[0],
                    $chatWriteForm = $("#chatWriteForm"),
                    $chatWindow = $("#chatWindow"),
                    $sideBar = $("#sideBar"),
                    $infoMessage = $("#info-message"),
                    $infoMessageText = $("#info-message-text"),
                    $more = $("#more"),
                    currentSidebar = $userContactList;

                this.bindSidebarEvents();

                $('span.icon-a', '#userContactList, #discussionContactList').on('click', function(){
                    $("#userContactList, #discussionContactList").toggleClass('hidden');
                    currentSidebar = $userContactList.hasClass('hidden') ? $discussionContactList : $userContactList
                });

                $("#back-to-sidebar").on('click', function () {
                    CHAT.toggle();
                });

                $("div.search input").on("keyup change", function () {
                    var $this = $(this), val = $this.val(), 
                        $sidebarShow = $("ul.show", currentSidebar),
                        $sidebarModel = $("ul.model", currentSidebar);

                    if (!val) {
                        $sidebarShow.removeClass('hidden');
                        $sidebarModel.addClass('hidden');
                        return;
                    } else {
                        $sidebarShow.addClass('hidden');
                        $sidebarModel.removeClass('hidden');
                    }

                    setTimeout(function () {
                        self.search(val, $sidebarModel);
                    }, 0);
                });

                $("#load-history").on('click', function () {
                    currentContext.loadHistory();
                });

                $('textarea', $chatWriteForm).on('flex-text', function () {
                    $contentContainerDiv.trigger('adjust-height');
                });

                $('#close-message').on('click', function () {
                    CHAT.hideInfo();
                });

                $('#check-message').on('click', function () {
                    self.checkMessage();
                    CHAT.hideInfo();
                });

                $contentContainerDiv.on('mousewheel', function (e) {
                    if (e.originalEvent.wheelDelta <= 0) return;
                    if ($(this).scrollTop() === 0) currentContext && currentContext.loadHistory();
                }).on('scroll', function (e) {
                    if ($(this).scrollTop() === 0) currentContext && currentContext.loadHistory();
                });

                $chatWriteForm.on('submit', $.wrapEventHandler(this, this.writeFormCallback));

                this.loadSidebar();

                $window.on('resize', function () {
                    $contentContainerDiv.trigger('adjust-height');
                });

                this.processingSearch = false;
                this.submitting = false;
            },

            /**
             * To get a context.
             * @param  {object|ChatContext} context A `ChatContext` instance or the `uniqueId`.
             * @param {bool} open Whether to open a new context when doesnt exist.
             * @return {ChatContext}         The `ChatContext` object found.
             */
            getContext: function (context, open) {
                var returnContext;

                if (!(context instanceof ChatContext)) {
                    returnContext = _contextList[context] || null;
                } else {
                    returnContext = context;
                }

                if (!returnContext && open) {
                    returnContext = this.openContext(context);
                }

                return returnContext;
            },

            /**
             * Create a new context.
             * @param  {string|object} data The `uniqueId` or the context data.
             * @return {ChatContext}      The context created.
             */
            openContext: function (data) {
                if (typeof data === 'string') {
                    data = dataList[data] || {};
                }

                if (!data.uniqueId) return null;

                return _contextList[data.uniqueId] = new ChatContext(data);
            },

            loadUnread: function () {
                var uniqueId, self = this;

                API.url('unread').get().ok(function (data) {
                    for (uniqueId in data) {
                        var context = self.getContext(uniqueId, true);
                        context && context.setUnread(data[uniqueId]);
                    }
                });
            },

            /**
             * The callback function for write form submission.
             * @param  {Event} e The Event object received.
             * @return {void}
             */
            writeFormCallback: function (e) {
                e.preventDefault();

                if (this.submitting) return;
                this.submitting = true;

                var data = $chatWriteForm.serializeObject(), self = this;
                if (data.attachments&&!$.isArray(data.attachments)) data.attachments = [data.attachments];
                $.extend(data, {
                    sender: userid
                });

                currentContext._API.post(data).ok(function (data) {
                    $chatWriteForm.data("postSuccess")();
                    $contentContainerDiv.trigger('adjust-height');
                    self.handleMessage(data);
                }).always(function () {
                    self.submitting = false;
                });
            }
        };
    })();

    $(function(){
        chatContextManager.initialize();
    });
})(jQuery, window);
