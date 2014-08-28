(function() {

    $( document ).ready(function() {

        var FIELD_TYPES = {
            0: 'TEXT',
            1: 'TEXTAREA',
            2: 'EMAIL',
            3: 'NUMBER',
            4: 'URL',
            5: 'CHECKBOX',
            6: 'CHECKBOX_MULTIPLE',
            7: 'SELECT',
            8: 'SELECT_MULTIPLE',
            9: 'RADIO_MULTIPLE',
            10: 'FILE',
            11: 'DATE',
            12: 'DATE_TIME',
            13: 'DOB',
            14: 'HIDDEN'
        };

        var $form = $($.find('form'));
        var $formRestrictions = jQuery.parseJSON(formRestrictions);

        initActions($form, $formRestrictions);





//    //    console.log($formRestrictions);
//        $.each($formRestrictions, function(index, value) {
////            console.log(index, value);
//            var maxExceeds = getFieldExceedingMaxAvailable(index, value);
////            console.log(maxExceeds);
//    //        var $field = $form.find('');
//        });

    });

    function initActions($form, $formRestrictions) {
            var warningData = getWarningMessagesData($formRestrictions);
            displayWarningMessages($form, warningData);
        }

    function getWarningMessagesData($formRestrictions) {
        var warningData = [];

        $.each($formRestrictions, function(index, value) {
            var maxExceeds = getFieldExceedingMaxAvailable(index, value);
            warningData.push(maxExceeds);
        });

        return warningData;
    }

    function getFieldExceedingMaxAvailable(index, value) {
        var maxExceeds = {};
        $.each(value, function(k, v) {
            if (v.sent >= v.max) {
                maxExceeds[index] = {name:k, value:v};
//                console.log('przekroczono max');
//                console.log(k);
//                console.log(v);
//                console.log(index);
//                console.log(value);
            }
            else {
//                console.log('jest jeszze miejsce');
            }
        });
        console.log(maxExceeds);
        return maxExceeds;
    }

    function displayWarningMessages($form, warningData) {
//        console.log(warningData);
        for (var i = 0; i < warningData.length; i++) {
//            console.log('co tu?');
//            console.log(warningData[i]);
            for (var key in warningData[i]) {
//                console.log(key);
//                console.log(warningData[i][key].name);
                for (var group in warningData[i][key]) {}
//                    console.log(warningData[i][key][group]);
//                $('body').find('.form-warnings').append('<p class="warning">Dla pola ' + key + ' wyczerpany został limit miejsc w grupach: ' + warningData[i][key].name + '</p>');
            }
        }
    }

})();



