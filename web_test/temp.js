


function getTermsFromKarp(language, query_mode, searchString) {
    // Format the search string into the URL
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${language}.lemma|"${searchString}"))&from=0&size=25`;

    // Make the GET request using fetch()
    return fetch(apiUrl)
      .then(response => {
        // Check if the response is OK (status code 200)
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        // Parse the JSON response
        return response.json();
      })
      .then(data => {
        const dataList = [];
        data.hits.forEach(hit => {

            const new_entry = {
                swedishLemma: hit.entry.swe.lemma,
                englishLemma: hit.entry.eng.lemma,
                source: [hit.entry.src],
                pos: [hit.entry.pos],
                swedishInflections: hit.entry.swe.inflection ?? [],
                englishInflections: hit.entry.eng.inflection ?? [],
                alternativeTranslations: hit.entry.synonyms ?? []
            }

            dataList.push(new_entry);
          });
        return dataList;
      })
      .catch(error => {
        // Handle any errors that occur during the fetch
        console.error('There was a problem with the fetch operation:', error);
        return [];
      });
  }


let language = "swe";
let searchString = "test";
let query_mode = "startswith";

getTermsFromKarp(language, query_mode, searchString).then(dataList => {
    console.log(dataList);
}).catch(error => {
    console.error('Error:', error);
});
