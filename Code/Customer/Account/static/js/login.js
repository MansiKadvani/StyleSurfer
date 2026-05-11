const loginform = document.getElementById("wizard");

const modal = document.getElementById("login");
const span = document.querySelector(".close");
const message = document.getElementById("message_login");

loginform.addEventListener("submit", (event) => {
    event.preventDefault();
    const username = document.getElementById("username");
    const password = document.getElementById("password");

    let valid = true;
    resetErrorMessages();

    if (username.value == "") {
        valid = false;
        showModal("Username is required." , "error");
    }
    else if(password.value == ""){
        valid = false;
        showModal("Password is required." , "error");
    }


    if (valid) {
        const LoginformData = new FormData(loginform); // Use the correct FormData object
        const loginUrl = window.location.origin + "/Account/login/";
        fetch(loginUrl, {
            method: 'POST',
            body: LoginformData, // Correct FormData object used here
        })
        .then(response => response.url)
        .then(url => {
            const params = new URLSearchParams(url.split('?')[1]);
            const error = params.get('error');
            const success = params.get('success');

            if (error) {
                // document.getElementById('error-message').value = error;
                showModal(error , "error");
                // Displaying alert message instead of error in the HTML
                // alert(error); // This will show an alert with the error message
            }
            else if(success){
                showModal(success,"success");
            }



            else {
                window.location.href = window.location.origin + ""; // Redirect if login is successful
            }
        });
    }
});

const params=new URLSearchParams(window.location.search);
const success = params.get('success');
if (success) {
    showModal(success,"success");
}

//function showModal(messageText) {
//    message.textContent = messageText;
//    modal.style.display = "block";
//
//    setTimeout(() => {
//        modal.style.display = "none";
//    }, 7000); // 3000 milliseconds = 3 seconds
//
//}


 function showModal(messageText, type) {
            message.textContent = messageText;

            const icon = document.querySelector(".modal-content i"); // Get the icon element

            if (type == "error") {
                message.style.color = "red";
                icon.className = "fa fa-exclamation-triangle"; // Set error icon
                icon.style.color = "red";
            } else {
                message.style.color = "green";
                icon.className = "fa fa-check-circle"; // Set success icon
                icon.style.color = "green";
            }

            modal.style.display = "block";

            setTimeout(() => {
                modal.style.display = "none";
            }, 7000);
        }


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