let currentIndex = 0;
let currentBatchSize = 25;
let termsList = [];

const ARRAY_FIELDS = ['synonyms', 'alternative_translations', 'swedish_inflections', 'english_inflections'];
const POS_OPTIONS = ['', 'N', 'NP', 'V', 'A', 'Ab'];

function uncheckAll() {
  const checkboxes = document.querySelectorAll('#term-verification input[type="checkbox"]');
  checkboxes.forEach(cb => { cb.checked = false; });
}

// Function for when the user presses verify terms
const verifyTerms = (nextBatchSize = 25) => {
  const rows = document.querySelectorAll('#terms-table tbody tr');
  const terms = [];

  rows.forEach(row => {
    const original = JSON.parse(row.dataset.original);
    const checkbox = row.querySelector('input[type="checkbox"]');
    const termData = { ...original };

    // Read editable cells
    row.querySelectorAll('[data-field]').forEach(cell => {
      const field = cell.dataset.field;
      const raw = (cell.tagName === 'SELECT' ? cell.value : cell.textContent).trim();
      if (ARRAY_FIELDS.includes(field)) {
        termData[field] = raw ? raw.split(',').map(s => s.trim()).filter(s => s) : [];
      } else {
        termData[field] = raw;
      }
    });

    termData.approved = checkbox.checked;
    terms.push(termData);
  });

  const username = sessionStorage.getItem('username');
  const payload = { username: username, terms: terms };

  const setButtonsDisabled = (disabled) => {
    document.getElementById('verify-button').disabled = disabled;
    document.getElementById('verify-more-button').disabled = disabled;
  };

  setButtonsDisabled(true);

  // Send approved and not approved terms to the servlet
  fetch('./handle-verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(response => response.text())
  .then(data => {
    if (data === "success") {
      const successMessage = document.getElementById('feedback-message');
      successMessage.style.display = 'block';
      setTimeout(hideSuccessMessage, 2000);
      currentIndex += currentBatchSize;
      displayNextBatch(nextBatchSize);
    } else {
      const noSuccessMessage = document.getElementById('feedback-message-bad');
      noSuccessMessage.style.display = 'block';
      console.error("Error processing terms");
    }
    setButtonsDisabled(false);
  })
  .catch(error => {
    console.error("Error: ", error);
    setButtonsDisabled(false);
  });
};

const hideSuccessMessage = () => {
  const successMessage = document.getElementById('feedback-message');
  successMessage.style.display = 'none';
}

// Helper: create an editable td
function editableCell(field, value) {
  const cell = document.createElement('td');
  cell.contentEditable = 'true';
  cell.dataset.field = field;
  if (Array.isArray(value)) {
    cell.textContent = value.join(', ');
  } else {
    cell.textContent = value || '';
  }
  return cell;
}

// Helper: create a pos select td
function posSelectCell(currentPos) {
  const cell = document.createElement('td');
  const select = document.createElement('select');
  select.dataset.field = 'agreed_pos';
  POS_OPTIONS.forEach(pos => {
    const option = document.createElement('option');
    option.value = pos;
    option.textContent = pos || '—';
    if ((currentPos || '') === pos) option.selected = true;
    select.appendChild(option);
  });
  cell.appendChild(select);
  return cell;
}

// Function for generating the table with the terms
function generateCheckboxes(data) {
  const tableBody = document.querySelector('#terms-table tbody');
  tableBody.innerHTML = '';

  // If there is no more terms to handle
  if ((data.length === 1 && data[0].length === 0) || (data.length === 0)) {
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
    tableRow.dataset.original = JSON.stringify(row);

    // Checkbox
    const checkboxCell = document.createElement('td');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `term${index}`;
    checkbox.checked = true;
    checkboxCell.appendChild(checkbox);
    tableRow.appendChild(checkboxCell);

    tableRow.appendChild(editableCell('swe_lemma', row.swe_lemma));
    tableRow.appendChild(editableCell('synonyms', row.synonyms));
    tableRow.appendChild(editableCell('eng_lemma', row.eng_lemma));
    tableRow.appendChild(editableCell('alternative_translations', row.alternative_translations));
    tableRow.appendChild(editableCell('swedish_inflections', row.swedish_inflections));
    tableRow.appendChild(editableCell('english_inflections', row.english_inflections));
    tableRow.appendChild(editableCell('src', row.src));
    tableRow.appendChild(editableCell('comment', row.comment));
    tableRow.appendChild(posSelectCell(row.agreed_pos));

    // Auto-verified (not editable)
    const autOK = document.createElement('td');
    autOK.textContent = (row.status === 'automatically verified') ? 'JA' : 'NEJ';
    tableRow.appendChild(autOK);

    tableBody.appendChild(tableRow);
  });
}

// Function to check if the user is logged in
function checkLoginStatus() {
  if (sessionStorage.getItem('loggedIn') !== 'true') {
    window.location.href = "login.html";
  }
}

// Function to parse the JSONL content from the file
function handleJSONLContent(jsonlContent) {
  const lines = jsonlContent.trim().split('\n');
  termsList = lines.map(line => JSON.parse(line));
  displayNextBatch();
}

// Function to display the terms in batches
function displayNextBatch(batchSize = 25) {
  const nextBatch = termsList.slice(currentIndex, currentIndex + batchSize);
  currentBatchSize = nextBatch.length;
  generateCheckboxes(nextBatch);
}

// Fetch JSONL file from server
async function fetchJSONL() {
  await fetch('./term-verification', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
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
