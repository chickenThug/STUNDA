function getTermsFromKarp(field, query_mode, searchString) {
    // Format the search string into the URL
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${field}|"${searchString}"))&from=0&size=100`;
    // Make the GET request using fetch()
    return fetch(apiUrl)
      .then(response => {
        // Check if the response is OK (status code 200)
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .catch(error => {
        // Handle any errors that occur during the fetch
        console.error('There was a problem with the fetch operation:', error);
        return [];
      });
}

async function search(language, searchString) {

    let languageLemma = "";
    let oppositeLang = "";
    let oppositeLemma = "";
    if (language === "swe") {
        languageLemma = "swedishLemma";
        oppositeLemma = "englishLemma";
        oppositeLang = "eng";
    }
    else if (language === "eng") {
        languageLemma = "englishLemma";
        oppositeLemma = "swedishLemma";
        oppositeLang = "swe";
    }
    else {
        throw new Error(`Unknown language '${language}': can only accept 'swe' or 'eng'.`);
    }

    let matches = await getTermsFromKarp(`${language}.lemma`, "startswith", searchString);

    const entries = {};
    console.log("before");
    matches.hits.forEach(hit => {
        const key = hit.entry[language].lemma + ";" + hit.entry.pos;
        if (!entries[key]) {
            // If the lemma doesn't exist in entries, create a new entry
            entries[key] = {
                id: hit.id,
                swedishLemma: hit.entry.swe.lemma,
                englishLemma: hit.entry.eng.lemma,
                source: hit.entry.src.split(", "),
                pos: [hit.entry.pos],
                swedishInflections: hit.entry.swe.inflection ?? [],
                englishInflections: hit.entry.eng.inflection ?? [],
                alternativeTranslations: hit.entry.synonyms ?? []
            };
        } else {
            let sources_old = entries[key].source;
            let sources_new = hit.entry.src.split(", ");

            if (sources_old.length < sources_new.length) {
                let opposite_lemma = entries[key][oppositeLemma];
                let old_translations = entries[key].alternativeTranslations;
                entries[key] = {
                    id: hit.id,
                    swedishLemma: hit.entry.swe.lemma,
                    englishLemma: hit.entry.eng.lemma,
                    source: hit.entry.src.split(", "),
                    pos: [hit.entry.pos],
                    swedishInflections: hit.entry.swe.inflection ?? [],
                    englishInflections: hit.entry.eng.inflection ?? [],
                    alternativeTranslations: hit.entry.synonyms ?? []
                };
                for (const synonym in old_translations) {
                    entries[key].alternativeTranslations.push(synonym)
                }
                entries[key].alternativeTranslations.push(`${opposite_lemma} (${sources_old})`);
            }
            else {
                entries[key].alternativeTranslations.push(`${hit.entry[oppositeLang].lemma} (${hit.entry.src})`);
            }
        }
      });
  
      // Convert the object back to an array
      let sortedEntries = Object.values(entries);
  
      // Sort to prioritize the exact match
      sortedEntries.sort((a, b) => {
          if (a[languageLemma] === searchString && b[languageLemma] !== searchString) {
              return -1;
          } else if (a[languageLemma] !== searchString && b[languageLemma] === searchString) {
              return 1;
          }
          return 0;
      });
      console.log(sortedEntries);
      return sortedEntries;
  }


search("swe", "test");

