# Elementi
## Holt-Winters
0 < A, B, C < 1
- Più grandi -> adattamento rapido ai cambiamenti recenti
- Più piccoli -> algoritmo conservativo

Determinati tramite più piccola SSE

### SSE
`SSE = SUM[i = 1 -> m](y[i] - y^[i])^2`

### Livello
`l[x] = A*y[x] + (1 - A)*(l[x-1] + b[x-1])`

### Trend
`b[x] = B*(l[x] - l[x-1]) + (1 - B)*b[x-1]`

### Stagionale
`s[x] = C*(y[x] - l[x]) + (1 - C)*s[x-L]`

### Previsione
`y^[x+m] = l[x] + m*b[x] + s[x - L + 1 + ((m-1) % L)]`

Previsione di un numero arbitrario m di punti.

### Deviazione
`d[t] = C*|y[t] - y^[t]| + (1-C)*d[t-m]`
- Superiore `y^[t] - D*d[t-m]`
- Inferiore `y^[t] + D*d[t-m]`

Con 2 < D < 3 per le fasce di confidenza

## RSI
Quanto violentemente cambia segnale, interno del range, media mobile

`RSI = 100 * U/(U + D)`
- U = media rialzi sul periodo
- D = media discese sul periodo

# Idea
Modulo Python con
- inserimento nuovo valore
- estrapolazione valori
- costruzione grafici
- "addestramento" A, B, C di Holt-Winters in base a dati inseriti da misurazioni
- predizione punto arbitrario grazie a Holt-Winters
- ma anche possibilità di inserimento manuale dei parametri Holt-Winters
- calcolo RSI dato il range

Quindi con architettura per mantenimento serie temporale (banalmente array, ma bisogna forse considerare anche il caso di inserimento dati a intervalli irregolari o "buchi" nelle misurazioni, quindi forse meglio matrice timestamp->valore e timestamp preso automaticamente dal modulo quando richiamo metodo inserimento valore).

Il modulo si "auto-addestra" all'inserimento di un dato: prevede i prossimi e, all'inserimento del successivo, adatta A, B e C in modo da minimizzare la SSE.

-> flag per attivare-disattivare apprendimento?

## Aspetti
### Memorizzazione dei dati

Lascerei il problema al software che va a usare la nostra libreria. Questo perché ritengo sia meglio realizzare una funzionalità "semplice" (predizione e opzionale grafico) ed evitare un aspetto complesso come la manutenzione su file dei dati.

Il programma potrebbe estrapolare quindi dati da un pcap, un database rrd, un database SQL o quant'altro e usare la nostra API per produrre grafici e previsioni.

### Produzione grafici

Potremmo anche usare rrdgraphv o plot o altre librerie Python già pronte, senza ovviamente stare a scrivere niente da zero.

# Test
Analisi flusso dati per tot secondi e inserimento dati per tuning A, B, C.

Produrre grafici e misurare per verificare predizioni.

## Test possibili
- Flussi aperti da un host nell'arco della giornata
- Dati scambiati nell'arco della giornata
- Malware https://www.unb.ca/cic/datasets/ids-2018.html
