**You:**

Du får nå oppgaver i et fag om geografiske informasjonssystem. Svar så godt du kan. 

Oppgave 1: 
a) Du skal bruke "map algebra" på eit rasterdatasett (utrekning rastercelle for rastercelle). Kva rekneoperasjonar kan du nytte når data er av typen:
i) nominell variabel
ii) intervall variabel
iii) ratio (forholds) variabel
iv) ordinal variabel

b) Ein kartprojeksjon kan ha ulike eigenskapar. Forklar kva det vil seie at ein kartprojeksjon er ekvidistant. Gje døme på eit typisk kart som nyttar ein ekvidistant projeksjon.

c) Når ein samlar inn data ved hjelp av satellittar og fjernmåling vert ein spektralsignatur brukt. Forklar kva ein spektralsignatur er, samt kva den kan brukast til.

------------------

**ChatGPT:**

Oppgave 1:
a) Når du bruker "map algebra" på et rasterdatasett, vil de ulike datatypene tillate ulike beregningsoperasjoner.

i) Nominell variabel: Denne typen data er kategorisk og uten noen bestemt rekkefølge. Man kan ikke utføre aritmetiske operasjoner som addisjon eller subtraksjon med nominelle variabler. Men man kan foreta sammenligningsoperasjoner for likhet (f.eks. hvor er cellene som har verdi 'skog'?).

ii) Intervall variabel: Dette er numeriske data hvor det er konstant mellomrom mellom verdiene, men det er ikke en naturlig nullpunkt. Du kan legge til og trekke fra disse verdiene, men multiplikasjon og divisjon kan ikke gi meningsfulle resultater. Temperatur (i Celsius eller Fahrenheit) er et eksempel på en intervall variabel.

iii) Ratio (forholds) variabel: Disse dataene er som intervallvariabler, men med et naturlig nullpunkt. Det betyr at du kan utføre alle aritmetiske operasjoner, inkludert multiplikasjon og divisjon, og de vil gi meningsfulle resultater. For eksempel, høyde over havet.

iv) Ordinal variabel: Dette er data som har en bestemt rekkefølge, men avstanden mellom verdiene er ikke konstant. Du kan sammenligne dem (f.eks. A er større enn B), men aritmetiske operasjoner er ikke nødvendigvis meningsfulle.

b) En ekvidistant kartprojeksjon er en projeksjon hvor avstandene mellom punkter er konstant over hele kartet i en eller flere retninger. Med andre ord, kartet bevarer avstander, men kan forvrenge andre egenskaper som vinkler eller areal. Et eksempel på en slik projeksjon er den azimutale ekvidistante projeksjonen, som ofte brukes til å vise flyruter fra et bestemt punkt.

c) En spektralsignatur er et sett med karakteristiske verdier som identifiserer et materiale basert på dens reflektanse eller emittance over en rekke bølgelengder i det elektromagnetiske spekteret. Når satellitter eller andre fjernmålingsinstrumenter samler inn data, kan de registrere hvordan ulike materialer reflekterer eller emitterer energi over et spektrum av bølgelengder. Ved å analysere disse signaturer kan forskere identifisere forskjellige materialer eller objekter på jordens overflate. Dette er spesielt nyttig for å skille mellom ulike typer vegetasjon, jordtyper, vann, urbane strukturer, og mer.



------------------

**You:**

Svar på oppgave a) igjen, hvor du kun oppgir regneoperasjoner som '=', '<>' og '+', osv.

------------------

**ChatGPT:**

Oppgave 1:
a) Basert på datatypene:

i) Nominell variabel: '=', '<>' (likhet og ulikhet)

ii) Intervall variabel: '+', '-', '=', '<>', '>', '<' (addisjon, subtraksjon, likhet, ulikhet, større enn, mindre enn)

iii) Ratio (forholds) variabel: '+', '-', '*', '/', '=', '<>', '>', '<' (addisjon, subtraksjon, multiplikasjon, divisjon, likhet, ulikhet, større enn, mindre enn)

iv) Ordinal variabel: '=', '<>', '>', '<' (likhet, ulikhet, større enn, mindre enn)



