
    var swiper = new Swiper('.swiper-container', {
      slidesPerView: 1,
      spaceBetween: 10,
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
    });
    function changeImage(imageUrl) {
              document.getElementById('mainProductImage').src = imageUrl;
          }
    function toggleAccordion(button) {
        var content = button.nextElementSibling;
        var icon = button.querySelector('i');
        if (content.style.display === 'block') {
          content.style.display = 'none';
          icon.classList.remove('fa-chevron-up');
          icon.classList.add('fa-chevron-down');
        } else {
          content.style.display = 'block';
          icon.classList.remove('fa-chevron-down');
          icon.classList.add('fa-chevron-up');
        }
      }


      var swiper = new Swiper(".recommend_slider", {
      spaceBetween: 30,
      loop: true,
      speed: 1000,
      autoplay:{
        delay: 2000,
      },
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
      navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  breakpoints: {320: {slidesPerView: 1, },768: {slidesPerView: 3, },1200: {slidesPerView: 4, },480: {slidesPerView: 2,},},
    });


// =================================================================================================================

//  size


      document.querySelectorAll('.size-button').forEach(button => {
        button.addEventListener('click', function() {
          // Remove 'active' class from all buttons
          document.querySelectorAll('.size-button').forEach(btn => btn.classList.remove('active'));
          // Add 'active' class to the clicked button
          this.classList.add('active');
        });
      });
  

//  ==============================================================================================================
  
    // Zoom effect //
  
    const mainImage = document.getElementById('mainProductImage');
  
     mainImage.addEventListener('mouseenter', () => {
      mainImage.style.transform = 'scale(1.9) '; // Zoom in to 150% when mouse enters
  });   
  
     mainImage.addEventListener('mouseleave', () => {
      mainImage.style.transform = 'scale(1)'; // Zoom out when mouse leaves
  });
  
  // Optional: Keep the zoom effect while moving the mouse within the image
  mainImage.addEventListener('mousemove', (event) => {
      const rect = mainImage.getBoundingClientRect();
      const x = event.clientX - rect.left; // x position within the image
      const y = event.clientY - rect.top; // y position within the image
  
      // Calculate the translate values based on mouse position
      const xPercent = (x / rect.width) * 100; // Percentage of x position
      const yPercent = (y / rect.height) * 100; // Percentage of y position
  
      // Apply the transformation to zoom in
      mainImage.style.transformOrigin = `${xPercent}% ${yPercent}%`; // Set the origin for the zoom effect
      mainImage.style.transform = 'scale(1.9)'; // Keep zoomed in while moving the mouse
  });



//=================================================================================================

//passed data




//======================================================================================================

// Add to cart


$.post('/add_to_cart/', formData, function (response) {
    if (response.success) {
        alert(response.message); // Show success message
    } else {
        alert(response.message); // Show error or duplicate message
    }
}).fail(function () {
    alert("An error occurred. Please try again.");
});

//========================================================================================================


  // Function to remove 'error' parameter from the URL
  function removeErrorParam() {
      const url = new URL(window.location.href);
      url.searchParams.delete('error');
      window.history.replaceState({}, document.title, url.toString()); // Update the URL
  }
  function removeSuccessParam() {
      const url = new URL(window.location.href);
      url.searchParams.delete('success');// Remove the 'error' parameter
      window.history.replaceState({}, document.title, url.toString()); // Update the URL
  }

  // Set timeout to remove error message and update URL after 5 minutes
  setTimeout(function() {
      const errorMsg = document.getElementById('error-message');
      const successMsg = document.getElementById('success-message');
      if (errorMsg) {
          errorMsg.style.display = 'none';
          removeErrorParam(); // Hide the error message
      }
      else{
        successMsg.style.display = 'none';
        removeSuccessParm();// Hide the error message
      }

      // Remove the parameter from the URL
  }, 20000); // 300,000 milliseconds = 5 minutes

  window.addEventListener("load", function() {
      removeErrorParam();
  });


//  ============================================================================================================

