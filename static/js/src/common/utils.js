(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['jquery'], factory);
    } else if (typeof exports === 'object') {
        // CommonJS
        factory(require('jquery'));
    } else {
        // Browser globals
        factory(jQuery);
    }
}(function ($) {

    var pluses = /\+/g;

    function encode(s) {
        return config.raw ? s : encodeURIComponent(s);
    }

    function decode(s) {
        return config.raw ? s : decodeURIComponent(s);
    }

    function stringifyCookieValue(value) {
        return encode(config.json ? JSON.stringify(value) : String(value));
    }

    function parseCookieValue(s) {
        if (s.indexOf('"') === 0) {
            // This is a quoted cookie as according to RFC2068, unescape...
            s = s.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, '\\');
        }

        try {
            // Replace server-side written pluses with spaces.
            // If we can't decode the cookie, ignore it, it's unusable.
            // If we can't parse the cookie, ignore it, it's unusable.
            s = decodeURIComponent(s.replace(pluses, ' '));
            return config.json ? JSON.parse(s) : s;
        } catch(e) {}
    }

    function read(s, converter) {
        var value = config.raw ? s : parseCookieValue(s);
        return $.isFunction(converter) ? converter(value) : value;
    }

    var config = $.cookie = function (key, value, options) {

        // Write

        if (value !== undefined && !$.isFunction(value)) {
            options = $.extend({}, config.defaults, options);

            if (typeof options.expires === 'number') {
                var days = options.expires, t = options.expires = new Date();
                t.setTime(+t + days * 864e+5);
            }

            return (document.cookie = [
                encode(key), '=', stringifyCookieValue(value),
                options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
                options.path    ? '; path=' + options.path : '',
                options.domain  ? '; domain=' + options.domain : '',
                options.secure  ? '; secure' : ''
            ].join(''));
        }

        // Read

        var result = key ? undefined : {};

        // To prevent the for loop in the first place assign an empty array
        // in case there are no cookies at all. Also prevents odd result when
        // calling $.cookie().
        var cookies = document.cookie ? document.cookie.split('; ') : [];

        for (var i = 0, l = cookies.length; i < l; i++) {
            var parts = cookies[i].split('=');
            var name = decode(parts.shift());
            var cookie = parts.join('=');

            if (key && key === name) {
                // If second argument (value) is a function it's a converter...
                result = read(cookie, value);
                break;
            }

            // Prevent storing a cookie that we couldn't decode.
            if (!key && (cookie = read(cookie)) !== undefined) {
                result[name] = cookie;
            }
        }

        return result;
    };

    config.defaults = {};

    $.removeCookie = function (key, options) {
        if ($.cookie(key) === undefined) {
            return false;
        }

        // Must not alter options, thus extending a fresh object...
        $.cookie(key, '', $.extend({}, options, { expires: -1 }));
        return !$.cookie(key);
    };

}));

