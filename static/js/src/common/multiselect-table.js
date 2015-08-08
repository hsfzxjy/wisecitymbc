;(function ($, window, undefined) {

    $.fn.extend({
        multiselect: function (config) {
            function changeState (checkbox, checked) {
                var id = $(checkbox).parent().parent().data("id"), oldState = (selectedItems.length);
                checkbox.checked = checked;

                if (checked) {
                    selectedItems.push(id);
                    if (!oldState) 
                        $relatedButtons.trigger("check", true);
                } else {
                    selectedItems.remove(id);
                    if (oldState && !selectedItems.length) 
                        $relatedButtons.trigger("check", false);
                }
            }

            function getCheckboxes() {
                return $("tbody>tr>td>input[type='checkbox']", $table);
            }

            var selectedItems = [], 
                $table = $(this),
                $selectAll = $("thead>tr>td>input[type='checkbox']", $table),
                $relatedButtons = $();

            $selectAll.on('change', function () {
                var checked = this.checked;

                getCheckboxes().each(function () {
                    changeState(this, checked);
                });
            });

            this.clearSelect = function () {
                $selectAll.trigger("change", false);
                $relatedButtons.trigger("check", false);
            };

            $(config.relatedButtons).each(function () {
                var $this;

                $relatedButtons.push($this = $(this.toString()));
                $this.on("click", function () {
                    $(this).trigger("table.click", selectedItems);
                });
            });

            $relatedButtons
            .on("check", function (e, checked) {
                $(this).each(function () {
                    $(this).toggleClass("disabled", !checked);
                });
            });

            this.clearSelect();

            $table.on("change", "tbody>tr>td>input[type='checkbox']", function () {
                changeState(this, this.checked);
            });

            return $table;
        }
    });
})(jQuery, window);