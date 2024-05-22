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
});
