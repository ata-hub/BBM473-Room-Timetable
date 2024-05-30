$(document).ready(function() {
    $('#loginForm').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/login',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                    $('#successModal').modal('show'); // bunlar kalmalı mı? bir şey göstermedi ama?
                } else {
                    console.log(response); 
                    $('#failureModal').modal('show');
                }
            },
            error: function() {
                $('#failureModal').modal('show');
            }
        });
    });

    $('#guestModal').on('shown.bs.modal', function(event) {
        event.preventDefault();
        $.ajax({
            url: '/guest-login',
            method: 'GET',
            data: $(this).serialize(),
            success: function(response) {
                var departments = response.departments;
                var departmentSelect = $('#department');
                departmentSelect.empty(); 
                departments.forEach(function(department) {
                    departmentSelect.append($('<option>', {
                        value: department.department_id, 
                        text: department.name 
                    }));
                });
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    });

    //TODO guest.html gelince oraya navigate et fln 
    $('#guestLoginForm').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: '/login',
            method: 'GET',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect_url;
                    $('#successModal').modal('show'); // bunlar kalmalı mı? bir şey göstermedi ama?
                } else {
                    console.log(response); 
                    $('#failureModal').modal('show');
                }
            },
            error: function() {
                $('#failureModal').modal('show');
            }
        });
    });
});