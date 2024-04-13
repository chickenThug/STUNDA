from utils import get_all, get_swe_inflections, add_inflections

every = get_all()

t = every['hits']

for s in t:
    current_id = s['id']
    entry = s['entry']
    swe_lemma = entry['swe']['lemma'].split()
    pos = entry['pos']
    aut = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NwLnNwcmFha2Jhbmtlbi5ndS5zZS9hdXRoL2p3dCIsImlhdCI6MTcxMjg0MjUwMSwiZXhwIjoxNzEyODg1NzAxLCJqdGkiOiJkZjFhMjVlZGMzM2Y0MGQxYTI4ZTQ4OTFhNzM1YWIxNSIsImlkcCI6Imh0dHBzOi8vbG9naW4uaWRwLmVkdWlkLnNlL2lkcC54bWwiLCJzdWIiOiJtdXB1Zy1iaWphdEBlZHVpZC5zZSIsImVtYWlsIjoiZWxvZmdAa3RoLnNlIiwic2NvcGUiOnsibGV4aWNhIjp7InN0dW5kYSI6MTB9fSwibGV2ZWxzIjp7IlJFQUQiOjEsIldSSVRFIjoxMCwiQURNSU4iOjEwMH19.eZE9sS8162ZQ6_v-peBwPUB-zxMdDYVxdZ7oLdsZrFmirl0CUPiFRwiaMFK_IaW1wmQuAk9_jTFrjmL_k7ZkosGC9Ly-MazaJmt-XaAZ72XftAUB5Yqw1xqDS-OSNE48pwnt4_p0Ule7afyChTnysSaTwDlP-lRoKtYnZO-41duuFaQc6sp2_7NKYofUhjQ51fgADqzBoI2TuAOGjIEBFWH8qSMoDAFhWcDCCtLJaU18hpTIFujTuQ2gbKqPqjYVMckGrHqOK_XGFYd4F21G8vVxNsXBAjBl-i_xx0OdhSeqs_X-h06B3-aH4LI8E6nqMXHBpkNYNfVdIe6k7uh4Zw'
    if len(swe_lemma) == 1 and pos == 'N':
        inflections = get_swe_inflections(swe_lemma)
        for element in inflections:
            if element['msd'] == 'pl indef nom':
                entry['swe']['inflection'] = [element['writtenForm'] + 'ty']
        
        print(entry)
        add_inflections(current_id, aut, entry)
        break