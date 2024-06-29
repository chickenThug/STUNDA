// Function for handling when the user tries to upload terms
const uploadFunction = (swe_term, eng_term, file, src, contact) => {
    let now = new Date();
    let dateString = now.toString();

    let uploadType = 'file';
    if (swe_term || eng_term ){
        uploadType = 'terms';
    }

    // Single term upload
    if (swe_term && eng_term){
        const termData = {engTerm: eng_term, sweTerm: swe_term, source: src}
        single_term_upload(termData);
    }

    // File upload
    const formData = new FormData();
    formData.append('csvfile', file);
    formData.append('source', src);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/stunda/term-upload', true); // The servlet responsible for file upload

    xhr.onload = function() {
        if (xhr.status === 200) {
            // Logging
            const data = {timestamp: dateString, uploadType: uploadType, successful: true}
            log_upload(data);

            const feedbackMessage = document.getElementById("feedback-message");
            feedbackMessage.style.display = 'block';
        } else {
            // Logging
            const data = {timestamp: dateString, uploadType: uploadType, successful: false}
            log_upload(data);

            // For when it is a bad search:
            const badfeedbackMessage = document.getElementById("feedback-message-bad");
            badfeedbackMessage.style.display = 'block';
        }
    };

    xhr.send(formData);
}

/* Function for validating the user inputs. 
If something is bad --> show appropriate error messages. Else --> call uploadFunction()*/
const validateAndUpload = () => {
    const feedbackMessage = document.getElementById("feedback-message");
    feedbackMessage.style.display = 'none';

    const badfeedbackMessage = document.getElementById("feedback-message-bad");
    badfeedbackMessage.style.display = 'none';

    // Extract all the values from the form
    const swe_term = document.getElementById('swe_term').value;
    const eng_term = document.getElementById('eng_term').value;
    const file = document.getElementById('term_file').files[0];
    const src = document.getElementById('src').value;
    const contact = document.getElementById('contact').value;
    const srcError = document.getElementById('src-error');
    const rights = document.getElementById('terms_checkbox').checked;
    const rightsError = document.getElementById('rights-error');
    const srcCommaError = document.getElementById('src-comma-error');

    if (!src && !rights) {
        srcError.style.display = 'inline';
        rightsError.style.display = 'inline';
        return;
    }
    else if (!src){
        srcError.style.display = 'inline';
        rightsError.style.display = 'none';
        return;
    }
    else if (!rights){
        if (src.includes(",")) {
            srcError.style.display = 'none';
            srcCommaError.style.display = 'inline'
            rightsError.style.display = 'inline';
            return;
        } else {
            rightsError.style.display = 'inline';
            srcError.style.display = 'none';
            srcCommaError.style.display = 'none'
            return;
        }
    }
    else {
        if (src.includes(",")) {
            srcCommaError.style.display = 'inline'
            srcError.style.display = 'none';
            rightsError.style.display = 'none';
            return;
        } else {
            srcError.style.display = 'none';
            rightsError.style.display = 'none';
            srcCommaError.style.display = 'none';
        }
    }

    uploadFunction(swe_term, eng_term, file, src, contact);
}

let language = 'swe';

// Function called when language button is pressed. Switches the language accordingly
const language_toggle = () => {
    const languageToggle = document.getElementById('language-toggle');
    if (languageToggle.alt === 'swe') {
        switchToSwedish();
        language = 'swe';
        languageToggle.alt = 'eng';
    } else {
        switchToEnglish();
        language = 'eng';
        languageToggle.alt = 'swe';
    } 
}