------------------

**You:**

Oppgave 2: 

Du jobbar som GIS-konsulent i ein kommune, og har fått i oppdrag å finne ein del informasjon i samband med kommunevalet 2019. I denne oppgåva skal du skisser kva GIS-metodar du vil bruke for å løyse dei ulike deloppgåvene. Du må òg skissere kva data du har bruk for, samt kvar du eventuelt kan skaffe desse.

a) Du skal finne ut kor mange husvære (brukseiningar) det er innafor kvar valkrins (eit hus kan ha fleire husvære).

b) Du skal finne gjennomsnittsavstanden frå alle bygningar til vallokalet (luftlinje).

c) Korleis vil du gå fram, og kva må du tenkje på, viss du skal finne avstanden mellom ein bygning og vallokalet langs ein veg?

d) Kva kartografiske verkemiddel vil du bruka for å vise korleis husværa fordeler seg innan ein valkrins? Grunngje svaret.

------------------

**ChatGPT:**

Oppgave 2:

a) **Husvære innenfor hver valkrins**:


- **Metode**: Overlay-analyse, ofte kjent som "intersect" i GIS-programvare.
- **Data**: Jeg trenger et datasett over alle husvære (brukseiningar) samt en geografisk inndeling av valkrinsene.
- **Kilde**: Kommunens bygningsregister eller Matrikkelen for informasjon om brukseiningar. Valgkretsdata kan skaffes fra kommunens karttjeneste eller fra Kartverket.

b) **Gjennomsnittsavstand fra bygningene til vallokalet (luftlinje)**:


- **Metode**: Avstandsoperasjon eller "Euclidean distance" i GIS-verktøy.
- **Data**: Posisjonen til alle bygninger og plasseringen av vallokaler.
- **Kilde**: Bygningsdata kan hentes fra kommunens bygningsregister eller Matrikkelen, mens valglokaler kan være tilgjengelige fra kommunen eller valgadministrasjonen.

c) **Avstand mellom bygning og vallokale langs vei**:


- **Metode**: Nettverksanalyse, ofte kalt "shortest path" eller "routing" i GIS-verktøy.
- **Data**: Posisjonen til bygningene, vallokalenes plassering, og et datasett som representerer vegnettet inkludert attributtinformasjon om veiklasser, fartsgrenser, osv.
- **Kilde**: Vegdata kan hentes fra Nasjonalt vegregister eller Vegvesenet. Bygning og vallokaler som nevnt tidligere.
- **Hensyn**: Man må ta hensyn til faktiske veiruter, veistengninger, og potensielle barrierer.

d) **Kartografiske verktøy for å vise fordelingen av husvære innen en valkrins**:


- **Metode**: Tematisk kartlegging.
- **Verkemiddel**:
   - Kanskje en **kortone** (også kjent som fargekoding) der ulike farger representerer antall husvære. For eksempel kan områder med høy konsentrasjon av husvære ha en mørkere farge, mens de med færre husvære har en lysere farge.
   - **Punkt-symboler** kan også brukes, hvor størrelsen på punktet representerer antall husvære i en bestemt lokasjon.

<li>**Grunngiving**: Kortonekart gir et klart visuelt bilde av tettheten og fordelingen av husvære over en valkrins. Dette gir en rask forståelse av hvilke områder som har høyere eller lavere konsentrasjoner av husvære. Punkt-symboler kan være nyttige for å vise eksakte plasseringer, men kan være mindre leselige i områder med høy tetthet. Valget av metode avhenger av hva som er mest hensiktsmessig for målgruppen og formålet med kartet.

------------------

**You:**

Oppgave 3: 

a) Du skal finne ut kor mange husvære (brukseiningar) det er innafor kvar valkrins (eit hus kan ha fleire husvære).
b) Du skal finne gjennomsnittsavstanden frå alle bygningar til vallokalet (luftlinje).
c) Korleis vil du gå fram, og kva må du tenkje på, viss du skal finne avstanden mellom ein bygning og vallokalet langs ein veg?
d) Kva kartografiske verkemiddel vil du bruka for å vise korleis husværa fordeler seg innan ein valkrins? Grunngje svaret.