(function () {
    'use strict';

    if (typeof window.JSON !== 'object') {
        window.JSON = {};
    }

    function f(n) {
        // Format integers to have at least two digits.
        return n < 10 ? '0' + n : n;
    }

    if (typeof Date.prototype.toJSON !== 'function') {

        Date.prototype.toJSON = function () {

            return isFinite(this.valueOf())
                ? this.getUTCFullYear()     + '-' +
                    f(this.getUTCMonth() + 1) + '-' +
                    f(this.getUTCDate())      + 'T' +
                    f(this.getUTCHours())     + ':' +
                    f(this.getUTCMinutes())   + ':' +
                    f(this.getUTCSeconds())   + 'Z'
                : null;
        };

        String.prototype.toJSON      =
            Number.prototype.toJSON  =
            Boolean.prototype.toJSON = function () {
                return this.valueOf();
            };
    }

    var cx,
        escapable,
        gap,
        indent,
        meta,
        rep;


    function quote(string) {

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe escape
// sequences.

        escapable.lastIndex = 0;
        return escapable.test(string) ? '"' + string.replace(escapable, function (a) {
            var c = meta[a];
            return typeof c === 'string'
                ? c
                : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
        }) + '"' : '"' + string + '"';
    }


    function str(key, holder) {

// Produce a string from holder[key].

        var i,          // The loop counter.
            k,          // The member key.
            v,          // The member value.
            length,
            mind = gap,
            partial,
            value = holder[key];

// If the value has a toJSON method, call it to obtain a replacement value.

        if (value && typeof value === 'object' &&
                typeof value.toJSON === 'function') {
            value = value.toJSON(key);
        }

// If we were called with a replacer function, then call the replacer to
// obtain a replacement value.

        if (typeof rep === 'function') {
            value = rep.call(holder, key, value);
        }

// What happens next depends on the value's type.

        switch (typeof value) {
        case 'string':
            return quote(value);

        case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

            return isFinite(value) ? String(value) : 'null';

        case 'boolean':
        case 'null':

// If the value is a boolean or null, convert it to a string. Note:
// typeof null does not produce 'null'. The case is included here in
// the remote chance that this gets fixed someday.

            return String(value);

// If the type is 'object', we might be dealing with an object or an array or
// null.

        case 'object':

// Due to a specification blunder in ECMAScript, typeof null is 'object',
// so watch out for that case.

            if (!value) {
                return 'null';
            }

// Make an array to hold the partial results of stringifying this object value.

            gap += indent;
            partial = [];

// Is the value an array?

            if (Object.prototype.toString.apply(value) === '[object Array]') {

// The value is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                length = value.length;
                for (i = 0; i < length; i += 1) {
                    partial[i] = str(i, value) || 'null';
                }

// Join all of the elements together, separated with commas, and wrap them in
// brackets.

                v = partial.length === 0
                    ? '[]'
                    : gap
                    ? '[\n' + gap + partial.join(',\n' + gap) + '\n' + mind + ']'
                    : '[' + partial.join(',') + ']';
                gap = mind;
                return v;
            }

// If the replacer is an array, use it to select the members to be stringified.

            if (rep && typeof rep === 'object') {
                length = rep.length;
                for (i = 0; i < length; i += 1) {
                    if (typeof rep[i] === 'string') {
                        k = rep[i];
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            } else {

// Otherwise, iterate through all of the keys in the object.

                for (k in value) {
                    if (Object.prototype.hasOwnProperty.call(value, k)) {
                        v = str(k, value);
                        if (v) {
                            partial.push(quote(k) + (gap ? ': ' : ':') + v);
                        }
                    }
                }
            }

// Join all of the member texts together, separated with commas,
// and wrap them in braces.

            v = partial.length === 0
                ? '{}'
                : gap
                ? '{\n' + gap + partial.join(',\n' + gap) + '\n' + mind + '}'
                : '{' + partial.join(',') + '}';
            gap = mind;
            return v;
        }
    }

// If the JSON object does not yet have a stringify method, give it one.

    if (typeof JSON.stringify !== 'function') {
        escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;
        meta = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        };
        JSON.stringify = function (value, replacer, space) {

// The stringify method takes a value and an optional replacer, and an optional
// space parameter, and returns a JSON text. The replacer can be a function
// that can replace values, or an array of strings that will select the keys.
// A default replacer method can be provided. Use of the space parameter can
// produce text that is more easily readable.

            var i;
            gap = '';
            indent = '';

// If the space parameter is a number, make an indent string containing that
// many spaces.

            if (typeof space === 'number') {
                for (i = 0; i < space; i += 1) {
                    indent += ' ';
                }

// If the space parameter is a string, it will be used as the indent string.

            } else if (typeof space === 'string') {
                indent = space;
            }

// If there is a replacer, it must be a function or an array.
// Otherwise, throw an error.

            rep = replacer;
            if (replacer && typeof replacer !== 'function' &&
                    (typeof replacer !== 'object' ||
                    typeof replacer.length !== 'number')) {
                throw new Error('JSON.stringify');
            }

// Make a fake root object containing our value under the key of ''.
// Return the result of stringifying the value.

            return str('', {'': value});
        };
    }


// If the JSON object does not yet have a parse method, give it one.

    if (typeof JSON.parse !== 'function') {
        cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;
        JSON.parse = function (text, reviver) {

// The parse method takes a text and an optional reviver function, and returns
// a JavaScript value if the text is a valid JSON text.

            var j;

            function walk(holder, key) {

// The walk method is used to recursively walk the resulting structure so
// that modifications can be made.

                var k, v, value = holder[key];
                if (value && typeof value === 'object') {
                    for (k in value) {
                        if (Object.prototype.hasOwnProperty.call(value, k)) {
                            v = walk(value, k);
                            if (v !== undefined) {
                                value[k] = v;
                            } else {
                                delete value[k];
                            }
                        }
                    }
                }
                return reviver.call(holder, key, value);
            }


// Parsing happens in four stages. In the first stage, we replace certain
// Unicode characters with escape sequences. JavaScript handles many characters
// incorrectly, either silently deleting them, or treating them as line endings.

            text = String(text);
            cx.lastIndex = 0;
            if (cx.test(text)) {
                text = text.replace(cx, function (a) {
                    return '\\u' +
                        ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
                });
            }

// In the second stage, we run the text against regular expressions that look
// for non-JSON patterns. We are especially concerned with '()' and 'new'
// because they can cause invocation, and '=' because it can cause mutation.
// But just to be safe, we want to reject all unexpected forms.

// We split the second stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace the JSON backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

            if (/^[\],:{}\s]*$/
                    .test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, '@')
                        .replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']')
                        .replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the third stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                j = eval('(' + text + ')');

// In the optional fourth stage, we recursively walk the new structure, passing
// each name/value pair to a reviver function for possible transformation.

                return typeof reviver === 'function'
                    ? walk({'': j}, '')
                    : j;
            }

// If the text is not JSON parseable, then a SyntaxError is thrown.

            throw new SyntaxError('JSON.parse');
        };
    }
}());

