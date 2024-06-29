let currentIndex = 0;
let termsList = [];

const verifyTerms =  () => {
  const checkboxes = document.querySelectorAll('#term-verification input[type="checkbox"]');
  const terms = [];

  checkboxes.forEach(checkbox => {
    const termData = JSON.parse(checkbox.value);
    // change to termData["approved"] = checkbox.checked; ?
    if (checkbox.checked) {
      termData["approved"] = true
    } else {
      termData["approved"] = false
    }
    terms.push(termData);
  });
  const username = sessionStorage.getItem('username');

  const payload = {
    username: username,
    terms: terms
  };

   // Send approved and not approved terms to the servlet
   fetch('/stunda/handle-verify', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    .then(response => response.text())
    .then(data => {
        if (data === "success") {
            const successMessage = document.getElementById('feedback-message');
            successMessage.style.display = 'block';
            setTimeout(hideSuccessMessage, 2000);
            currentIndex += 25;
            displayNextBatch();
        } else {
            const noSuccessMessage = document.getElementById('feedback-message-bad');
            noSuccessMessage.style.display = 'block';
            console.error("Error processing terms");
        }
    })
    .catch(error => {
        console.error("Error: ", error);
    });
};

const hideSuccessMessage = () => {
  const successMessage = document.getElementById('feedback-message');
  successMessage.style.display = 'none';
 }

function generateCheckboxes(data) {
  const tableBody = document.querySelector('#terms-table tbody');
  tableBody.innerHTML = '';

  if ((data.length === 1 && data[0].length === 0) || (data.length === 0)) {
    // Display message if no terms to check
    const noTermsMessage = document.getElementById('no-action-message');
    noTermsMessage.style.display = 'block';

    const tableHead = document.querySelector('#terms-table thead');
    tableHead.style.display = 'none';
    
    const submitButton = document.querySelector('.submit-button');
    submitButton.style.display = 'none';

    return;
  }

  data.forEach((row, index) => {
    const tableRow = document.createElement('tr');

    // Checkboxes
    const checkboxCell = document.createElement('td');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `term${index}`;
    checkbox.name = `term${index}`;
    checkbox.value = JSON.stringify(row);
    checkbox.checked = true;
    checkboxCell.appendChild(checkbox);
    tableRow.appendChild(checkboxCell);

    // Swe lemma
    const sweLemmaCell = document.createElement('td');
    sweLemmaCell.textContent = row.swe_lemma || '';
    tableRow.appendChild(sweLemmaCell);

    // Eng lemma
    const engLemmaCell = document.createElement('td');
    engLemmaCell.textContent = row.eng_lemma || '';
    tableRow.appendChild(engLemmaCell);

    // Swe inf
    const sweInfCell = document.createElement('td');
    sweInfCell.textContent = row.swedish_inflections || '';
    tableRow.appendChild(sweInfCell);

    // Eng inf
    const engInfCell = document.createElement('td');
    engInfCell.textContent = row.english_inflections || '';
    tableRow.appendChild(engInfCell);

    const srcCell = document.createElement('td');
    srcCell.textContent = row.src || '';
    tableRow.appendChild(srcCell);

    const posCell = document.createElement('td');
    posCell.textContent = row.agreed_pos || '';
    tableRow.appendChild(posCell);

    // Swe lemma
    const autOK = document.createElement('td');
    autOK.textContent = (row.status === 'automatically verified') ? 'JA':'NEJ';
    tableRow.appendChild(autOK);

    tableBody.appendChild(tableRow);
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
  const lines = jsonlContent.trim().split('\n');
  termsList = lines.map(line => JSON.parse(line));
  displayNextBatch();
}

function displayNextBatch(){
  const nextBatch = termsList.slice(currentIndex, currentIndex + 25);
  generateCheckboxes(nextBatch);
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