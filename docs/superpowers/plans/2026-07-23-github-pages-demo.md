# GitHub Pages Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy a live demo of rdf-InContext to `https://surf-ori.github.io/incontext/` with a wrapper page explaining Enhanced Publications.

**Architecture:** Build a concatenated JS bundle from the source files (no Java/Ant needed — plain `cat`), copy static assets to `docs/`, and add a wrapper `index.html`. GitHub Pages is already configured to serve from `/docs` on `main`.

**Tech Stack:** Vanilla JavaScript (ES3-era), jQuery 1.4.4 (bundled), bash for the build script.

## Global Constraints

- jQuery version stays at 1.4.4 — it is bundled in the repo and `$.browser` depends on it
- No npm, no Node.js build tools — build script must be plain bash + `cat` + `sed`
- All paths in this plan are relative to the repo root `/c/Users/mvn439/Code/incontext/`
- Run all commands from the repo root unless stated otherwise
- GitHub Pages is already enabled: `main` branch, `/docs` folder

---

### Task 1: Remove `async: false` from rdfxmlparser.js

**Files:**
- Modify: `trunk/Source/Scripts/utils/rdfxmlparser.js:33`

**Why:** `async: false` on `XMLHttpRequest` is deprecated and prints a console error in modern browsers. The success callback already handles async flow — removing this one line is sufficient.

- [ ] **Step 1: Remove the async: false line**

  Open `trunk/Source/Scripts/utils/rdfxmlparser.js`. The `$.ajax` call starts at line 30. Remove line 33 exactly:

  Before (lines 30–34):
  ```javascript
        $.ajax({
          url: dataUrl,
          dataType: ($.browser.msie) ? "text" : "xml",
          async: false,
          success: function(data) {
  ```

  After:
  ```javascript
        $.ajax({
          url: dataUrl,
          dataType: ($.browser.msie) ? "text" : "xml",
          success: function(data) {
  ```

- [ ] **Step 2: Verify the edit**

  ```bash
  grep -n "async" trunk/Source/Scripts/utils/rdfxmlparser.js
  ```

  Expected output: one line only — inside the IE6 branch (`xml.async = false;` around line 37). The top-level `async: false` must be gone.

- [ ] **Step 3: Commit**

  ```bash
  git add trunk/Source/Scripts/utils/rdfxmlparser.js
  git commit -m "fix: remove deprecated synchronous XHR (async: false) from rdfxmlparser"
  ```

---

### Task 2: Build script and `docs/` static assets

**Files:**
- Create: `scripts/build.sh`
- Create: `docs/visualizer.js` (output — do not hand-edit)
- Copy: `docs/Content/` from `trunk/Source/Content/`
- Copy: `docs/Example/` from `trunk/Source/Example/`

