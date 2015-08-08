CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [
        { name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
        { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
        { name: 'forms'},
        { name: 'tools'},
        { name: 'insert'},
        { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
        { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
        //{ name: 'styles' , items: ['Format']},
        { name: 'colors' },
        { name: 'font'}
    ];
    config.removeButtons = 'Scayt,SpellChecker,Maximize,Image,Styles';
    config.extraPlugins = 'colorbutton,font';
    config.removePlugins = 'elementspath';
    config.resize_enabled = false;
    config.format_tags = 'p;h1;h2;h3;pre';
    config.removeDialogTabs = 'image:advanced;link:advanced';
    config.allowedContent = true;
    config.bodyClass = 'ckeditor-body';
};
