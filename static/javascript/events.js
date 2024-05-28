// events.js

// Function to show booking details in modal
function showDetails(title, description) {
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalDescription').innerText = description;
}

// Function to open edit modal with existing booking details
function editBooking(event, booking) {
    event.stopPropagation();  // Stop the event from propagating to parent elements
    event.preventDefault();   // Prevent the default action

    console.log("edit screen opened");
    document.getElementById('editTitle').value = booking.title;
    console.log("title value written:", document.getElementById('editTitle').value);
    document.getElementById('editDescription').value = booking.description;
    document.getElementById('editRoom').value = booking.room_id;
    document.getElementById('editStartTime').value = booking.start_time;
    document.getElementById('editEndTime').value = booking.end_time;

    // Open the edit modal
    $('#editBookingModal').modal('show');
}

// Function to save changes made in the edit modal
function saveChanges() {
    // Get the edited values from the edit modal inputs
    let editedTitle = document.getElementById('editTitle').value;
    let editedDescription = document.getElementById('editDescription').value;
    let editedRoom = document.getElementById('editRoom').value;
    let editedStartTime = document.getElementById('editStartTime').value;
    let editedEndTime = document.getElementById('editEndTime').value;

    // Update the booking details in the database or backend service
    // For demonstration purposes, let's assume there's a function updateBookingDetails to update the details
    updateBookingDetails(editedTitle, editedDescription, editedRoom, editedStartTime, editedEndTime);

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
