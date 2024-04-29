const new_entry = {
  id: hit.id,
  swedishLemma: hit.entry.swe.lemma,
  englishLemma: hit.entry.eng.lemma,
  source: hit.entry.src.split(', '),
  pos: [hit.entry.pos],
  swedishInflections: hit.entry.swe.inflection ?? [],
  englishInflections: hit.entry.eng.inflection ?? [],
  alternativeTranslations: hit.entry.synonyms ?? []
}