- [ ] **Step 1: Create `scripts/build.sh`**

  ```bash
  mkdir -p scripts
  ```

  Write `scripts/build.sh` with this exact content:

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  SRC="trunk/Source/Scripts"
  OUT="docs/visualizer.js"

  mkdir -p docs

  files=(
    "$SRC/dependencies/jquery-1.4.4.js"
    "$SRC/dependencies/jquery.address-1.3.1.min.js"
    "$SRC/dependencies/jquery.effects.core.js"
    "$SRC/dependencies/rdflib/util.js"
    "$SRC/dependencies/rdflib/uri.js"
    "$SRC/dependencies/rdflib/term.js"
    "$SRC/dependencies/rdflib/rdfparser.js"
    "$SRC/dependencies/rdflib/identity.js"
    "$SRC/visualizer.js"
    "$SRC/utils/htmlpopup.js"
    "$SRC/utils/rdfxmlparser.js"
    "$SRC/framework/core.js"
    "$SRC/framework/sandbox.js"
    "$SRC/modules/syncdataconnector.js"
    "$SRC/modules/schemaconnector.js"
    "$SRC/modules/dataservice.js"
    "$SRC/modules/schemaservice.js"
    "$SRC/modules/htmldrawservice.js"
    "$SRC/modules/historymanager.js"
    "$SRC/modules/cloudservice.js"
    "$SRC/modules/navigationservice.js"
    "$SRC/modules/animationservice.js"
    "$SRC/domain/node.js"
  )

  # Concatenate, stripping UTF-8 BOM (0xEF 0xBB 0xBF) from each file
  for f in "${files[@]}"; do
    sed 's/\xef\xbb\xbf//g' "$f"
  done > "$OUT"

  echo "Built $OUT ($(wc -c < "$OUT") bytes)"
  ```

- [ ] **Step 2: Make it executable and run it**

  ```bash
  chmod +x scripts/build.sh
  bash scripts/build.sh
  ```

  Expected output (byte count will vary slightly):
  ```
  Built docs/visualizer.js (XXXXXX bytes)
  ```

- [ ] **Step 3: Verify the bundle is valid**

  ```bash
  wc -c docs/visualizer.js
  head -3 docs/visualizer.js
  grep -c "VisualizerApp" docs/visualizer.js
  ```

  Expected:
  - File size > 200,000 bytes
  - First line starts with `/*` (jQuery header comment)
  - `grep -c "VisualizerApp"` returns at least 2 (defined in `visualizer.js`, used in `historymanager.js`)

- [ ] **Step 4: Copy static assets**

  ```bash
  cp -r trunk/Source/Content docs/Content
  cp -r trunk/Source/Example docs/Example
  ```

- [ ] **Step 5: Verify assets are in place**

  ```bash
  ls docs/Content/
  ls docs/Example/
  ```

  Expected — `docs/Content/`:
  ```
  Images/  blank.gif  iepngfix.htc  iepngfix_tilebg.js  visualizer-ie6.css  visualizer-skin.css  visualizer.css
  ```

  Expected — `docs/Example/`:
  ```
  example_data.rdf  example_schema.json  example_schema.rdf
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add scripts/build.sh docs/visualizer.js docs/Content docs/Example
  git commit -m "build: add build script and assemble docs/ demo assets"
  ```

---

### Task 3: Create `docs/index.html` — the wrapper page

**Files:**
- Create: `docs/index.html`

- [ ] **Step 1: Write `docs/index.html`**

  Colours and font from SURF's Curve design system (`tokens.surf-blue-turquoise.json`):
  - Primary: `#064BCB`, teal accent: `#BDEEE9`, link: `#053EAA`
  - Muted bg: `#F5F5F4`, border: `#D6D3D1`, text: `#0A0A0A`
  - Font: "Source Sans 3" (Google Fonts)

  Write this exact content to `docs/index.html`:

  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>InContext — RDF Visualiser for Enhanced Publications</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="Content/visualizer.css">
    <link rel="stylesheet" href="Content/visualizer-skin.css">
    <style>
      /* SURF Curve design tokens — surf-blue-turquoise theme */
      :root {
        --surf-primary:    #064BCB;
        --surf-teal:       #BDEEE9;
        --surf-link:       #053EAA;
        --surf-muted-bg:   #F5F5F4;
        --surf-border:     #D6D3D1;
        --surf-text:       #0A0A0A;
        --surf-text-muted: #525252;
      }

      *, *::before, *::after { box-sizing: border-box; }

      body {
        font-family: "Source Sans 3", sans-serif;
        font-size: 1.125rem;
        line-height: 1.75rem;
        color: var(--surf-text);
        background: #fff;
        margin: 0;
        padding: 0;
      }

      /* Top bar */
      .surf-bar {
        background: var(--surf-primary);
        color: #fff;
        padding: 0.75rem 2rem;
        font-size: 0.875rem;
        font-weight: 600;
        letter-spacing: 0.02em;
      }
      .surf-bar a { color: #fff; text-decoration: none; opacity: 0.85; }
      .surf-bar a:hover { opacity: 1; }

      /* Content */
      .content {
        max-width: 920px;
        margin: 0 auto;
        padding: 2rem 2rem 3rem;
      }

      h1 {
        font-size: 2.25rem;
        line-height: 2.5rem;
        font-weight: 700;
        color: var(--surf-primary);
        margin: 1.5rem 0 0.25rem;
      }
      .subtitle {
        color: var(--surf-text-muted);
        margin: 0 0 2rem;
        font-size: 1rem;
      }

      h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--surf-primary);
        margin: 2rem 0 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid var(--surf-teal);
      }

      p { margin: 0 0 1rem; }

      a { color: var(--surf-link); }
      a:hover { text-decoration: none; }

      .ref {
        background: var(--surf-muted-bg);
        border-left: 4px solid var(--surf-primary);
        padding: 0.8rem 1.2rem;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0.5rem 0 1.5rem;
        border-radius: 0 0.25rem 0.25rem 0;
      }

      .demo-divider {
        border: none;
        border-top: 2px solid var(--surf-teal);
        margin: 2.5rem 0 1rem;
      }
      .demo-label {
        font-size: 0.875rem;
        color: var(--surf-text-muted);
        margin-bottom: 1rem;
      }
    </style>
  </head>
  <body>

    <div class="surf-bar">
      <a href="https://www.surf.nl/">SURF</a>
    </div>

    <div class="content">

      <h1>InContext</h1>
      <p class="subtitle">RDF Visualiser for Enhanced Publications &mdash;
        originally built for SURFfoundation (2011&ndash;2013).</p>

      <h2>What are Enhanced Publications?</h2>
      <p>
        An Enhanced Publication is a scholarly article linked to its underlying research data, images, datasets,
        and other resources &mdash; forming a compound object where every part is addressable by URI and the
        relations between parts are recorded in RDF. The standard that makes this possible is
        <a href="https://www.openarchives.org/ore/">OAI-ORE</a> (Open Archives Initiative Object Reuse and Exchange).
        InContext was built as part of the <a href="https://www.surf.nl/">SURFshare</a> programme to make those
        linked objects explorable directly in a browser, without any server-side software &mdash; a purely
        client-side JavaScript solution that was novel at the time.
      </p>

      <h2>About this demo</h2>
      <p>
        The graph below shows an Enhanced Publication from the
        <a href="http://escape.utwente.nl/">ESCAPE project</a> at the University of Twente.
        It describes the <em>Physics of Fluids</em> research group and its connected publications, datasets,
        people, and events &mdash; all described as RDF and navigable by clicking.
        Click any node to move it to the centre and explore its relations.
        The browser URL updates as you navigate, so every object has a shareable deep-link.
      </p>

      <h2>Learn more</h2>
      <div class="ref">
        van Godtsenhoven, K., Karstensen Elbæk, M., Schmeltz Pedersen, G., Sierman, B.,
        Bijsterbosch, M., Hochstenbach, P., Russell, R., &amp; van der Feesten, M. (2009).
        <em>Emerging Standards for Enhanced Publications and Repository Technology: Survey on Technology</em>.
        DRIVER II / SURFfoundation / Amsterdam University Press.
        Open access: <a href="http://hdl.handle.net/1854/LU-1942496">hdl.handle.net/1854/LU-1942496</a>
      </div>

      <hr class="demo-divider">
      <p class="demo-label">&#9660; Interactive visualiser &mdash; click any node to navigate</p>

      <div id="visualizer_canvas"></div>

    </div><!-- /.content -->

    <script src="visualizer.js"></script>
    <script>
      var app = new VisualizerApp("visualizer_canvas", "http://pof.tnw.utwente.nl/", {
        debug: false,
        dataUrl: "Example/example_data.rdf",
        schemaUrl: "Example/example_schema.json",
        schemaFormat: "application/json",
        titleProperties: [
          "http://purl.org/dc/terms/title",
          "http://xmlns.com/foaf/0.1/name"
        ],
        dontShowProperties: [
          "http://purl.utwente.nl/ns/escape-system.owl#id",
          "http://purl.utwente.nl/ns/escape-system.owl#resourceUri"
        ],
        annotationTypeId: "http://purl.utwente.nl/ns/escape-annotations.owl#RelationAnnotation",
        objectAnnotationTypeId: "http://purl.utwente.nl/ns/escape-annotations.owl#object",
        subjectAnnotationTypeId: "http://purl.utwente.nl/ns/escape-annotations.owl#subject",
        descriptionAnnotationTypeId: "http://purl.org/dc/terms/description",
        imageTypeId: "http://xmlns.com/foaf/0.1/img",
        useHistoryManager: true,
        baseClassTypes: {
          "http://purl.utwente.nl/ns/escape-pubtypes.owl#Publication": "publication",
          "http://purl.org/dc/dcmitype/MovingImage": "video",
          "http://purl.utwente.nl/ns/escape-events.owl#Event": "event",
          "http://purl.utwente.nl/ns/escape-projects.owl#Topic": "topic"
        }
      });
    </script>

  </body>
  </html>
  ```

- [ ] **Step 2: Verify locally**

  ```bash
  python3 -m http.server 8080 --directory docs
  ```

  Open `http://localhost:8080/` in a browser. Verify:
  - Page title "InContext — RDF Visualiser for Enhanced Publications" appears
  - All three text sections render (What are Enhanced Publications / About this demo / Learn more)
  - The book link points to `http://hdl.handle.net/1854/LU-1942496`
  - The visualiser canvas area appears below the divider
  - Browser console (F12) shows no errors — specifically no `async: false` deprecation warning and no `VisualizerApp is not defined`
  - After a moment the visualiser renders nodes (RDF graph loads from `Example/example_data.rdf`)
  - Clicking a node updates the URL hash (e.g. `#/?id=http%3A%2F%2F...`)

  Stop the server with Ctrl+C when done.

