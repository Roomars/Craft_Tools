# Craft Tools

Strumenti e dati per progettare build Minecraft a blocchi verificati, usati dalla
skill Claude `build-minecraft`.

**Visualizzatore live**: https://roomars.github.io/Craft_Tools/

## Struttura

```
Craft_Tools/
├── index.html              → elenco build (homepage GitHub Pages)
├── viewer.html              → visualizzatore 3D/sezioni, generico: legge un build.json via ?b=...
├── database/
│   └── minecraft_blocks_java_26.1.json   → database ufficiale blocchi (Java 26.1, 1168 blocchi:
│                                            nome EN/IT, forma, altezza, colore da texture reali)
└── builds/
    └── <nome-build>/
        ├── build.json       → dati puri della build (dimensioni, palette, livelli, edifici)
        └── README.md        → descrizione, conteggi, versione database usata
```

## Database blocchi

Ogni blocco riporta: `id`, `name_en`, `name_it`, `shape`, `height` (e `heights`/
`y_extent_by_property` quando lo stato cambia l'altezza), `color` (colore medio
dalla texture ufficiale, con tint di bioma applicato dove serve),
`height_source` (`model`/`collision`/`mixed`/`none`).

La skill `build-minecraft` scarica questo file a ogni sessione e non usa mai
un blocco che non vi compare.

## Aggiungere una build

1. Generare `build.json` da uno script Python che legge il database e produce
   il modello dati (`title`, `dims`, `order`, `palette`, `buildings`, `layers`,
   `facing`, `start`).
2. Salvarlo in `builds/<nome>/build.json` con un `README.md` a fianco.
3. Aggiungere una voce in `index.html`.

## Copyright

Il database salva solo **colori medi calcolati** dalle texture ufficiali di
Minecraft (Mojang/Microsoft), non le texture stesse: nessun asset originale è
ridistribuito in questo repository.
