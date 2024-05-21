const someFunc = () => {
    console.log("klickat på knappen");
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
    // Change logo text
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Computing Terms';
    
    // Change info text
    document.querySelector('.info-container').innerHTML = '<p>Info about uploading:</p><p>Thank you for your contribution!</p><p>You can choose to either upload a single term pair directly (one at a time) in the field below, or upload a txt-file on the following format:</p><p>english_term1,swedish_term1<br>english_term2,swedish_term2<br>....</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Upload single term pair:</p><input type="text" class="upload-input" id="swe_term" placeholder="Swedish term..."><input type="text" class="upload-input" id="eng_term" placeholder="English term..."><p>Upload file:</p><input type="file" class="upload-file"><button class="submit-button" onclick="someFunc()">Upload</button>';
}

const switchToSwedish = () => {
    // Change logo text
    document.querySelector('.logo-sub').textContent = 'Sveriges Tekniska Universitets Nätverk för Datatermer';
    
    // Change info text
    document.querySelector('.info-container').innerHTML = '<p>Info om uppladdning:</p><p>Tack för ditt bidrag!</p><p>Du kan välja att antingen ladda upp ett enskilt termpar direkt (ett åt gången) i nedan fält, eller ladda upp en txt-fil på följande format:</p><p>engelsk_term1,svensk_term1<br>engelsk_term2,svensk_term2<br>....</p>';

    document.querySelector('.upload-container').innerHTML = '<p>Ladda upp ett enskilt termpar:</p><input type="text" class="upload-input" id="swe_term" placeholder="Svensk term..."><input type="text" class="upload-input" id="eng_term" placeholder="Engelsk term..."><p>Ladda upp fil:</p><input type="file" class="upload-file"><button class="submit-button" onclick="someFunc()">Ladda upp</button>';
}
