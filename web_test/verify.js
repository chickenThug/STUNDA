const verifyTerms =  () => {
  console.log("verified");

  const checkboxes = document.querySelectorAll('#term-verification input[type="checkbox"]');
  const terms = [];

  checkboxes.forEach(checkbox => {
    const termData = JSON.parse(checkbox.value);
    if (checkbox.checked) {
      termData["approved"] = true
    } else {
      termData["approved"] = false
    }
    terms.push(termData);
  });

   console.log("verification otw");
   console.log(terms);

   // FIX SERVLET CALL HERE
   // Send approved and not approved terms to the servlet
   fetch('/stunda/handle-verify', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(terms)
    })
    .then(response => response.text())
    .then(data => {
      console.log("Received data:", data);
        if (data === "success") {
            console.log("Terms processed successfully");
        } else {
            console.error("Error processing terms");
        }
    })
    .catch(error => {
        console.error("Error: ", error);
    });
};

function generateCheckboxes(data) {
  const container = document.getElementById('term-verification');

  if (data.length === 0) {
    // Display message if no terms to check
    const noTermsMessage = document.getElementById('no-action-message');
    noTermsMessage.style.display = 'block';
    return;
  }

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
      // Use an array of conditions and filter out any that result in empty strings or falsy values
      label.textContent = [
        row.swe_lemma ? `${row.swe_lemma}${row.swedish_inflections ? ` (${row.swedish_inflections})` : ''}` : '',
        row.eng_lemma ? `${row.eng_lemma}${row.english_inflections ? ` (${row.english_inflections})` : ''}` : '',
        row.agreed_pos || '',
        row.src || ''
      ].filter(Boolean).join(', ');

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

function handleJSONLContent(jsonlContent) {
  console.log(jsonlContent);
  const lines = jsonlContent.trim().split('\n');
  const termsList = lines.map(line => JSON.parse(line));
  console.log(termsList);
  generateCheckboxes(termsList);
}

// Fetch JSONL file from server
async function fetchJSONL() {
  await fetch('/stunda/term-verification', {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json'
      }
  })
  .then(response => response.text())
  .then(data => handleJSONLContent(data))
  .catch(error => {
      console.error('Error fetching JSONL:', error);
  });
}

// Run on page load
window.onload = function() {
  checkLoginStatus();
  fetchJSONL();
};