from utils import get_all, get_swe_inflections, add_inflections

every = get_all()

t = every['hits']

for s in t:
    current_id = s['id']
    entry = s['entry']
    swe_lemma = entry['swe']['lemma'].split()
    pos = entry['pos']
    aut = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NwLnNwcmFha2Jhbmtlbi5ndS5zZS9hdXRoL2p3dCIsImlhdCI6MTcxMzg2OTQ0MCwiZXhwIjoxNzEzOTEyNjQwLCJqdGkiOiJmNGFmMmNjZGE5Njg0ZTI0ODAxZDE5YjcxY2Q3ZWNlZSIsImlkcCI6Imh0dHBzOi8vbG9naW4uaWRwLmVkdWlkLnNlL2lkcC54bWwiLCJzdWIiOiJtdXB1Zy1iaWphdEBlZHVpZC5zZSIsImVtYWlsIjoiZWxvZmdAa3RoLnNlIiwic2NvcGUiOnsibGV4aWNhIjp7InN0dW5kYSI6MTB9fSwibGV2ZWxzIjp7IlJFQUQiOjEsIldSSVRFIjoxMCwiQURNSU4iOjEwMH19.KmPOjtafHnblqtVTYgFSi06sX-5djTKizxHvOwq7nHzjbZf3fPWmXaK8iZ9zBKWzc4jN6fpbxIT_Q7jEiZpykGE_phUiUbmKjwFHJfXlwNBfV6Z21lx1oJ09EDwAC8ztFWYEnmKofwe8_KVcL3ib47pQX2YjT-8cY7C1A-cSzT1btjQVXlNGRHzZ-N2Pz-Wc6VRAyViugJOpV6ohJ7OvELoEebjeIzkvJJJRxIH91H490fP79nzKlQE7nPvLP9OX_ZdIwaHKiQFKrzGJ7AJC06NBRy6KovARejFNuXx7suS1iEBCsLpZOMavrLG5Gcr8ig6fVWK3grPMwTp7DKMJkA'
    if len(swe_lemma) == 1 and pos == 'N':
        inflections = get_swe_inflections(swe_lemma)
        for element in inflections:
            if element['msd'] == 'pl indef nom':
                entry['swe']['inflection'] = [element['writtenForm'] + 'ty']
        
        print(entry)
        print(current_id, " id")
        add_inflections(current_id, aut, entry)
        break