const switchToEnglish = () => {
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Computing Terms';
    
    document.querySelector('.info-container').innerHTML = '<p>Thank you for your contribution!</p><p>You can choose to either upload a single term pair in the fields below, or to upload a csv-file on the following format:</p><p>english_term1,swedish_term1<br>english_term2,swedish_term2<br>....</p><p>To make it easier you can download an outline for the csv-file here:</p><a href="files/outline.csv" download="outline.csv">Download outline (outline.csv)</a><p>In the form there is two fields for source and contact information. Source is a mandatory field, where it should be specified where the terms are gathered from. Contact information is optional, and it can for example be an email address.</p><p>If you want to search for terms you can do it at the <a href="https://folkets-lexikon.csc.kth.se/stunda/" target="blank">search page</a>. You can also read more about the project <a href="https://writing.chalmers.se/stunda/" target="blank">here</a>.</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Upload single term pair:</p><input type="text" class="upload-input" id="swe_term" placeholder="Swedish term..."><input type="text" class="upload-input" id="eng_term" placeholder="English term..."><p>Upload file:</p><input type="file" class="upload-file" id="term_file"><span id="src-error" class="error-message" style="color: red; display: none;">Source is mandatory</span><span id="src-comma-error" class="error-message" style="color: red; display: none;">It is not allowed with a comma in the source</span><input type="text" class="upload-input" id="src" placeholder="Source..." required><input type="text" class="upload-input" id="contact" placeholder="Contact information..."><span id="rights-error" class="error-message" style="color: red; display: none;">You have to approve the rights before upload</span><div><input type="checkbox" id="terms_checkbox"><label for="terms_checkbox">I give the rights for the terms to be uploaded publicly in STUNDA</label></div><button class="submit-button" onclick="validateAndUpload()">Upload</button>';

    document.querySelector('#feedback-message').innerHTML = 'Successful upload of terms. Thank you for your contribution!';

    document.querySelector('#feedback-message-bad').innerHTML = 'Unsuccessful upload of terms. Please try again later.'
}

const switchToSwedish = () => {
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';
    
    document.querySelector('.info-container').innerHTML = '<p>Tack för ditt bidrag!</p><p>Du kan välja att antingen ladda upp ett enskilt termpar i nedan fält, eller ladda upp en csv-fil på följande format:</p><p>engelsk_term1,svensk_term1<br>engelsk_term2,svensk_term2<br>....</p><p>För att underlätta kan du ladda ner en mall för csv-filen här:</p><a href="files/outline.csv" download="outline.csv">Ladda ner mall (outline.csv)</a><p>I formuläret finns två fält för källa och kontaktuppgifter. Källa är ett obligatoriskt fält, där det ska anges var termparet är hämtat från. Kontaktuppgifter är frivilligt, och kan exempelvis vara en mailadress.</p><p>Om du vill söka efter termer kan du göra det på <a href="https://folkets-lexikon.csc.kth.se/stunda/" target="blank">söksidan</a>. Det går också att läsa mer om projektet <a href="https://writing.chalmers.se/stunda/" target="blank">här</a>.</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Ladda upp ett enskilt termpar:</p><input type="text" class="upload-input" id="swe_term" placeholder="Svensk term..."><input type="text" class="upload-input" id="eng_term" placeholder="Engelsk term..."><p>Ladda upp fil:</p><input type="file" class="upload-file" id="term_file"><span id="src-error" class="error-message" style="color: red; display: none;">Källa är obligatoriskt</span><span id="src-comma-error" class="error-message" style="color: red; display: none;">Det är inte tillåtet med kommatecken i källan</span><input type="text" class="upload-input" id="src" placeholder="Källa..." required><input type="text" class="upload-input" id="contact" placeholder="Kontaktuppgifter..."><span id="rights-error" class="error-message" style="color: red; display: none;">Du måste godkänna rättigheterna innan uppladdning</span><div><input type="checkbox" id="terms_checkbox"><label for="terms_checkbox">Jag ger rättigheter till att angivna termer laddas upp publikt i STUNDA</label></div><button class="submit-button" onclick="validateAndUpload()">Ladda upp</button>';

    document.querySelector('#feedback-message').innerHTML = 'Lyckad uppladdning av termer. Tack för ditt bidrag!';

    document.querySelector('#feedback-message-bad').innerHTML = 'Uppladdning av termer gick inte. Vänligen försök igen vid senare tillfälle.'
}

// Function for calling the servlet handling the logging of the upload
function log_upload(data){
    fetch('/stunda/log-upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.error('Error logging upload:', error));
}

// Function for calling the servlet handling the single term upload
function single_term_upload(data){
    fetch('/stunda/single-term-upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .catch(error => console.error('Error uploading single terms:', error));
}