(function() {

    $( document ).ready(function() {

        FIELD_TYPES = {
            1: 'TEXT',
            2: 'TEXTAREA',
            3: 'EMAIL',
            4: 'CHECKBOX',
            5: 'CHECKBOX_MULTIPLE',
            6: 'SELECT',
            7: 'SELECT_MULTIPLE',
            8: 'RADIO_MULTIPLE',
            9: 'FILE',
            10: 'DATE',
            11: 'DATE_TIME',
            12: 'HIDDEN',
            13: 'NUMBER',
            14: 'URL',
            15: 'DOB'
        };

        var $form = $($.find('form'));
        var $formWarnings = $.parseJSON(formWarnings);
        var $formRestrictions = $.parseJSON(formRestrictions);

        initActions($form, $formWarnings, $formRestrictions);

    });

    function initActions($form, $formWarnings, $formRestrictions) {
        assignFormWarningsToField($form, $formWarnings);
        hideReserveButton($form);
        displayWarningMessages($form, $formWarnings);
    }

    function assignFormWarningsToField($form, $formWarnings) {
        $form.find('#id_form_warnings').val($formWarnings);
    }

    function hideReserveButton($form) {
        $form.find('#id_reserve').parent().hide();
    }

    function displayWarningMessages($form, warningData) {
        if (!$.isEmptyObject(warningData)) {
            for (var question in warningData) {
                var answers = [];
                for (var option in warningData[question]) {
                    for (var key in warningData[question][option])
                        answers.push(key);
                }
                if (answers.length > 0)
                    $form.parent().find('div.form-warnings').append("W pytaniu: '" + question + "' opcje odpowiedzi: '" + answers.join(", ") + "' osiągnęły już maksymalną liczbę zgłoszeń.\n");
            }
            if (answers.length > 0)
                $form.parent().find('div.form-warnings').append("Wciąż możesz zapisać się do grup, które osiągnęły swój limit zgłoszeń. Trafisz wtedy na listę rezerwową.");
        } else {
          return false;
        }
    }

})();



