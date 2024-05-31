$(document).ready(function() {

    $('#studentRequestForm').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/student_request',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    $('#studentRequestModal').modal('hide');
                    $('#successModal').modal('show');
                } else {
                    $('#studentRequestModal').modal('hide');
                    $('#failureModal').modal('show');
                }
            },
            error: function() {
                $('#studentRequestModal').modal('hide');
                $('#failureModal').modal('show');
            }
        });
    });

    $('#featureRequestForm').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/feature_request',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    $('#featureRequestModal').modal('hide');
                    $('#successModal').modal('show');
                } else {
                    $('#featureRequestModal').modal('hide');
                    $('#failureModal').modal('show');
                }
            },
            error: function() {
                $('#featureRequestModal').modal('hide');
                $('#failureModal').modal('show');
            }
        });
    });

    $('#reserveRoomForm').on('submit', function (e) {
        e.preventDefault();
        const startHour = $('#startTimeHour').val();
        const startMinute = $('#startTimeMinute').val();
        const endHour = $('#endTimeHour').val();
        const endMinute = $('#endTimeMinute').val();
    
        // Perform any validation or AJAX request here
    
        console.log(`Start Time: ${startHour}:${startMinute}`);
        console.log(`End Time: ${endHour}:${endMinute}`);
    
        // For example, show success modal after form submission
        $('#reserveRoomModal').modal('hide');
        $('#successModal').modal('show');
      });

    $.getJSON('/list_features', function (data) {
    const featureDropdown = $('#existingFeatures');
    data.features.forEach(function (feature) {
        featureDropdown.append(
        `<option value="${feature.feature_id}">${feature.name}</option>`
        );
    });
    });

    // Show/hide the feature input field based on the selected option
    $('#existingFeatures').on('change', function () {
    const selectedValue = $(this).val();
    if (selectedValue === 'other') {
        $('#newFeatureGroup').show();
        $('#feature').prop('required', true);
    } else {
        $('#newFeatureGroup').hide();
        $('#feature').prop('required', false);
    }
    });
      // Add the script to show/hide the End Date field
    const repeatDropdown = $('#eventRepeat');
    const endDateGroup = $('#endDateGroup');

    repeatDropdown.on('change', function() {
        if (repeatDropdown.val() === 'today') {
            endDateGroup.hide();
        } else {
            endDateGroup.show();
        }
    });
});
