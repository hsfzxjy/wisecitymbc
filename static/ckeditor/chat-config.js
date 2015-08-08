CKEDITOR.editorConfig = function( config ) {
    config.toolbarGroups = [];
    config.removeButtons = 'Scayt,SpellChecker,Maximize,Image,Styles,Underline,Subscript,Superscript';
    config.extraPlugins = 'colorbutton,font';
    config.removePlugins = 'elementspath';
    config.resize_enabled = false;
    config.format_tags = 'p;h1;h2;h3;pre';
    config.removeDialogTabs = 'image:advanced;link:advanced';
    config.height = "100px";
};
