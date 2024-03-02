document.addEventListener("DOMContentLoaded", function () {
    // Get the outer div element
    var emailList = document.getElementById("email-list");

    // Add a click event listener to the outer div
    emailList.addEventListener("click", function (event) {
        // Check if the clicked element is an inner div with class "email-list-item"
        if (event.target.classList.contains("email-list-item")) {
            // Get the specific inner div that was clicked
            var clickedEmail = event.target;

            // Perform actions based on the clicked inner div
            var emailContentDisplay = document.getElementById("email-content")
            emailContentDisplay.innerHTML = clickedEmail.innerHTML;

            // You can perform any other actions here based on the clicked item
        }
    });
});