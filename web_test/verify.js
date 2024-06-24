const verifyTerms =  () => {
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
   console.log("verification otw");

   // FIX SERVLET CALL HERE
   // Send approved and not approved terms to the servlet
   fetch('/stunda/handle-verified', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        approvedTerms: approvedTerms,
        notApprovedTerms: notApprovedTerms
    })
})
.then(response => response.json())
.then(data => {
    if (data.status === "success") {
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
        row.swe_term ? `${row.swe_term}${row.swe_inf ? ` (${row.swe_inf})` : ''}` : '',
        row.eng_term ? `${row.eng_term}${row.eng_inf ? ` (${row.eng_inf})` : ''}` : '',
        row.at || '',
        row.pos || '',
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

function handleCSVContent(csvContent) {
  const lines = csvContent.split('\n');
  const termsList = [];
  const headers = lines[0].split(',');
  
  for (let i = 1; i < lines.length -1; i++) {
      const values = lines[i].split(',');
      if (values.length === headers.length) {
          const termData = {};
          for (let j = 0; j < headers.length; j++) {
              termData[headers[j]] = values[j];
          }
          termsList.push(termData);
      }
      // TODO: remove in future
      else {
        const termData = {};
          for (let j = 0; j < headers.length; j++) {
              termData[headers[j]] = values[j];
          }
          termsList.push(termData);
      }
  }

  generateCheckboxes(termsList);
}


// Fetch CSV file from server
async function fetchCSV() {
  await fetch('/stunda/term-verification', {
      method: 'GET',
      headers: {
          'Content-Type': 'text/csv'
      }
  })
  .then(response => response.text())
  .then(data => handleCSVContent(data))
  .catch(error => {
      console.error('Error fetching CSV:', error);
  });
}

// Run on page load
window.onload = function() {
  checkLoginStatus();
  fetchCSV();
};