(function ($, window, undefined) {

    /**
     * Provides a simple template method.
     */
    String.prototype.render = function (context) {
        if (context === undefined) return this;

        var token = /\{([\w\.]+)\}/g;
        return this.replace(token, function (word) {
            var words = word.slice(1,-1).split('.'), obj = context;

            for (var i = 0,l = words.length; i < l; i++) {
                obj = obj[words[i]];
                if (obj === undefined || obj === null) return '';
            }

            return obj;
        });
    };

    Array.prototype.indexOf = Array.prototype.indexOf || function (item) {
        var i, l;
        for (i = 0, l = this.length; i<l; i++)
            if (item === this[i]) return i;
        return -1;
    };

    Array.prototype.remove = Array.prototype.remove || function (item) {
        var pos = this.indexOf(item);
        if (pos < 0) return this;
        this.splice(pos, 1);
        return this;
    };

    $.extend({
            
        //debug: window.location.origin.indexOf('localhost') >= 0,
        
        encodeJSON: window.JSON.stringify,

        decodeJSON: window.JSON.parse,

        emptyFunc: function (_) {
            return _;
        },

        autoInvokeFunc: function (f) {
            f();
            return this;
        },

        getUrlParam: function (name) {
            var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)"),
                r = window.location.search.substr(1).match(reg);
            return (r!==null ? unescape(r[2]) : null);
        },

        getAnchor: function () {
            return window.location.hash;
        },

        isCtrlEnter: function (e) {
            if (!(e.which)) {
                if (e.data) {
                    e = e.data.$;
                } else {
                    return false;
                }
            }
            return (e.which === 13 || e.which === 10) && e.ctrlKey;
        },

        argumentsToArray: function (args) {
            return Array.apply(null, args);
        },

        wrapEventHandler: function (context, handler) {
            return function () {
                handler.apply(context, $.argumentsToArray(arguments));
            };
        },

        jump: function (url) {
            window.location.href = url;
        },


        getScript: function (id) {
            return $("#"+id).html();
        },

        showHtml: function (html, callback) {
            $(html).show('slow', callback || $.emptyFunc);
        },

        renderAndInsert: function (config, callback) {
            var CONFIG = {
                preprocessor: $.emptyFunc,
                operation: "prepend"
            }, callback = callback || $.emptyFunc;

            $.extend(CONFIG, config);
            var template = CONFIG.template || $.getScript(CONFIG.templateId),
                $container = (typeof CONFIG.$container === 'string'?$(CONFIG.$container):CONFIG.$container);

            function renderTemplate(data,i) {
                CONFIG.preprocessor(data,i);
                return template.render(data);
            }

            function insert(html) {
                if (!html) {
                    callback();
                    return;
                }

                html = $(html);
                if (CONFIG.operation === 'clear') $container.html("");
                if (CONFIG.operation === 'append') 
                    html.appendTo($container);
                else
                    html.prependTo($container);
                $.showHtml(html, callback);
                return html;
            }

            if ($.isArray(CONFIG.data)) {
                var html = [];
                $(CONFIG.data).each(function(i){
                    html.push(renderTemplate(this, i));
                });
                return insert(html.join(''));
            } else {
                return insert(renderTemplate(CONFIG.data));
            }
        },

        getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        closeWindow: function () {
            window.opener = null;
            window.close();
        }
    });

    $.fn.extend({

        serializeObject: function () {
            var o={}, a = this.serializeArray();
            $.each(a, function () {
                var value=this.hasOwnProperty('value')?this.value:'';
                if ($.isArray(o[this.name])) {
                    o[this.name].push(value)
                } else 
                    (o[this.name]===undefined)?o[this.name]=value:o[this.name]=[o[this.name],value];
            });
            return o;
        },

        error: function () {
            var $this = $(this);
            $this
                .addClass('blank')
                .one('keypress', function () {
                    $(this).removeClass('blank');
                })
                .focus();
        },

        clearForm: function() {
            var a=$(this);
            a.find('input,textarea')
             .not(':button, :submit, :reset, :hidden')  
             .val('')  
             .removeAttr('checked')  
             .removeAttr('selected');
        },

        flexText: function (maxHeight) {

            function autoHeight (editor) {
                $(editor).css({'height':'auto','overflow-y':'hidden'}).height(editor.scrollHeight);
            }

            if (!this.is('textarea')) return;

            $(this).on('input propertychange keyup change', function () {
                if ($.isNumeric(maxHeight)
                    && this.scrollHeight > maxHeight 
                    && this.scrollHeight > $(this).height()+15) return;
                autoHeight(this);
                $(this).trigger('flex-text');
            });
        },

        autoHeight: function (min) {

            function adjust ($element) {
                var sum = 0, height;

                $element.siblings().not(':hidden').each(function () {
                    sum += $(this).outerHeight();
                });

                height = $element.parent().outerHeight() - sum;
                if (height < min) height = min;

                $element.height(height);
            }

            min = min || 0;
            this.on('adjust-height', function () {
                adjust($(this));
            });

            return this;
        }
    });

    $(function(){
        $('form').each(function(){
            var $form = $(this);
            $('textarea', $form).on('keypress', function(e){
                if ($.isCtrlEnter(e))
                    $form.submit();
            });
        });

        $('body').on('click', '.btn-close', function () {
            if (confirm('Are you sure to quit?'))
                $.closeWindow();
        });
    });
})(jQuery, window);