------------------

**ChatGPT:**

Oppgave 3:

a) **Husvære innenfor hver valkrins**:


- **GIS-metode**: Spatial join eller overlay-analyse.
- **Data nødvendig**: Datasett over alle husvære (brukseiningar) og geografisk inndeling av valkrinsene.
- **Kilde**: Kommunens bygningsregister eller Matrikkelen for informasjon om brukseiningar. Valgkretsdata kan hentes fra kommunens karttjeneste eller fra Kartverket.

b) **Gjennomsnittsavstand fra bygningene til vallokalet (luftlinje)**:


- **GIS-metode**: Punkt-til-punkt avstandsberegning.
- **Data nødvendig**: Posisjonen til alle bygninger og plasseringen av vallokaler.
- **Kilde**: Bygningsdata fra kommunens bygningsregister eller Matrikkelen, mens informasjon om valglokaler fra kommunen eller valgadministrasjonen.

c) **Avstand mellom bygning og vallokale langs vei**:


- **GIS-metode**: Nettverksanalyse med fokus på shortest path/routing.
- **Data nødvendig**: Posisjonen til bygningene, vallokalenes plassering, og detaljert vegnett datasett.
- **Kilde**: Vegdata kan hentes fra Nasjonalt vegregister eller Vegvesenet. Bygning og vallokalenes data som tidligere nevnt.
- **Hensyn**: Veiens tilstand (om den er åpen/stengt), veitype (gangsti, hovedvei osv.), og andre potensielle barrierer som kan påvirke valg av rute.

d) **Kartografiske verktøy for fordeling av husvære innen en valkrins**:


- **GIS-metode**: Tematisk kartlegging.
- **Verkemiddel**:
   - **Kortonekart**: Dette er et fargekart hvor hver farge representerer et visst antall husvære. F.eks. kan mørkere farger representere områder med høy konsentrasjon av husvære, mens lysere farger representerer lavere konsentrasjoner.
   - Alternativt, **punkt-symboler** der hvert punkt representerer et husvære, med størrelsen eller fargen på punktet som varierer basert på antall.

<li>**Grunngiving**: Kortonekart gir et klart visuelt bilde av hvor mange husvære det er i ulike deler av en valkrins. Det gir et raskt overblikk over hvor de tettest befolkede områdene er. Punkt-symboler kan gi mer presis informasjon om nøyaktige plasseringer, men kan bli uleselige i områder med høy tetthet. Valget av verktøy avhenger av målgruppen og formålet med kartet.

------------------

**You:**

<button type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="radix-:rao:" data-state="closed"><img alt="Uploaded image" loading="lazy" width="209" height="193" decoding="async" data-nimg="1" class="max-w-full transition-opacity duration-300 opacity-100" src="https://files.oaiusercontent.com/file-LZPQjjv8CYanWxprWS2CaH1V?se=2023-10-30T20%3A00%3A25Z&amp;sp=r&amp;sv=2021-08-06&amp;sr=b&amp;rscc=max-age%3D3599%2C%20immutable&amp;rscd=attachment%3B%20filename%3Dimage.png&amp;sig=mTONq9H6m97yky2QCQyg7csrroxqGt75LpnLOEhfqLI%3D" style="color: transparent;"></button>Oppgave 3: 

a) I eit kart skal du framstille ulike mengder (vekt) av eit fenomen ved hjelp av skalerte sirklar. Du skal utforme kartet slik at mengdene visuelt sett vert oppfatta riktig i høve til einannan. Foreslå kva radius det kan vere i kvar av desse sirklane (høvet mellom dei 4 radiane må vere riktig):
i) 360 tonn
ii) 22 tonn
iii) 220 tonn
iv) 430 tonn

b) Kva er eit prikkekart, og kva må ein ta omsyn til når ein skal utforme eit prikkekart?

c) Ved komprimering av rasterdata kan ein t.d. nytte "chain-code".
Vis korleis figuren på vedlagt bilde kan lagrast ved hjelp av "chain-code".

