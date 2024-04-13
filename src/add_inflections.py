from utils import get_all, get_swe_inflections, add_inflections

every = get_all()

t = every['hits']

for s in t:
    current_id = s['id']
    entry = s['entry']
    swe_lemma = entry['swe']['lemma'].split()
    pos = entry['pos']
    aut = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NwLnNwcmFha2Jhbmtlbi5ndS5zZS9hdXRoL2p3dCIsImlhdCI6MTcxMzAxNDg5OSwiZXhwIjoxNzEzMDU4MDk5LCJqdGkiOiJkY2E2NDU4MDRhNGY0MDBkYTE5ZDkxZDhhY2Q0OTQ5NCIsImlkcCI6Imh0dHBzOi8vbG9naW4uaWRwLmVkdWlkLnNlL2lkcC54bWwiLCJzdWIiOiJtdXB1Zy1iaWphdEBlZHVpZC5zZSIsImVtYWlsIjoiZWxvZmdAa3RoLnNlIiwic2NvcGUiOnsibGV4aWNhIjp7InN0dW5kYSI6MTB9fSwibGV2ZWxzIjp7IlJFQUQiOjEsIldSSVRFIjoxMCwiQURNSU4iOjEwMH19.t0SEZgoW1ybYw1gEdytkK5W3C6EurSbr0MPz3llQDW4F4zWK4MCuoUHRa6w1Z6JvsFfAGcSsdTchCYYIp5iLYnUbI_p1mCQrW_gZTM4EQNhULg2WIqWEVs3qSXVhbmMkFwrJmE9C3Q-GZHbx0OgRfHmEekr6RG7T3GAx3Nd2Uf25O43wifZPFOj2r_SMhoWQ2p93do9AQI9Z58qdrfkz9BgNmWeoJNxVUjTfX1GAe9-YMnzCKHM96mwzSnn9egPd47-KdiQOg0Qsx2TZVyOuoRK9k7EiaGvY7mtqwBMzhhNJYzthiv_8KProOHHYE7GzGFNnE4FIP20zBOUDk5QeTw'
    if len(swe_lemma) == 1 and pos == 'N':
        inflections = get_swe_inflections(swe_lemma)
        for element in inflections:
            if element['msd'] == 'pl indef nom':
                entry['swe']['inflection'] = [element['writtenForm'] + 'ty']
        
        print(entry)
        print(current_id, " id")
        add_inflections(current_id, aut, entry)
        break