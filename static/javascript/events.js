// events.js

// Function to show booking details in modal
function showDetails(title, description, capacity, features) {
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalDescription').innerText = description;
    document.getElementById('modalCapacity').innerText = 'Capacity: ' + capacity;
    document.getElementById('modalFeatures').innerText = 'Features: ' + features;
}

// Function to open edit modal with existing booking details
function editBooking(event, booking) {
    event.stopPropagation();  // Stop the event from propagating to parent elements
    event.preventDefault();   // Prevent the default action

    console.log("edit screen opened");
    document.getElementById('editTitle').value = booking.title;
    document.getElementById('editDescription').value = booking.description;
    document.getElementById('editRoom').value = booking.room_name;
    document.getElementById('editDate').value = booking.date;
    document.getElementById('editStartTime').value = booking.start_time;
    document.getElementById('editEndTime').value = booking.end_time;
    document.getElementById('editEventId').value = booking.event_id;

    // Open the edit modal
    $('#editBookingModal').modal('show');
}

// Function to delete a booking
// Function to open delete confirmation modal
function deleteBooking(event_id) {
    // Prevent card detail popup from appearing
    event.stopPropagation();
    event.preventDefault();

    // Show the confirmation modal
    $('#confirmationModal').modal('show');

    // Set event id as data attribute to the "Yes" button for deletion
    $('#confirmDelete').attr('data-event-id', event_id);
}

// Event listener for confirm delete button
$('#confirmDelete').on('click', function() {
    // Get the event id from the button's data attribute
    var event_id = $(this).data('event-id');

    // Make an AJAX call to cancel the reservation
    $.ajax({
        url: '/cancel-reservation',
        method: 'POST',
        data: { event_id: event_id },
        success: function(response) {
            // Handle success response
            console.log('Event cancelled successfully');
            // Optionally, update the UI to reflect the cancelled reservation
        },
        error: function(error) {
            // Handle error response
            console.error('Error cancelling event:', error);
        }
    });
});

// Function to save changes made in the edit modal
function saveChanges() {
    // Get the edited values from the edit modal inputs
    let editedTitle = document.getElementById('editTitleInput').value;
    let editedDescription = document.getElementById('editDescriptionInput').value;
    let editedRoom = document.getElementById('editRoomInput').value;
    let editedDate = document.getElementById('editDateInput').value;

    // Get the values from the custom time pickers
    let startHour = document.getElementById('editStartTimeHour').value;
    let startMinute = document.getElementById('editStartTimeMinute').value;
    let editedStartTime = (startHour && startMinute) ? `${startHour}:${startMinute}` : null;

    let endHour = document.getElementById('editEndTimeHour').value;
    let endMinute = document.getElementById('editEndTimeMinute').value;
    let editedEndTime = (endHour && endMinute) ? `${endHour}:${endMinute}` : null;

    // Check if title or description has changed
    let originalTitle = document.getElementById('editTitle').value;
    let originalDescription = document.getElementById('editDescription').value;
    // Get the event_id from the hidden input field
    let eventId = document.getElementById('editEventId').value;

    if ((editedTitle && editedTitle !== originalTitle) || 
        (editedDescription && editedDescription !== originalDescription)) {
        console.log("calling change event details")
        $.ajax({
            url: '/change_event_details',
            type: 'POST',
            data: JSON.stringify({
                event_id: eventId,
                title: (editedTitle !== null) ? editedTitle : originalTitle,
                description: (editedDescription !== null) ? editedDescription : originalDescription
            }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Event details updated:', response);
                location.reload(); // Reload the page
            },
            error: function(error) {
                console.error('Error updating event details:', error);
            }
        });
    }

    // Check if date, start time, end time, or room has changed
    let originalDate = document.getElementById('editDate').value;
    let originalStartTime = document.getElementById('editStartTime').value;
    let originalEndTime = document.getElementById('editEndTime').value;
    let originalRoom = document.getElementById('editRoom').value;

    if ((editedDate && editedDate !== originalDate) || 
        (editedStartTime && editedStartTime !== originalStartTime) || 
        (editedEndTime && editedEndTime !== originalEndTime) || 
        (editedRoom && editedRoom !== originalRoom)) {
        console.log("calling change reservation")
        $.ajax({
            url: '/change_reservation',
            type: 'POST',
            data: JSON.stringify({
                event_id: eventId,
                day: (editedDate !== null) ? editedDate : originalDate,
                to_start: (editedStartTime !== null) ? editedStartTime : originalStartTime,
                to_end: (editedEndTime !== null) ? editedEndTime : originalEndTime,
                room: (editedRoom !== null) ? editedRoom : originalRoom
            }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Reservation updated:', response);
                location.reload(); // Reload the page
            },
            error: function(error) {
                console.error('Error updating reservation:', error);
            }
        });
    }

    // Close the edit modal
    $('#editBookingModal').modal('hide');
}

function showEditInput(field) {
    const mainInput = document.getElementById(field);
    const editInputContainer = mainInput.parentElement.querySelector('.edit-input-container');

    console.log('Main input:', mainInput);
    console.log('Edit input container:', editInputContainer);

    if (editInputContainer.style.display === 'none' || editInputContainer.style.display === '') {
        // Set the value of the edit input to the main input's value
        const editInput = editInputContainer.querySelector('.edit-input');
        editInput.value = mainInput.value;
        editInputContainer.style.display = 'block';
    } else {
        editInputContainer.style.display = 'none';
    }

    console.log('After toggle - Main input display:', mainInput.style.display);
    console.log('After toggle - Edit input container display:', editInputContainer.style.display);
}

function closeModal() {
    document.getElementById('popupModal').style.display = "none";
}

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
    var modal = document.getElementById('popupModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
