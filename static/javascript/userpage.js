document.addEventListener("DOMContentLoaded", function() {
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

    // Get today's date and display it
    var today = new Date();
    var todayDateElement = document.getElementById('today-date');
    if (todayDateElement) {
        todayDateElement.textContent = "Today's Date: " + formatDate(today);
    }

    // Event listener for input date change
    document.getElementById('selected-date').addEventListener('change', function() {
        var selectedDate = new Date(this.value);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(selectedDate);
        // Implement functionality to navigate to the selected date
    });

    // < Button functionality (Previous day)
    document.getElementById('prev-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() - 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        // Implement functionality to navigate to the previous day
    });

    // > Button functionality (Next day)
    document.getElementById('next-day').addEventListener('click', function() {
        var currentDate = new Date(document.getElementById('today-date').textContent.split(': ')[1].split(', ')[1].replace(/\//g, '-'));
        currentDate.setDate(currentDate.getDate() + 1);
        document.getElementById('today-date').textContent = "Selected Date: " + formatDate(currentDate);
        // Implement functionality to navigate to the next day
    });
});