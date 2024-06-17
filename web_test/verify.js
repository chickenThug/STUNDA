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

// Sample data
const data = [
  { swe: "test", eng: "test", swe_inf: ["testböj", "jfjfj", "jfjfj"], eng_inf: ["testinfl", "hah"], pos: "N", at: "teast", src: "emelie" },
  { swe: "test2", eng: "test2", swe_inf: "testböj2", eng_inf: "testinfl2", pos: "N2", at: "teast2", src: "emelie2" },
  { swe: "test3", eng: "test3", swe_inf: "testböj3", eng_inf: "testinfl3", pos: "N3", at: "teast3", src: "emelie3" },
  { swe: "test4", eng: "test4", swe_inf: "testböj4", eng_inf: "testinfl4", pos: "N4", at: "teast4", src: "emelie4" },
  { swe: "test5", eng: "test5", swe_inf: "testböj5", eng_inf: "testinfl5", pos: "N5", at: "teast5", src: "emelie5" }
];

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
  generateCheckboxes(data);
};
