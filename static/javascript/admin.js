document.addEventListener("DOMContentLoaded", function() {
    var myReservations = JSON.parse(document.getElementById('my-reservations').textContent);
    var otherReservations = JSON.parse(document.getElementById('other-reservations').textContent);


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

    function paintCells(myReservations, otherReservations) {
        const cells = document.querySelectorAll('td[data-room-name][data-time-slot]');
        
        cells.forEach(cell => {
            const roomName = cell.getAttribute('data-room-name');
            const timeSlot = cell.getAttribute('data-time-slot');
            const cellTime = timeToMinutes(timeSlot);
            cell.classList.remove('your-reservations', 'reserved');

            myReservations.forEach(reservation => {
                if (reservation.room_name === roomName) {
                    const startTime = timeToMinutes(reservation.start_time);
                    const endTime = timeToMinutes(reservation.end_time);
                    if (cellTime >= startTime && cellTime < endTime) {
                        cell.classList.add('your-reservations');
                    }
                }
            });

            otherReservations.forEach(reservation => {
                if (reservation.room_name === roomName) {
                    const startTime = timeToMinutes(reservation.start_time);
                    const endTime = timeToMinutes(reservation.end_time);
                    //console.log(`Cell Time: ${cellTime}, Start Time: ${startTime}, End Time: ${endTime}`);
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
        fetchReservations(formatDateForDb(selectedDate));
    });

    // < Button functionality (Previous day)
    document.getElementById('prev-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() - 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        fetchReservations(formatDateForDb(currentDate));
    });

    // > Button functionality (Next day)
    document.getElementById('next-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() + 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        fetchReservations(formatDateForDb(currentDate));
    });

    function fetchReservations(day) {
        fetch(`/get-by-day?day=${day}`)
            .then(response => response.json())
            .then(data => {

                if (data.my_reservations === "False") {
                    data.my_reservations = [];
                }
                
                if (data.other_reservations === "False") {
                    data.other_reservations = [];
                }
                paintCells(data.my_reservations, data.other_reservations);
            })
            .catch(error => {
                console.error('Error fetching reservations:', error);
            });
    }

    paintCells(myReservations, otherReservations);
});