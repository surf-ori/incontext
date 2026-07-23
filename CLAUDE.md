# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**rdf-InContext** is a client-side JavaScript visualisation widget for [Enhanced Publications](http://hdl.handle.net/1854/LU-1942496) — compound scholarly objects that link publications to datasets, images, and other resources via [OAI-ORE](https://www.openarchives.org/ore/) RDF. It was developed ~2011–2013 for [SURFfoundation](https://www.surf.nl/) as part of the SURFshare programme.

The visualiser renders an interactive "newspaper-style" cloud of RDF objects, letting users navigate between related resources by clicking. It is purely client-side: no server is needed to run it — only the RDF data is fetched remotely.

## Repository layout

```
trunk/Source/          ← current working code (develop here)
  example_source.html  ← run this in a browser to test (loads all .js files individually)
  example_release.html ← uses the pre-built visualizer_compiled_min.js
  Scripts/
    visualizer.js      ← entry point; defines VisualizerApp and wires modules
    framework/         ← Core (event bus + registry) and Sandbox (per-module API)
    modules/           ← 9 swappable service modules (see Architecture below)
    utils/             ← htmlpopup.js, rdfxmlparser.js
    domain/node.js     ← Node domain object
    dependencies/      ← jQuery 1.4.4, jquery.address, rdflib partial
  Content/             ← CSS (visualizer.css, visualizer-skin.css) and Images
  Example/             ← example_data.rdf, example_schema.json/.rdf

tags/release-1.0/      ← release snapshot v1.0
tags/release-1.1/      ← release snapshot v1.1 (latest stable)
trunk/Lib/             ← Ant build tools (YUI Compressor)
trunk/build.xml        ← Ant build: compiles + minifies all JS into visualizer_compiled_min.js
docs/                  ← wiki pages exported from Google Code (.wiki, .md)
```

## Running the visualiser

No install or build required for development. Open `trunk/Source/example_source.html` directly in a browser — it loads all scripts individually. Due to the RDF data fetch (`Example/example_data.rdf`) you need to serve it over HTTP:

```bash
python3 -m http.server 8080 --directory trunk/Source
# then open http://localhost:8080/example_source.html
```

The release build (`example_release.html`) uses `Scripts/visualizer_compiled_min.js` (pre-built; no live rebuild workflow expected for most dev tasks).

## Building the release bundle

Requires Java + Ant:

```bash
cd trunk
ant          # produces Scripts/visualizer_compiled.js and Scripts/visualizer_compiled_min.js
```

The Ant task concatenates and then runs YUI Compressor (`Lib/yuicompressor-2.4.2.jar`) over all source JS files.

## Architecture

The visualiser uses a **modular sandbox pattern** (Nicholas Zakas's scalable JS architecture): modules communicate only through a central event bus, never directly.

**Three-layer framework (`Scripts/framework/`):**
- `Core` — module registry, config store, event bus (`subscribe`/`notify`/`waitFor`)
- `Sandbox` — thin per-module façade that proxies Core without exposing it
- `VisualizerApp` (in `visualizer.js`) — public API; instantiates Core, registers modules, exposes `loadObject()` and `subscribe()` to the host page

**Nine service modules (`Scripts/modules/`):**

| Module | Role |
|---|---|
| `SyncDataConnector` | AJAX-fetches RDF/XML or RDF/JSON from `dataUrl` |
| `SchemaConnector` | AJAX-fetches schema from `schemaUrl` |
| `DataService` | Maps raw RDF triples → `Node` domain objects; resolves base class types |
| `SchemaService` | Parses schema; resolves property labels and inverse/symmetric relations |
| `HtmlDrawService` | Renders the DOM cloud (centre object + surrounding nodes) |
| `CloudService` | Manages cloud layout and node grouping by type |
| `NavigationService` | Handles click events; triggers `load-object` transitions |
| `AnimationService` | CSS/jQuery animations between navigation states |
| `HistoryManager` | Syncs browser URL hash with selected object (jquery.address) |

Modules are replaceable: pass a `modules` override map as the 4th argument to `VisualizerApp`.

**Startup sequence:** `VisualizerApp` waits for `document.ready + core.all-modules-started + schemaservice.ready` (and optionally `historymanager.ready`) before firing the initial `load-object`.

## Embedding in a host page (release mode)

```html
<link href="Content/visualizer.css" rel="stylesheet">
<link href="Content/visualizer-skin.css" rel="stylesheet">
<script src="Scripts/visualizer_compiled_min.js"></script>

<div id="visualizer_canvas"></div>
<script>
  var app = new VisualizerApp(
    "visualizer_canvas",        // container element id
    "https://example.org/pub1", // start object URI (null = aggregation root)
    {
      dataUrl:          "https://my-repo/pub1.rdf",
      schemaUrl:        "https://my-repo/schema.json",
      schemaFormat:     "application/json",
      titleProperties:  ["http://purl.org/dc/terms/title"],
    }
  );
  app.subscribe("*.load-object", function(e) { console.log("loaded", e.data); });
</script>
```

See `docs/ConfigurationOptions.md` for all config keys. See `docs/VisualiserApi.wiki` for events (`load-object`, `uri-click`, `object-uri-click`) and external calls (`app.loadObject(uri)`).

## Data formats

- **Data** (`dataUrl`): RDF/XML (default) or RDF/JSON describing the Enhanced Publication graph
- **Schema** (`schemaUrl`): RDF/XML or JSON defining property labels, types, OWL inverse/symmetric relations, and base class mappings

Example files are in `trunk/Source/Example/`. The expected RDF model is OAI-ORE: an `ore:Aggregation` with `ore:aggregates` relations to resources typed via FOAF, SKOS, OWL, or custom namespaces.

## Skinning

Edit `Content/visualizer-skin.css` to override default styles. CSS class names for node types are generated from `baseClassTypes` config values (e.g. `"aggregation"`, `"document"`, `"person"`). Icons are set via CSS background images keyed on these class names.

## Goals for this revival

- Make the example run live as a **GitHub Pages** demo
- Update dependencies (jQuery 1.4.4 → current, rdflib partial → current rdflib.js)
- Archive to **Zenodo** with a proper DOI
