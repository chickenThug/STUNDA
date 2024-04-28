function getTermsFromKarp(field, query_mode, searchString) {
    // Format the search string into the URL
    const apiUrl = `https://spraakbanken4.it.gu.se/karp/v7/query/stunda?q=and(or(${query_mode}|${field}|"${searchString}"))&from=0&size=25`;

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
                id: hit.id,
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

function getLemmaByLanguageExactMatch(language, searchString) {
  const field = `${language}.lemma`
  return getTermsFromKarp(field, "equals", searchString)
}

function getLemmaByLanguageBeginsWith(language, searchString) {
  const field = `${language}.lemma`
  return getTermsFromKarp(field, "startswith", searchString)
}

function mergeResults(firstResultList, secondResultList) {
  const uniqueResults = new Map();

    // Add each item from the first result list to the Map
    firstResultList.forEach(item => {
        uniqueResults.set(item.id, item);
    });

    // Add each item from the second result list to the Map
    // This will automatically overwrite any duplicate ids from the first list
    secondResultList.forEach(item => {
        uniqueResults.set(item.id, item);
    });

    // Convert the Map values back to an array and return
    return Array.from(uniqueResults.values());
}

async function tryMerge() {
  let language = "swe";
  let searchString = "test";
  let query_mode = "startswith";
  let result1 = null;
  let result2 = null;
  try {
        result1 = await getLemmaByLanguageExactMatch(language, searchString);
        // You can now use 'result' here for further processing or return it
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    try {
      result2 = await getLemmaByLanguageBeginsWith(language, searchString);
      // You can now use 'result' here for further processing or return it
  } catch (error) {
      console.error('Error fetching data:', error);
  }
  console.log(mergeResults(result1, result2));
}






tryMerge();
