function showSuccessMessage(message) {
    const successMessageDiv = document.getElementById('success-message');
    successMessageDiv.textContent = message;
    successMessageDiv.style.display = 'block';
    successMessageDiv.style.opacity = 1;

    // Hide the message after 3 seconds
    setTimeout(function() {
        successMessageDiv.style.opacity = 0;
        setTimeout(function() {
            successMessageDiv.style.display = 'none';
        }, 300);  // Wait for fade out to complete before hiding
    }, 5000);  // Show for 3 seconds
}

// On page load, check for query params and show success message if applicable
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const successMessage = urlParams.get('success');
    
    if (successMessage === 'password_set') {
        showSuccessMessage("Your password has been set successfully! Please log in.");
    }
    else if (successMessage === 'email_sent') {
        showSuccessMessage("Email is sent to your email address for reset the password. Please check your email.");
    }
    else if (successMessage === 'psw_changed') {
        showSuccessMessage("Your password has been changed successfully! Please log in.");
    }

}

const sellerloginform = document.getElementById("login-form");

const modal = document.getElementById("logins");
const span = document.querySelector(".close");
const message = document.getElementById("messages");

sellerloginform.addEventListener("submit" , (event) =>{
    event.preventDefault();
    const semail = document.getElementById("your_email");
    const spassword = document.getElementById("your_pass");
    const regExEmail = /^[a-zA-Z0-9_.+\-]+@([a-zA-Z0-9.\-]+\.)+[a-zA-Z]{2,}$/;

    let valid = true;
    resetErrorMessages();

    if (semail.value === "") {
        valid = false;
        showModal("Email is required.");
    } else if (!regExEmail.test(semail.value)) {
        valid = false;
        showModal("Enter a valid email address.");
    } else if(spassword.value == ""){
        valid = false;
        showModal("Password is required.");
    }

    if (valid) {
        const sLoginformData = new FormData(sellerloginform); // Use the correct FormData object
        const sloginUrl = `${window.location.origin}/Seller/seller_login/`;
        fetch(sloginUrl, {
            method: 'POST',
            body: sLoginformData, // Correct FormData object used here
        })
        .then(response => response.url)
        .then(url => {
            const params = new URLSearchParams(url.split('?')[1]);
            const error = params.get('error');
            if (error) {
                showModal(error);     
                // Displaying alert message instead of error in the HTML
                // alert(error); // This will show an alert with the error message
            } else {
                // window.location.href = `${window.location.origin}/Seller/dashboard/`
                window.location.href = `${window.location.origin}/Seller/Sdashboard/`;
            }
        });
    }
});

function resetErrorMessages() {
    const errorMsg = document.querySelectorAll(".error-message");
    errorMsg.forEach((error) => {
        error.textContent = "";
    });
}


span.onclick = function() {
    modal.style.display = "none";
};

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};

function showModal(messageText) {
    message.textContent = messageText;
    modal.style.display = "block";

    setTimeout(() => {
        modal.style.display = "none";
    }, 5000); // 3000 milliseconds = 3 seconds

}