------------------

**ChatGPT:**

Oppgave 3:

a) **Skalerte sirklar**:
For å skape riktig oppfatning av forskjellige mengder ved hjelp av skalerte sirklar, bør man skalere arealet av sirklene i stedet for radiusen. Arealet av en sirkel er gitt ved <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>A</mi><mo>=</mo><mi>π</mi><msup><mi>r</mi><mn>2</mn></msup></mrow><annotation encoding="application/x-tex">A = \pi r^2</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.6833em;">A<span class="mspace" style="margin-right: 0.2778em;">=<span class="mspace" style="margin-right: 0.2778em;"><span class="strut" style="height: 0.8141em;"><span class="mord mathnormal" style="margin-right: 0.03588em;">π<span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.8141em;"><span style="top: -3.063em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2.

La oss finne en skaleringsfaktor ved å bruke den største verdien, 430 tonn, som referanse. La oss si at 430 tonn tilsvarer en sirkel med en radius på <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>1</mn></msub></mrow><annotation encoding="application/x-tex">r_1</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1​<span class="vlist" style="height: 0.15em;">. Så for 430 tonn har vi:
<math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>A</mi><mn>1</mn></msub><mo>=</mo><mi>π</mi><msubsup><mi>r</mi><mn>1</mn><mn>2</mn></msubsup></mrow><annotation encoding="application/x-tex">A_1 = \pi r_1^2</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.8333em; vertical-align: -0.15em;">A<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: 0em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1​<span class="vlist" style="height: 0.15em;"><span class="mspace" style="margin-right: 0.2778em;">=<span class="mspace" style="margin-right: 0.2778em;"><span class="strut" style="height: 1.0622em; vertical-align: -0.2481em;"><span class="mord mathnormal" style="margin-right: 0.03588em;">π<span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.8141em;"><span style="top: -2.4519em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1<span style="top: -3.063em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2​<span class="vlist" style="height: 0.2481em;">

For en annen verdi, for eksempel 360 tonn:
<math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>A</mi><mn>2</mn></msub><mo>=</mo><mrow><mo fence="true">(</mo><mfrac><mn>360</mn><mn>430</mn></mfrac><mo fence="true">)</mo></mrow><msub><mi>A</mi><mn>1</mn></msub></mrow><annotation encoding="application/x-tex">A_2 = \left(\frac{360}{430}\right) A_1</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.8333em; vertical-align: -0.15em;">A<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: 0em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2​<span class="vlist" style="height: 0.15em;"><span class="mspace" style="margin-right: 0.2778em;">=<span class="mspace" style="margin-right: 0.2778em;"><span class="strut" style="height: 1.2em; vertical-align: -0.35em;"><span class="mopen delimcenter" style="top: 0em;">(<span class="vlist" style="height: 0.8451em;"><span style="top: -2.655em;"><span class="pstrut" style="height: 3em;">430<span style="top: -3.23em;"><span class="pstrut" style="height: 3em;"><span class="frac-line" style="border-bottom-width: 0.04em;"><span style="top: -3.394em;"><span class="pstrut" style="height: 3em;">360​<span class="vlist" style="height: 0.345em;"><span class="mclose delimcenter" style="top: 0em;">)<span class="mspace" style="margin-right: 0.1667em;">A<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: 0em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1​<span class="vlist" style="height: 0.15em;">
<math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>A</mi><mn>2</mn></msub><mo>=</mo><mi>π</mi><msubsup><mi>r</mi><mn>2</mn><mn>2</mn></msubsup></mrow><annotation encoding="application/x-tex">A_2 = \pi r_2^2</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.8333em; vertical-align: -0.15em;">A<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: 0em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2​<span class="vlist" style="height: 0.15em;"><span class="mspace" style="margin-right: 0.2778em;">=<span class="mspace" style="margin-right: 0.2778em;"><span class="strut" style="height: 1.0622em; vertical-align: -0.2481em;"><span class="mord mathnormal" style="margin-right: 0.03588em;">π<span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.8141em;"><span style="top: -2.4519em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2<span style="top: -3.063em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2​<span class="vlist" style="height: 0.2481em;">

