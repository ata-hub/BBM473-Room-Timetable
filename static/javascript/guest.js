document.addEventListener("DOMContentLoaded", function() {
    var reservations = JSON.parse(document.getElementById('reservations').textContent);
    var department = JSON.parse(document.getElementById('department').textContent);

    // Function to get the day of the week
    function getDayOfWeek(date) {
        var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return days[date.getDay()];
    }

    // Function to format date as "Day of the Week, MM/DD/YYYY"
    function formatDate(date) {
        var mm = String(date.getMonth() + 1).padStart(2, '0');
        var dd = String(date.getDate()).padStart(2, '0');
        var yyyy = date.getFullYear();
        return getDayOfWeek(date) + ', ' + mm + '/' + dd + '/' + yyyy;
    }

    function formatDateForDb(date) {
        var mm = String(date.getMonth() + 1).padStart(2, '0');
        var dd = String(date.getDate()).padStart(2, '0');
        var yyyy = date.getFullYear();

        return dd + '-' + mm + '-' + yyyy;
    }

    // Get today's date and display it
    var today = new Date();
    var todayDateElement = document.getElementById('today-date');
    if (todayDateElement) {
        todayDateElement.textContent = "Today's Date: " + formatDate(today);
    }

    function timeToMinutes(time) {
        const [hours, minutes] = time.split(':').map(Number);
        return hours * 60 + minutes;
    }

    function paintCells(reservations) {
        const cells = document.querySelectorAll('td[data-room-name][data-time-slot]');
        
        cells.forEach(cell => {
            const roomName = cell.getAttribute('data-room-name');
            const timeSlot = cell.getAttribute('data-time-slot');
            const cellTime = timeToMinutes(timeSlot);
            cell.classList.remove('reserved');

            reservations.forEach(reservation => {
                if (reservation.room_name === roomName) {
                    const startTime = timeToMinutes(reservation.start_time);
                    const endTime = timeToMinutes(reservation.end_time);
                    if (cellTime >= startTime && cellTime < endTime) {
                        cell.classList.add('reserved');
                    }
                }
            });
        });
    }

    // Event listener for input date change
    document.getElementById('selected-date').addEventListener('change', function() {
        var selectedDate = new Date(this.value);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(selectedDate);
        fetchReservations(formatDateForDb(selectedDate), department);
    });

    // < Button functionality (Previous day)
    document.getElementById('prev-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() - 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        fetchReservations(formatDateForDb(currentDate), department);
    });

    // > Button functionality (Next day)
    document.getElementById('next-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() + 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        fetchReservations(formatDateForDb(currentDate), department);
    });

    function fetchReservations(day, department) {
        fetch(`/get-by-dep?day=${day}&dep=${department}`)
            .then(response => response.json())
            .then(data => {
                if (data.reservations == "False") {
                    console.log("here88");
                    data.reservations = [];
                }

                paintCells(data.reservations);
            })
            .catch(error => {
                console.error('Error fetching reservations:', error);
            });
    }

    paintCells(reservations);
});