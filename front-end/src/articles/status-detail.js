(function (){

$(function(){
    var commentConfig = {
            templateId: "commentTemplate",
            $container: $("#commentContainer"),
            api: statusAPI.url('comments'),
            listType: "waterfall"
        },
        commentList = LIST.createList(commentConfig), submitting = false;

    $("#commentForm").on('submit', function(e) {
        if (submitting) return;

        submitting = true;
        var $this = $(this), data = $this.serializeObject();
        if (!data.body_text) {
            $('textarea', $this).popover();
            return false;
        }
        statusAPI.url('comments').bindElements($("input[type='submit']", $this))
            .post(data).ok(function(data){
                commentList.loadPrevious();
            })
            .always(function () {
                submitting = false;
                $this.clearForm();
            });
    });
});
})();
