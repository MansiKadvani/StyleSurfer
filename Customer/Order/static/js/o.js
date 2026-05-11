// Validate the input fields separately

const address = document.getElementById("address");

function validateAddressForm(event) {
    event.preventDefault(); // Prevent form submission
    debugger;

    let isValid = true; // Flag to track if the form is valid
    resetErrorMessages(); // Reset previous error messages

    // Validate First Name
    let firstName = document.getElementById("firstName");
    if (!firstName.value.trim()) {
        isValid = false;
        document.getElementById("firstNameError").innerText = "First name is required.";
        firstName.classList.add("is-invalid");
    } else {
        firstName.classList.remove("is-invalid");
    }

    // Validate Last Name
    let lastName = document.getElementById("lastName");
    if (!lastName.value.trim()) {
        isValid = false;
        document.getElementById("lastNameError").innerText = "Last name is required.";
        lastName.classList.add("is-invalid");
    } else {
        lastName.classList.remove("is-invalid");
    }

    // Validate Email
    let email = document.getElementById("email");
    let emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!email.value.trim()) {
        isValid = false;
        document.getElementById("emailError").innerText = "Email is required.";
        email.classList.add("is-invalid");
    } else if (!emailPattern.test(email.value.trim())) {
        isValid = false;
        document.getElementById("emailError").innerText = "Please enter a valid email.";
        email.classList.add("is-invalid");
    } else {
        email.classList.remove("is-invalid");
    }

    // Validate Mobile Number
    let mobileNumber = document.getElementById("mobileNumber");
    let mobilePattern = /^[0-9]{10}$/; // Example pattern for 10 digit mobile number
    if (!mobileNumber.value.trim()) {
        isValid = false;
        document.getElementById("mobileError").innerText = "Mobile number is required.";
        mobileNumber.classList.add("is-invalid");
    } else if (!mobilePattern.test(mobileNumber.value.trim())) {
        isValid = false;
        document.getElementById("mobileError").innerText = "Please enter a valid 10-digit mobile number.";
        mobileNumber.classList.add("is-invalid");
    } else {
        mobileNumber.classList.remove("is-invalid");
    }

    // Validate Address Line 1
    let address1 = document.getElementById("addressLine1");
    if (!address1.value.trim()) {
        isValid = false;
        document.getElementById("address1Error").innerText = "Address Line 1 is required.";
        address1.classList.add("is-invalid");
    } else {
        address1.classList.remove("is-invalid");
    }

    // Validate City
    let city = document.getElementById("city");
    if (!city.value.trim()) {
        isValid = false;
        document.getElementById("cityError").innerText = "City is required.";
        city.classList.add("is-invalid");
    } else {
        city.classList.remove("is-invalid");
    }

    // Validate State
    let state = document.getElementById("state");
    if (!state.value.trim()) {
        isValid = false;
        document.getElementById("stateError").innerText = "State is required.";
        state.classList.add("is-invalid");
    } else {
        state.classList.remove("is-invalid");
    }

    // Validate Pin Code
    let pincode = document.getElementById("pinCode");
    let pincodePattern = /^[0-9]{6}$/; // Example for 6 digit pin code
    if (!pincode.value.trim()) {
        isValid = false;
        document.getElementById("pincodeError").innerText = "Pin Code is required.";
        pincode.classList.add("is-invalid");
    } else if (!pincodePattern.test(pincode.value.trim())) {
        isValid = false;
        document.getElementById("pincodeError").innerText = "Please enter a valid 6-digit pin code.";
        pincode.classList.add("is-invalid");
    } else {
        pincode.classList.remove("is-invalid");
    }

    // Validate Country
    let country = document.getElementById("country");
    if (!country.value.trim()) {
        isValid = false;
        document.getElementById("countryError").innerText = "Country is required.";
        country.classList.add("is-invalid");
    } else {
        country.classList.remove("is-invalid");
    }







debugger;
    if (isValid) {
    const formData = new FormData(address);
    const registerUrl = `${window.location.origin}/Cart/order_form/order_form/`;
    fetch(registerUrl, {
        method: 'POST',
        body: formData, // Correct FormData object used here
    })
    .then(response => response.url)
    .then(url => {
        const params = new URLSearchParams(url.split('?')[1]);
        const error = params.get('error');
        if (error) {
            showModal(error);
        } else {
            navigateToStep(2)
        }
    });

    // Continue to next step
   ;
}



   
}

// Function to reset error messages and styles
function resetErrorMessages() {
    let errorMessages = document.querySelectorAll('.invalid-feedback');
    errorMessages.forEach(function (message) {
        message.innerText = '';
    });

    let inputFields = document.querySelectorAll('.form-control');
    inputFields.forEach(function (input) {
        input.classList.remove('is-invalid');
    });
}

// Retrieve the current step from the URL
function getCurrentStepFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('step')) || 1; // Default to step 1 if not found
}

// Update the URL with the current step
function updateURLWithStep(step) {
    const url = new URL(window.location);
    url.searchParams.set('step', step);
    history.pushState(null, '', url);
}

// Function to navigate to a specific step
function navigateToStep(step) {
    updateURLWithStep(step);

    // Hide all sections
    document.getElementById('address-section').classList.add('hidden');
    document.getElementById('review-section').classList.add('hidden');
    document.getElementById('payment-section').classList.add('hidden');

    // Set all steps as inactive
    document.getElementById('step1').classList.remove('active');
    document.getElementById('step2').classList.remove('active');
    document.getElementById('step3').classList.remove('active');

    // Show the appropriate section and highlight the step
    if (step === 1) {
        document.getElementById('address-section').classList.remove('hidden');
        document.getElementById('step1').classList.add('active');
    } else if (step === 2) {
        document.getElementById('review-section').classList.remove('hidden');
        document.getElementById('step2').classList.add('active');
    } else if (step === 3) {
        document.getElementById('payment-section').classList.remove('hidden');
        document.getElementById('step3').classList.add('active');
    }
}

// Functions to navigate to next and previous steps
function navigateToNextStep() {
    let currentStep = getCurrentStepFromURL();
    if (currentStep < 3) {
        navigateToStep(currentStep + 1);
    }
}

function navigateToPrevStep() {
    let currentStep = getCurrentStepFromURL();
    if (currentStep > 1) {
        navigateToStep(currentStep - 1);
    }
}

// On page load, navigate to the last saved step
window.onload = function () {
    let currentStep = getCurrentStepFromURL();
    navigateToStep(currentStep);
};

// Function to show the appropriate payment section based on the selected method
function showPaymentSection(method) {
    // Hide both sections first
    document.getElementById('payOnlineSection').style.display = 'none';
    document.getElementById('cashOnDeliverySection').style.display = 'none';

    // Show the selected section
    if (method === 'online') {
        document.getElementById('payOnlineSection').style.display = 'block';
        document.getElementById('payOnlineBtn').classList.add('active');
        document.getElementById('cashOnDeliveryBtn').classList.remove('active');
    } else if (method === 'cod') {
        document.getElementById('cashOnDeliverySection').style.display = 'block';
        document.getElementById('cashOnDeliveryBtn').classList.add('active');
        document.getElementById('payOnlineBtn').classList.remove('active');
    }
}

// Initialize the payment section to show Pay Online by default
showPaymentSection('online');

//--------------------------------

