$(document).ready(function() {
    $('.btn-square').on('click', function() {
      var requestId = $(this).data('request-id');
      var acceptance = $(this).data('acceptance');
      console.log("student button is clicked:", acceptance)
      $.ajax({
        url: '/admin/accept_student_request',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
          permission_id: requestId,
          acceptance: acceptance
        }),
        success: function(response) {
            //burada sayfayı tekrar yükle
          if (response.success) {
            alert('Permission updated successfully');
            location.reload();  // Reload the page to reflect changes
          } else {
            alert('Failed to update permission: ' + response.message);
          }
        },
        error: function(xhr) {
          alert('Error: ' + xhr.responseText); // error message from app.py
        }
      });
    });
  });