- [ ] **Step 3: Commit and push**

  ```bash
  git add docs/index.html
  git commit -m "feat: add GitHub Pages demo wrapper page with Enhanced Publications context"
  git push
  ```

---

### Task 4: Verify GitHub Pages deployment

- [ ] **Step 1: Check deployment status**

  ```bash
  gh run list --repo surf-ori/incontext --limit 3
  ```

  Wait for the Pages deployment to show as completed (usually under 2 minutes after push).

- [ ] **Step 2: Verify live URL**

  ```bash
  curl -sI https://surf-ori.github.io/incontext/ | head -5
  ```

  Expected: `HTTP/2 200`

- [ ] **Step 3: Open in browser and smoke-test**

  Open `https://surf-ori.github.io/incontext/` and verify:
  - Wrapper text renders
  - Visualiser loads and shows the RDF graph
  - Clicking a node navigates and updates the URL
  - Book link (`hdl.handle.net/1854/LU-1942496`) opens correctly

- [ ] **Step 4: Add live demo link to README**

  Append to `README.md`, after the DOI badge:

  ```markdown
  [![Live demo](https://img.shields.io/badge/demo-GitHub%20Pages-blue)](https://surf-ori.github.io/incontext/)
  ```

  ```bash
  git add README.md
  git commit -m "docs: add GitHub Pages live demo badge to README"
  git push
  ```