Ved å sammenligne de to arealene kan vi finne <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>2</mn></msub></mrow><annotation encoding="application/x-tex">r_2</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">2​<span class="vlist" style="height: 0.15em;">. Samme metode kan brukes for å finne <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>3</mn></msub></mrow><annotation encoding="application/x-tex">r_3</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">3​<span class="vlist" style="height: 0.15em;"> for 220 tonn og <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>4</mn></msub></mrow><annotation encoding="application/x-tex">r_4</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">4​<span class="vlist" style="height: 0.15em;"> for 22 tonn.

Når vi har <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>1</mn></msub></mrow><annotation encoding="application/x-tex">r_1</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1​<span class="vlist" style="height: 0.15em;">, kan vi beregne de andre radiane ved å ta kvadratroten av det skalerte arealet.

Uten en spesifikk verdi for <math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>r</mi><mn>1</mn></msub></mrow><annotation encoding="application/x-tex">r_1</annotation></semantics></math><span class="katex-html" aria-hidden="true"><span class="strut" style="height: 0.5806em; vertical-align: -0.15em;"><span class="mord mathnormal" style="margin-right: 0.02778em;">r<span class="vlist" style="height: 0.3011em;"><span style="top: -2.55em; margin-left: -0.0278em; margin-right: 0.05em;"><span class="pstrut" style="height: 2.7em;">1​<span class="vlist" style="height: 0.15em;">, kan vi ikke gi eksakte tall for radiusen til de andre sirklene, men prosessen er som beskrevet ovenfor.

b) **Prikkekart**:
Et prikkekart er en type tematisk kart hvor individuelle punkter eller "prikker" representerer en bestemt mengde av et fenomen. Hver prikk på kartet representerer en bestemt mengde av dataelementet, som kan være salg, befolkning, produksjon, osv.

Når man utformer et prikkekart, må man ta hensyn til:


- **Valg av prikkstørrelse**: For stor eller for liten prikk kan forvirre tolkningen.
- **Prikkenes tetthet**: For tett plasserte prikker kan overlappe og gjøre kartet uleselig.
- **Bakgrunnskartets klarhet**: Det bør ikke være for mange unødvendige detaljer som kan distrahere fra prikkene.
- **Konsistens**: Hver prikk må representere samme mengde av fenomenet over hele kartet.

c) **Chain-code for komprimering**:
Chain-code er en metode for å representere en binær figur ved å registrere sekvensen av bevegelser rundt figuren. En vanlig tilnærming bruker 8 retninger, hvor hver retning får en unik kode.

Ut ifra det vedlagte bildet, kan vi starte fra et hjørnepunkt i figuren og begynne å spore figuren mot klokka ved å bruke chain-code. Imidlertid, uten en høyoppløselig versjon av bildet, kan chain-code-representasjonen være unøyaktig.

Vanligvis ville man spesifisere startpunktet og så notere en sekvens av tall som beskriver bevegelsen rundt figuren, hvor hvert tall representerer en bestemt retning (f.eks., 0 for opp, 1 for opp-høyre, 2 for høyre, osv.).

Basert på bildet du har gitt, ville en grov chain-code vært en sekvens som beskriver formen på figuren, men for å gi en nøyaktig chain-code, ville man trenge en mer detaljert versjon av figuren.



------------------

**You:**

Her er en representasjon av bildet i tekst: 

0000000
0111000
0111100
0111100
0111100
0111110
0000110
0000000

Rasterdataene er 7x7. Svar nå på oppgave c) på nytt.

------------------

**ChatGPT:**

Takk for den tekstlige representasjonen. La oss bruke den for å generere en chain-code.

For å representere chain-code, kan vi bruke følgende 8 retninger:

```<button class="flex ml-auto gizmo:ml-0 gap-2 items-center"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="icon-sm" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code</button>
7  0  1
6  x  2
5  4  3

```
Her starter vi fra det øverste venstre hjørnet av figuren og beveger oss mot klokken. La oss starte fra første punktet i figuren (1) i øverste rad.

Basert på representasjonen gitt:

