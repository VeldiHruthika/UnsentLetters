document.getElementById("email-form").addEventListener("submit", function(event) {
    event.preventDefault();
    const email = document.getElementById("email").value;

    // Make sure email is not empty and follow correct validation
    if (email === "") {
        document.getElementById("error-message").style.display = "block";
        return;
    }

    // Send the email to the backend for OTP generation
    fetch('/register', {
        method: 'POST',
        body: new URLSearchParams({ 'email': email }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/verify-otp';  // Redirect to OTP verification page
        } else {
            document.getElementById("error-message").style.display = "block";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById("error-message").style.display = "block";
    });
});
