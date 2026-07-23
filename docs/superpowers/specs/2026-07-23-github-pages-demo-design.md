# Design: GitHub Pages Demo for rdf-InContext

**Date:** 2026-07-23
**Status:** Approved

## Goal

Deploy a live, working demo of rdf-InContext to GitHub Pages at `https://surf-ori.github.io/incontext/`, served from the `/docs` folder on `main`. The demo uses the bundled example data (ESCAPE project, University of Twente) and is wrapped in a page that gives visitors context about Enhanced Publications and OAI-ORE.

## What changes

### 1. Source fix — remove synchronous XHR

`trunk/Source/Scripts/utils/rdfxmlparser.js`: remove `async: false` from the `$.ajax()` call. The success callback is already in place; making the call async requires no other changes.

### 2. Build script

New file: `scripts/build.sh`

Concatenates the 20 JS source files in the order defined by `trunk/build.xml`, strips UTF-8 BOM characters, and writes to `docs/visualizer.js`. No minification (no Java dependency; this is a demo). The concatenation order is:

```
dependencies/jquery-1.4.4.js
dependencies/jquery.address-1.3.1.min.js
dependencies/jquery.effects.core.js
dependencies/rdflib/util.js
dependencies/rdflib/uri.js
dependencies/rdflib/term.js
dependencies/rdflib/rdfparser.js
dependencies/rdflib/identity.js
visualizer.js
utils/htmlpopup.js
utils/rdfxmlparser.js
framework/core.js
framework/sandbox.js
modules/syncdataconnector.js
modules/schemaconnector.js
modules/dataservice.js
modules/schemaservice.js
modules/htmldrawservice.js
modules/historymanager.js
modules/cloudservice.js
modules/navigationservice.js
modules/animationservice.js
domain/node.js
```

(The `rdflib/LICENSE` text file from `build.xml` is omitted — it is not JavaScript and would break parsing.)

### 3. `docs/` folder layout

```
docs/
  index.html          ← wrapper page (see below)
  visualizer.js       ← concatenated bundle (output of build.sh)
  Content/            ← copied from trunk/Source/Content/ (CSS + images)
  Example/            ← copied from trunk/Source/Example/ (RDF data + schema)
```

### 4. `docs/index.html` — wrapper page

Single self-contained HTML page. Structure:

- Page title: "InContext — RDF Visualiser for Enhanced Publications"
- Header with title and one-line description
- **What are Enhanced Publications?** — explains OAI-ORE compound objects, URI-addressable resources, relation recording in RDF, SURFshare programme context
- **About this demo** — describes the ESCAPE/University of Twente dataset shown; instructs the visitor to click nodes to navigate
- **Learn more** — citation and open-access link to *Emerging Standards for Enhanced Publications and Repository Technology* (van Godtsenhoven et al., 2009): `http://hdl.handle.net/1854/LU-1942496`
- `<div id="visualizer_canvas">` where the visualiser renders
- Script block initialising `VisualizerApp` with the bundled example data

Configuration passed to `VisualizerApp`:
- `dataUrl`: `Example/example_data.rdf`
- `schemaUrl`: `Example/example_schema.json`, `schemaFormat: "application/json"`
- `startObjectId`: `http://pof.tnw.utwente.nl/` (confirmed present in the data)
- `titleProperties`, `dontShowProperties`, annotation config — copied from `example_release.html`
- `useHistoryManager: true` (enables URL-based deep-linking to nodes)
- `debug: false` (no console noise in the live demo)

### 5. GitHub Pages configuration

In GitHub repo settings: **Pages → Source → Deploy from branch `main`, folder `/docs`**.

Live URL: `https://surf-ori.github.io/incontext/`

No GitHub Actions workflow needed.

## What does NOT change

- `trunk/` source tree — untouched except the one-line `async: false` removal
- `tags/` — untouched
- All existing metadata files (CLAUDE.md, LICENSE, .zenodo.json, CITATION.cff)
- jQuery version stays at 1.4.4 (bundled; `$.browser` and other legacy APIs work)

## Success criteria

1. `https://surf-ori.github.io/incontext/` loads without JS errors
2. The visualiser renders the ESCAPE graph centred on the University of Twente Physics of Fluids group
3. Clicking a node navigates to it and updates the browser URL hash
4. The wrapper text and book link are visible above the visualiser
