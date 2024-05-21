const uploadFunction = (swe_term, eng_term, file, src, contact) => {
    console.log("swe term");
    console.log(swe_term);

    console.log("eng term");
    console.log(eng_term);

    console.log("file");
    console.log(file);

    console.log("source");
    console.log(src);

    console.log("contact");
    console.log(contact);
}

const validateAndUpload = () => {
    const swe_term = document.getElementById('swe_term').value;
    const eng_term = document.getElementById('eng_term').value;
    const file = document.getElementById('term_file').files[0];
    const src = document.getElementById('src').value;
    const contact = document.getElementById('contact').value;
    const srcError = document.getElementById('src-error');

    if (!src) {
        srcError.style.display = 'inline';
        return;
    } else {
        srcError.style.display = 'none';
    }

    uploadFunction(swe_term, eng_term, file, src, contact);
}

let language = 'swe';

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
    
    document.querySelector('.info-container').innerHTML = '<p>Thank you for your contribution!</p><p>You can choose to either upload a single term pair in the fields below, or to upload a csv-file on the following format:</p><p>english_term1,swedish_term1<br>english_term2,swedish_term2<br>....</p><p>To make it easier you can download an outline for the csv-file here:</p><a href="files/outline.csv" download="outline.csv">Download outline (outline.csv)</a><p>In the form there is two fields for source and contact information. Source is a mandatory field, where it should be specified where the terms are gathered from. Contact information is optional, and it can for example be an email address.</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Upload single term pair:</p><input type="text" class="upload-input" id="swe_term" placeholder="Swedish term..."><input type="text" class="upload-input" id="eng_term" placeholder="English term..."><p>Upload file:</p><input type="file" class="upload-file" id="term_file"><span id="src-error" class="error-message" style="color: red; display: none;">Källa är obligatoriskt</span><input type="text" class="upload-input" id="src" placeholder="Source..." required><input type="text" class="upload-input" id="contact" placeholder="Contact information..."><button class="submit-button" onclick="validateAndUpload()">Ladda upp</button>';
}

const switchToSwedish = () => {
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';
    
    document.querySelector('.info-container').innerHTML = '<p>Tack för ditt bidrag!</p><p>Du kan välja att antingen ladda upp ett enskilt termpar i nedan fält, eller ladda upp en csv-fil på följande format:</p><p>engelsk_term1,svensk_term1<br>engelsk_term2,svensk_term2<br>....</p><p>För att underlätta kan du ladda ner en mall för csv-filen här:</p><a href="files/outline.csv" download="outline.csv">Ladda ner mall (outline.csv)</a><p>I formuläret finns två fält för källa och kontaktuppgifter. Källa är ett obligatoriskt fält, där det ska anges var termparet är hämtat från. Kontaktuppgifter är frivilligt, och kan exempelvis vara en mailadress.</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Ladda upp ett enskilt termpar:</p><input type="text" class="upload-input" id="swe_term" placeholder="Svensk term..."><input type="text" class="upload-input" id="eng_term" placeholder="Engelsk term..."><p>Ladda upp fil:</p><input type="file" class="upload-file" id="term_file"><span id="src-error" class="error-message" style="color: red; display: none;">Källa är obligatoriskt</span><input type="text" class="upload-input" id="src" placeholder="Källa..." required><input type="text" class="upload-input" id="contact" placeholder="Kontaktuppgifter..."><button class="submit-button" onclick="validateAndUpload()">Ladda upp</button>';
}
