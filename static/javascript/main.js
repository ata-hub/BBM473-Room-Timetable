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

    function resetFormFields() {
        $('#reserveRoomForm')[0].reset();
        $('#endDateGroup').hide(); // Hide the end date field
    }

    $('#reserveRoomForm').on('submit', function (e) {
        e.preventDefault();
        const day = $('#eventDate').val();
        let startHour = $('#startTimeHour').val();
        const startMinute = $('#startTimeMinute').val();
        let endHour = $('#endTimeHour').val();
        const endMinute = $('#endTimeMinute').val();
        const room = $('#room').val();
        const title = $('#eventTitle').val();
        const description = $('#eventDescription').val();
        const repeat = $('#eventRepeat').val();
        let endDate = null;

        if (startHour.toString().length == 1) {
            startHour = "0" + startHour.toString(); 
        }

        if (endHour.toString().length == 1) {
            endHour = "0" + endHour.toString(); 
        }

        const startTime = startHour + ":" + startMinute;
        const endTime = endHour + ":" + endMinute;

        if (repeat !== 'today') {
            endDate = $('#endReservationDate').val();
        }

        const requestData = {
            title: title,
            description: description,
            start_time: startTime,
            end_time: endTime,
            room: room,
            repeat: repeat,
            day: day,
            end_date: endDate
        };

        $.ajax({
            url: '/reservation',
            method: 'POST',
            data: requestData,
            success: function(response) {
                if (response.success) {
                    $('#reserveRoomModal').modal('hide');
                    $('#successModal').modal('show');
                    // Clear form fields
                    resetFormFields();
                    setTimeout(function() {
                        location.reload(); // Reload the page to refresh the table data
                    }, 2000); 
                } else if (response.message === "No suggestions") {
                    // Handle case where no suggestions are available
                    alert('No suggestions available.');
                } else if (response.suggestions) {
                    // Display the list of suggestions in a modal or section on the page
                    displaySuggestions(response.suggestions);
                } else {
                    // Handle other failure responses
                    alert(response.message);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.status === 400) {
                    try {
                        const response = JSON.parse(jqXHR.responseText);
                        if (response.suggestions) {
                            $('#reserveRoomModal').modal('hide');
                            displaySuggestions(response.suggestions);
                        } else {
                            $('#reserveRoomModal').modal('hide');
                            $('#failureModal').modal('show');
                            alert(response.message);
                        }
                    } catch (e) {
                        $('#reserveRoomModal').modal('hide');
                        $('#failureModal').modal('show');
                        alert('An error occurred. Please try again.');
                    }
                } else {
                    console.error('Error making reservation:', errorThrown);
                    $('#reserveRoomModal').modal('hide');
                    $('#failureModal').modal('show');
                    alert('An error occurred. Please try again.');
                }
            }
        });
    });

    // Function to display suggestions in a modal or a section
    function displaySuggestions(suggestions) {
        let suggestionsHtml = '<div class="modal fade" id="suggestionsModal" tabindex="-1" aria-labelledby="suggestionsModalLabel" aria-hidden="true"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="suggestionsModalLabel">Suggested Rooms</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div><div class="modal-body"><form id="suggestionsForm">';
        
        suggestions.forEach((suggestion, index) => {
            suggestionsHtml += `<div class="form-check">
                                    <input class="form-check-input" type="radio" name="suggestion" id="suggestion${index}" value="${suggestion.room_id}">
                                    <label class="form-check-label" for="suggestion${index}">
                                        ${suggestion.name} (Type: ${suggestion.type}, Capacity: ${suggestion.capacity})
                                    </label>
                                </div>`;
        });
        
        suggestionsHtml += '</form></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary" id="confirmSuggestion">Confirm</button></div></div></div></div>';
        
        // Append the modal to the body
        $('body').append(suggestionsHtml);
        
        // Show the modal
        $('#suggestionsModal').modal('show');

        // Add click event to suggestion items
        // Add click event to the confirm button
        $('#confirmSuggestion').on('click', function() {
            const selectedSuggestion = $('input[name="suggestion"]:checked').val();
            if (selectedSuggestion) {
                const roomId = selectedSuggestion;

                // Update the form with the selected suggestion
                $('#room').val(roomId);

                // Hide the suggestions modal
                $('#suggestionsModal').modal('hide');
                $('#suggestionsModal').remove(); // Remove the modal from the DOM

                // Resubmit the form with the new suggestion
                submitWithUpdatedSuggestion();
            } else {
                alert('Please select a suggestion.');
            }
        });
    }

    // Function to submit the form with the updated suggestion
    function submitWithUpdatedSuggestion() {
        let startHour = $('#startTimeHour').val();
        const startMinute = $('#startTimeMinute').val();
        let endHour = $('#endTimeHour').val();
        const endMinute = $('#endTimeMinute').val();
        const room = $('#room').val();
        const title = $('#eventTitle').val();
        const description = $('#eventDescription').val();
        const repeat = $('#eventRepeat').val();
        const day = $('#eventDate').val();
        let endDate = null;

        if (startHour.toString().length == 1) {
            startHour = "0" + startHour.toString(); 
        }

        if (endHour.toString().length == 1) {
            endHour = "0" + endHour.toString(); 
        }

        const startTime = startHour + ":" + startMinute;
        const endTime = endHour + ":" + endMinute;

        if (repeat !== 'today') {
            endDate = $('#endReservationDate').val();
        }

        const requestData = {
            title: title,
            description: description,
            start_time: startTime,
            end_time: endTime,
            room: room,
            repeat: repeat,
            day: day,
            end_date: endDate
        };

        $.ajax({
            url: '/reservation',
            method: 'POST',
            data: requestData,
            success: function(response) {
                if (response.success) {
                    $('#successModal').modal('show');
                    // Clear form fields
                    resetFormFields();

                    // Ensure backdrop is removed
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();

                    setTimeout(function() {
                        location.reload(); // Reload the page to refresh the table data
                    }, 2000); 
                } else {
                    $('#failureModal').modal('show');
                    alert(response.message);

                    // Ensure backdrop is removed
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                }
            },
            error: function(error) {
                console.error('Error making reservation:', error);
                $('#failureModal').modal('show');
                alert('An error occurred. Please try again.');

                // Ensure backdrop is removed
                $('body').removeClass('modal-open');
                $('.modal-backdrop').remove();
            }
        });
    }

    // Ensure backdrop is removed when the success modal is hidden
    $('#successModal').on('hidden.bs.modal', function() {
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
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
