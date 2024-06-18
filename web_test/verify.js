const verifyTerms = () => {
  console.log("verified");

  const checkboxes = document.querySelectorAll('#term-verification input[type="checkbox"]');
  const approvedTerms = [];
  const notApprovedTerms = [];

  checkboxes.forEach(checkbox => {
    const termData = JSON.parse(checkbox.value);
    if (checkbox.checked) {
      approvedTerms.push(termData);
    } else {
      notApprovedTerms.push(termData);
    }
  });

  console.log("appr terms");
  console.log(approvedTerms);
  console.log("not appr terms");
  console.log(notApprovedTerms);

  // Show the feedback message
  const feedbackMessage = document.getElementById("feedback-message");
  feedbackMessage.style.display = 'block';

  // For when it is a bad search:
  const badfeedbackMessage = document.getElementById("feedback-message-bad");
  badfeedbackMessage.style.display = 'block';
};

function generateCheckboxes(data) {
  const container = document.getElementById('term-verification');
  data.forEach((row, index) => {
      const checkboxContainer = document.createElement('div');
      checkboxContainer.className = 'checkbox-container';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = `term${index}`;
      checkbox.name = `term${index}`;
      checkbox.value = JSON.stringify(row);
      checkbox.checked = true;

      const label = document.createElement('label');
      label.htmlFor = `term${index}`;
      label.textContent = `${row.swe} (${row.swe_inf}), ${row.eng} (${row.eng_inf}), ${row.at}, ${row.pos}, ${row.src}`;

      checkboxContainer.appendChild(checkbox);
      checkboxContainer.appendChild(label);

      // Append the container to the main container
      container.appendChild(checkboxContainer);
  });
}

// Function to check if the user is logged in
function checkLoginStatus() {
  if (sessionStorage.getItem('loggedIn') !== 'true') {
      // Redirect to login page if not logged in
      window.location.href = "login.html";
  }
}

// Run on page load
window.onload = function() {
  checkLoginStatus();
  
  fetch('/stunda/term-verification', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    generateCheckboxes(data);
  })
  .catch(error => {
    console.error('Error fetching term data:', error);
  });
};
