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
});
