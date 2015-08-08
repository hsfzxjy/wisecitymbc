CKEDITOR.plugins.add('img', {
	init: function(editor){
		var config = editor.config.upload, fileId=config.fileId, formId=config.formId, queueId = config.queueId, $file=$("#"+fileId), $queue=$("#"+queueId), $form=$("#"+formId), callback = config.callback||function(){}, progress = config.progress||function(){};
		//$form.hide();
		$form.fileupload({
			url: "/api/files/public/",
			autoUpload: true,
			dataType: 'json',
			formAcceptCharset: "unicode",
			done: function (e, xhr) {
				var data = xhr.result, 
				insertion=/^.+\.(jpg|gif|png)$/i.test(data.name)?"<img src='{url}' />":"<a href='{url}'>{name}</a>"; //判断图片
				editor.insertHtml(insertion.replace('{url}', data.url).replace('{name}', data.name));
				callback(data);
				$file.val("");
			},
			progressall: function(e, data) {
				var p=parseInt(data.loaded / data.total * 5, 10);
				progress(p);
			}
		});
		$(file).change(function(){
			$form.fileupload("send");
			console.log(1);
		});
		editor.addCommand( 'img',
		{
			exec : function(editor)
			{
				return $file.click();
				$file.change();
			}
		});
	editor.ui.addButton('img',
		{
			label: '图片/文件',
			command: 'img',
			icon: this.path + 'icon.png'
		} );
	},
	onLoad:function(){}
});
