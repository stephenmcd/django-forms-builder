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
        monitorChangesOfFieldsToSetReservedTrue($form, $formWarnings, $formRestrictions);
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
                $form.parent().find('div.form-warnings').append("W pytaniu: '" + question + "' opcje odpowiedzi: '" + answers.join(", ") + "' osiągnęły już maksymalną liczbę zgłoszeń.\n");
            }
            $form.parent().find('div.form-warnings').append("Wciąż możesz zapisać się do grup, które osiągnęły swój limit zgłoszeń. Trafisz wtedy na listę rezerwową.");
        } else {
          return false;
        }
    }

    function monitorChangesOfFieldsToSetReservedTrue($form, warningData, $formRestrictions) {
        for (var key in warningData) {
            var fieldID = "id_" + normalizeString(key);
            var fieldType = getFieldType(key, $formRestrictions);
            console.log(fieldType);
            findFormFieldAndSetMonitoring($form, warningData, fieldID, fieldType, key);
        }
    }

    function getFieldType(fieldName, $formRestrictions) {
        return $formRestrictions[fieldName]['field_type'];
    }

    function normalizeString(s){
        var r = s.toLowerCase();
        r = r.replace(/À|Á|Â|Ã|Ä|Å|Ą/g, "A");
        r = r.replace(/à|á|â|ã|ä|å|ą/g, "a");
        r = r.replace(/Ò|Ó|Ô|Õ|Õ|Ö|Ø|Ó/g, "O");
        r = r.replace(/ò|ó|ô|õ|ö|ø|ó/g, "o");
        r = r.replace(/È|É|Ê|Ë|Ę/g, "E");
        r = r.replace(/è|é|ê|ë|ę/g, "e");
        r = r.replace(/Ç|ç|Ć|ć/g, "c");
        r = r.replace(/Ì|Í|Î|Ï/g, "I");
        r = r.replace(/ì|í|î|ï/g, "i");
        r = r.replace(/Ù|Ú|Û|Ü/g, "U");
        r = r.replace(/ù|ú|û|ü/g, "u");
        r = r.replace(/Ź|ź|Ż|ż/g, "z");
        r = r.replace(/Ś|ś/g, "s");
        r = r.replace(/Ł|ł/g, "l");
        r = r.replace(/Ń|ń/g, "n");
        return r;
    }

    function findFormFieldAndSetMonitoring($form, warningData, fieldID, fieldType, key) {
        var $reserveField = $form.find('#id_reserve');
        if (FIELD_TYPES[fieldType] == "RADIO_MULTIPLE") {
            $form.find('ul#'+fieldID+'').on('change', function(event) {
                var checkedOption = $(event.target).val();
                for (var i = 0; i < warningData[key].length; i++) {
                    if (warningData[key][i].hasOwnProperty(checkedOption)) {
                        $reserveField.attr('checked', true);
                    } else {
                        $reserveField.attr('checked', false);
                    }
                }
//                if (warningData[key].hasOwnProperty("Kobieta")) {
//                    console.log('true');
//                }
            });
//            console.log("RADIO_MULTIPLE");
        }
    }


})();