```<button class="flex ml-auto gizmo:ml-0 gap-2 items-center"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="icon-sm" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code</button>
0000000
0111000
0111100
0111100
0111100
0111110
0000110
0000000

```
Chain-code blir (starter fra øverste venstre hjørnet av figuren):


- Begynn på (2,2).
- Gå ned (4): tre trinn
- Gå til høyre (2): tre trinn
- Gå opp (0): tre trinn
- Gå til høyre (2): ett trinn
- Gå ned (4): fire trinn
- Gå til venstre (6): fire trinn

Chain-code: `444, 222, 000, 2, 4444, 6666`

Merk: Dette er en av de mulige chain-codene for figuren basert på startpunkt og retning. Chain-code kan variere avhengig av hvilket punkt man starter fra og hvilken retning man velger.



------------------

**You:**

Oppgave 4: 

a) Forklar kort prinsippet for dei viktigaste innsamlingsmetodane for digitale terrengmodellar og sei noko om i kva samanheng dei ulike metodane vert nytta.

b) Ein digital terrengmodell består av registrerte punkt i terrengoverflata (koordinatar), samt ein interpolasjonsmetode for å finne overflata mellom dei registrerte punkta. Forklar oversiktleg korleis desse interpolasjonsmetodane fungerer:
i) Punktvis interpolasjon
ii) Lokale funksjonar

c) Punktfordelinga (diskretiseringsmønsteret) i ein digital terrengmodell kan variere. Mellom anna kan punkt lagrast langs karakteristiske bruddlinjer i terrenget (terrenglinjer), eller som "vilkårleg" fordelte punkt der terrenget endrar seg. I sistnemnde metode vert gjerne punkta knyta saman til eit nettverk av trekantar. Kva er fordelen med å kombinere desse to metodane?
Korleis vil du ta med terrenglinjer i ein trekantmodell?

------------------

**ChatGPT:**

Oppgave 4:

a) Prinsipp for innsamlingsmetoder for digitale terrengmodeller (DTM):


- **Fotogrammetri**: Denne metoden er basert på å ta bilder fra forskjellige vinkler (oftest fra fly eller satellitt) og deretter bruke disse bildene for å beregne høyden til terrengpunkter. Det er en tradisjonell metode for å lage DTMer og brukes ofte i sammenheng med topografisk kartografi.
- **LiDAR (Light Detection and Ranging)**: Dette er en fjernmålingsmetode der et fly med en laser skanner terrengoverflaten. LiDAR gir meget detaljerte og presise høydedata, og er spesielt nyttig i områder med tett vegetasjon. Det er mye brukt i skogbruk, flommodellering, og urban planlegging.
- **Radar**: Noen satellitter bruker radarbølger for å bestemme høyden på terrengoverflaten. Dette kan være spesielt nyttig i skydekte områder.

b) Interpolasjonsmetoder for DTM:

i) **Punktvis interpolasjon**: Her brukes verdien av kjente punkter for å estimere verdien av ukjente punkter. Dette kan gjøres med metoder som nærmeste nabo, bilinear eller kubisk konvolusjon.

ii) **Lokale funksjoner**: Dette er mer avanserte interpolasjonsteknikker som tar hensyn til en gruppe nærliggende punkter for å estimere verdien av et ukjent punkt. Eksempler kan være IDW (Inverse Distance Weighted) eller Kriging.

c) Ved å kombinere punkter lagret langs karakteristiske terrenglinjer med vilkårlig fordelte punkter, kan man oppnå en modell som både fanger opp skarpe terrengendringer (som klipper eller daler) og gir en generell overflateform i jevnere områder. Fordelen med denne kombinasjonen er at man får en mer detaljert og nøyaktig terrengmodell.

For å ta med terrenglinjer i en trekantmodell, vil man først og fremst sørge for at terrenglinjene blir representert som en serie av punkter i modellen. Når trekantnettverket (ofte kalt TIN - Triangulated Irregular Network) dannes, vil disse punktene sørge for at trekantene følger terrenglinjene, slik at brudd i terrenget blir korrekt representert.



------------------

