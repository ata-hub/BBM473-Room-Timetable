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
            location.reload();
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
    console.log("edited room is:",editedRoom)
    // Get the values from the custom time pickers
    let startHour = document.getElementById('editStartTimeHour').value;
    let startMinute = document.getElementById('editStartTimeMinute').value;
    console.log("startHour:",startHour,"startMinute:",startMinute)
    let editedStartTime = (startHour && startMinute) ? `${startHour}:${startMinute}` : null;

    let endHour = document.getElementById('editEndTimeHour').value;
    let endMinute = document.getElementById('editEndTimeMinute').value;
    let editedEndTime = (endHour && endMinute) ? `${endHour}:${endMinute}` : null;

    // Check if title or description has changed
    let originalTitle = document.getElementById('editTitle').value;
    let originalDescription = document.getElementById('editDescription').value;
    let originalRoom = document.getElementById('editRoom').value;
    let originalDate = document.getElementById('editDate').value;
    let originalStartTime = document.getElementById('editStartTime').value;
    let originalEndTime = document.getElementById('editEndTime').value;
    // Get the event_id from the hidden input field
    let eventId = document.getElementById('editEventId').value;

    // Initialize arrays to store changed fields
    let changedFields = [];
    let changedReservationFields = [];

    // Check if title has changed and add to changedFields
    if (editedTitle.trim() !== "" && editedTitle !== originalTitle && editedTitle) {
        console.log("pushing title:", editedTitle)
        changedFields.push({ key: 'title', value: editedTitle });
    }

    // Check if description has changed and add to changedFields
    if (editedDescription.trim() !== "" && editedDescription !== originalDescription && editedDescription) {
        console.log("pushing description:", editedDescription)
        changedFields.push({ key: 'description', value: editedDescription });
    }

    // Check if date has changed and add to changedReservationFields
    if (editedDate.trim() !== "" && editedDate !== originalDate && editedDate) {
        console.log("pushing date:", editedDate)
        changedReservationFields.push({ key: 'day', value: editedDate });
    }

    // Check if startTime has changed and add to changedReservationFields
    if (editedStartTime !== null && editedStartTime) {
        console.log("pushing startTime:", editedStartTime)
        changedReservationFields.push({ key: 'to_start', value: editedStartTime });
    }

    // Check if endTime has changed and add to changedReservationFields
    if (editedEndTime !== null && editedEndTime) {
        console.log("pushing endtime:", editedEndTime)
        changedReservationFields.push({ key: 'to_end', value: editedEndTime });
    }

    // Check if room has changed and add to changedReservationFields
    if (editedRoom.trim() !== "" && editedRoom !== originalRoom && editedRoom) {
        console.log("pushing room:", editedRoom)
        changedReservationFields.push({ key: 'room', value: editedRoom });
    }

    // Add original values for fields not in changedFields
    if (!changedFields.find(field => field.key === 'title')) {
        changedFields.push({ key: 'title', value: originalTitle });
    }
    if (!changedFields.find(field => field.key === 'description')) {
        changedFields.push({ key: 'description', value: originalDescription });
    }

    // Send AJAX request for event details if any fields have changed
    if (changedFields.length > 0) {
        console.log("Calling change event details with changed fields:", changedFields);
        $.ajax({
            url: '/change_event_details',
            type: 'POST',
            data: JSON.stringify({
                event_id: eventId,
                changed_fields: changedFields
            }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Event details updated successfully:', response);
                location.reload(); // Reload the page
            },
            error: function(error) {
                console.error('Error updating event details:', error);
            }
        });
    }

    // Add original values for fields not in changedReservationFields
    if (!changedReservationFields.find(field => field.key === 'day')) {
        changedReservationFields.push({ key: 'day', value: originalDate });
    }
    if (!changedReservationFields.find(field => field.key === 'to_start')) {
        changedReservationFields.push({ key: 'to_start', value: originalStartTime });
    }
    if (!changedReservationFields.find(field => field.key === 'to_end')) {
        changedReservationFields.push({ key: 'to_end', value: originalEndTime });
    }
    if (!changedReservationFields.find(field => field.key === 'room')) {
        changedReservationFields.push({ key: 'room', value: originalRoom });
    }

    // Send AJAX request for reservation details if any fields have changed
    if (changedReservationFields.length > 0) {
        console.log("Calling change reservation with changed fields:", changedReservationFields);
        $.ajax({
            url: '/change_reservation',
            type: 'POST',
            data: JSON.stringify({
                event_id: eventId,
                changed_fields: changedReservationFields
            }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Reservation updated successfully:', response);
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

    if (editInputContainer.style.display === 'none' || editInputContainer.style.display === '') {
        // Set the value of the edit input to the main input's value
        const editInput = editInputContainer.querySelector('.edit-input');
        editInput.value = mainInput.value;
        editInputContainer.style.display = 'block';
    } else {
        editInputContainer.style.display = 'none';
    }

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
