/* sidebar.js */

$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        console.log('Toggle button clicked!');
    });
});
document.addEventListener("DOMContentLoaded", function() {
    var sidebar = document.querySelector('.sidebar');
    var sidebarToggle = document.querySelector('.sidebar-toggle');
    var isStudent = isStudent === "True";
    var isInstructor = isInstructor === "True";
    var username = username;
    var department = department;
    var sidebarOpen = true;

    if (isStudent) {
        // Select the link with the specified URL and set its display style to "block"
        //document.querySelector("a[href='{{ url_for('reserve_rooms') }}']").style.display = "block";
    }

    // Check if the user is an instructor and show the corresponding link
    if (isInstructor) {
        // Select the link with the specified URL and set its display style to "block"
        //document.querySelector("a[href='{{ url_for('feature_request') }}']").style.display = "block";
    }


    
    

    
    

    
    
});
