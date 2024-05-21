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
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Computing Terms';
    
    // Change info text
    document.querySelector('.info-container').innerHTML = '<p>Info on uploading:</p><p>Thank you for your contribution!</p><p>You can choose to either upload a single term pair directly (one at a time) in the field below, or upload a txt-file on the following format:</p><p>english_term1,swedish_term1<br>english_term2,swedish_term2<br>....</p>';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Data term...');
}

const switchToSwedish = () => {
    // Change logo text
    document.querySelector('.logo-main').textContent = 'STUNDA';
    document.querySelector('.logo-sub').textContent = 'Swedish Technical University Network for Computing Terms';
    
    // Change info text
    document.querySelector('.info-text p').innerHTML = 'Stunda is a network for Sweden\'s technical universities aimed at promoting efficient technical communication in Swedish within higher education, primarily by working with discipline-specific terminology. Read more <a href="https://writing.chalmers.se/stunda/" target="blank">here</a>. For advanced search, see <a href="https://spraakbanken.gu.se/karp/tng/?mode=stunda&lexicon=stunda&show=stunda:01GX3DS1AKX7YZVYR6F5V8VZS6">KARP</a>.';
    
    // Change button text
    document.querySelector('.search-button').textContent = 'Search';

    // Change placeholder text
    document.getElementById('search-input').setAttribute('placeholder', 'Data term...');
}
