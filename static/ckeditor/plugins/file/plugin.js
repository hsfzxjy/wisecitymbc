CKEDITOR.plugins.add('file', {
	init: function(editor){
		var config = editor.config.upload, fileId=config.fileId, formId=config.formId, queueId = config.queueId, $file=$("#"+fileId), $queue=$("#"+queueId), $form=$("#"+formId), insertion="<a href='{url}'>{name}</a>", callback = config.callback||function(){};
		$form.hide();
		$form.fileupload({
			url: "/api/files/public/",
			autoUpload: true,
			dataType: 'json',
			formAcceptCharset: "unicode",
			done: function (e, xhr) {
				var data = xhr.result;
				editor.insertHtml(window.uploadInsertion.replace('{url}', data.url).replace('{name}', data.name));
				callback(data);
				$form.hide();
			}
		});
		editor.addCommand( 'file',
		{
			exec : function( editor )
			{    
				window.uploadInsertion=insertion;
				$form.show();
			}
		});
	editor.ui.addButton( 'file',
		{
			label: '文件',
			command: 'file',
			icon: this.path + 'icon.png'
		} );
	},
	onLoad:function(){}
});
