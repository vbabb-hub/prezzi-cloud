# Aruba Cloud: listino pubblico e listino Enterprise

Nel sito compaiono due provider distinti, perché Aruba ha due listini con prezzi diversi.

| | **Aruba Cloud** (pubblico) | **Aruba Cloud Enterprise** |
|---|---|---|
| Fonte | cloud.it/prezzi, letto il 27/10/2026 | "Listino per il Mercato Enterprise" v. ARB-11740-1, valido dal 03/08/2026 (enterprise.aruba.it), aggiornato ogni mese |
| Per chi | acquisto diretto online | enterprise e PA: servizi con qualifica ACN (ogni voce riporta ID e livello, per esempio IA-418 QC1) |
| Impegni | prezzo annuale (non il 3 anni) | 1 anno circa -10% sul mensile; 3 anni solo sui server dedicati |
| Ambito | compute, storage, rete, GPU on Demand | in più VPS, Virtual Data Center, Kubernetes, DBaaS, server dedicati con GPU, VMware, backup |
| IVA | esclusa | esclusa |

## Confronto sulle voci in comune (euro al mese, IVA esclusa)

| Cloud Server PRO | Pubblico | Enterprise | Differenza |
|---|---|---|---|
| O2A4 (2 vCPU / 4 GB) | 20,10 | 23,00 | +14% |
| O4A8 (4 / 8) | 31,20 | 41,70 | +34% |
| O8A16 (8 / 16) | 55,50 | 76,23 | +37% |
| O16A32 (16 / 32) | 152,60 | 153,87 | +1% |
| O2A8R (2 / 8) | 25,70 | 36,63 | +43% |
| O4A16R (4 / 16) | 41,60 | 65,00 | +56% |
| O8A32R (8 / 32) | 76,30 | 119,00 | +56% |

Con impegno a 1 anno (al mese): O2A4 19,50 contro 20,70; O4A8 30,33 contro 37,53; O8A16 53,92 contro 68,61; O16A32 148,08 contro 138,48; O2A8R 25,00 contro 32,96; O4A16R 40,42 contro 58,50; O8A32R 74,08 contro 107,10.

Block Storage (euro per GB al mese): Standard AZ 0,0365 contro 0,0438; Performance AZ 0,0657 contro 0,0803; Standard Regional 0,0584 contro 0,0730; Performance Regional 0,0949 contro 0,1168 (circa +20-25% sull'Enterprise).

GPU: il server con L40S costa 1.979,90 al mese sul pubblico (GPU on Demand) e 2.942,66 sull'Enterprise (AI-A110, 2 CPU EPYC 9124, 128 GB). La RTX 4080 Super costa 529,90 contro 1.011,38 (AI-A109). **Le configurazioni non sono identiche**: il confronto va fatto sulla scheda tecnica, non solo sul prezzo.

## Come leggere la differenza
- Il listino Enterprise è quello da usare per offerte a PA o enterprise con requisiti ACN; quello pubblico è un riferimento di mercato più basso.
- Sui Cloud Server PRO il divario non è costante: quasi nullo a 16 vCPU, fino a +56% sulle taglie con più RAM.
- Gli SLA dell'Enterprise sono dichiarati nel listino (Cloud Server PRO 99,95%, VPS 99,80%, Kubernetes 99,95% senza HA e 99,98% con HA, DBaaS 99,95%).
- I prezzi Enterprise sono "listino": gli sconti di convenzione o di gara non sono inclusi.
