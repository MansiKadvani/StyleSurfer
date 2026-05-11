const modal = document.getElementById("myModal");
const span = document.querySelector(".close");
const message = document.getElementById("message");

const registrationForm = document.getElementById("wizard");

registrationForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const username = document.getElementById("username");
    const email = document.getElementById("email");
    const number = document.getElementById("number");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("cpassword");

    const regExEmail = /^[a-zA-Z0-9_.+\-]+@([a-zA-Z0-9.\-]+\.)+[a-zA-Z]{2,}$/;
    const regExMobNo = /^(\+\d{1,3}[- ]?)?\d{10}$/;
    const regExPassword = /^(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}\[\]:;"'<>,.?~-])[A-Za-z\d!@#$%^&*()_+{}\[\]:;"'<>,.?~-]{8,}$/;

    let valid = true;
    resetErrorMessages();

    if (username.value === "") {
        valid = false;
        showModal("Username is required.");
    } else if (email.value === "") {
        valid = false;
        showModal("Email is required.");
    } else if (!regExEmail.test(email.value)) {
        valid = false;
        showModal("Enter a valid email address.");
    } else if (number.value === "") {
        valid = false;
        showModal("Number is required.");
    } else if (!regExMobNo.test(number.value)) {
        valid = false;
        showModal("Enter a valid number.");
    }else if (password.value === "") {
        valid = false;
        showModal("Password is required.");
    } else if (!regExPassword.test(password.value)) {
        valid = false;
        showModal("Password must be at least 8 characters long and include at least one uppercase letter and one special character.");
    } else if (confirmPassword.value === "") {
        valid = false;
        showModal("Confirm password is required.");
    } else if (confirmPassword.value !== password.value) {
        valid = false;
        showModal("Passwords do not match.");
    }  
    if (valid) {
        const formData = new FormData(registrationForm);
        const registerUrl = `${window.location.origin}/Account/Registration/`;
        fetch(registerUrl, {
            method: 'POST',
            body: formData, // Correct FormData object used here
        })
        .then(response => response.url)
        .then(url => {
            const params = new URLSearchParams(url.split('?')[1]);
            const error = params.get('error');
            if (error) {
                // document.getElementById('error-message').value = error;
                showModal(error);
                // Displaying alert message instead of error in the HTML
                // alert(error); // This will show an alert with the error message
            } else {
                window.location.href = `${window.location.origin}/Account/otpVerify/`;
            }
        });
    }
});

function showModal(messageText) {
    message.textContent = messageText;
    modal.style.display = "block";

    setTimeout(() => {
        modal.style.display = "none";
    }, 7000); // 3000 milliseconds = 3 seconds

}

function resetErrorMessages() {
    const errorMsg = document.querySelectorAll(".error-message");
    errorMsg.forEach(error => error.textContent = "");
}

span.onclick = function() {
    modal.style.display = "none";
};

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};