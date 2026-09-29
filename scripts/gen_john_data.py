#!/usr/bin/env python3
"""Generate docs/Example/john_data.rdf — the career of John Doove as an Enhanced Publication.

Shown by docs/index.html#john. Publication metadata (titles, dates, DOIs, creators,
affiliations, ORCIDs, grant) is read from scratch/john_zenodo.json, a trimmed copy of
the Zenodo API response for creators.name:"Doove, John" plus the ORCID record summary.
Career data comes from the Open Science President nomination text.

Usage: python3 scripts/gen_john_data.py [source.json] [output.rdf]
"""
import json
import os
import re
import sys
from xml.sax.saxutils import escape, quoteattr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scratch", "john_zenodo.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "docs", "Example", "john_data.rdf")
DATA = json.load(open(SRC, encoding="utf-8"))
RECORDS = {r["doi"]: r for r in DATA["records"]}
SNIPPETS = {r["doi"]: r for r in DATA["unverified_from_search_snippets"]}
ORCID_RECORD = DATA["orcid_record"]

NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "ore": "http://www.openarchives.org/ore/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "swrc": "http://swrc.ontoware.org/ontology#",
    "swan": "http://swan.mindinformatics.org/ontologies/1.2/discourse-relationships/",
    "escape-projects": "http://purl.utwente.nl/ns/escape-projects.owl#",
    "escape-annotations": "http://purl.utwente.nl/ns/escape-annotations.owl#",
}
AGENTS = "http://purl.utwente.nl/ns/escape-agents.owl#"
PUB = "http://purl.utwente.nl/ns/escape-pubtypes.owl#"
EVENTS = "http://purl.utwente.nl/ns/escape-events.owl#"
TOPIC = "http://purl.utwente.nl/ns/escape-projects.owl#ResearchTopic"
PERSON = "http://xmlns.com/foaf/0.1/Person"
ORG = "http://xmlns.com/foaf/0.1/Organization"
PROJECT = "http://xmlns.com/foaf/0.1/Project"
ANNOT = "http://purl.utwente.nl/ns/escape-annotations.owl#RelationAnnotation"

BASE = "https://surf-ori.github.io/incontext/john/"
AGG = BASE + "aggregation"
REM = BASE + "resourcemap"
JOHN = "https://orcid.org/" + ORCID_RECORD["orcid"]
LI = "https://www.linkedin.com/in/jdoove/"

resources = []  # (uri, type, [(prop, value, is_uri)])


def res(uri, rtype, *props):
    resources.append((uri, rtype, list(props)))
    return uri


def L(p, v):
    return (p, v, False)


def R(p, v):
    return (p, v, True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def display_name(name):
    """'van Eck, Nees Jan' -> 'Nees Jan van Eck' (spelling and casing kept as in the source)."""
    family, _, given = name.partition(", ")
    return (given + " " + family).strip()


def doi_uri(doi):
    return "https://doi.org/" + doi


def year(date):
    return date[:4]


# ---------------------------------------------------------------- topics
T_OA = res("https://en.wikipedia.org/wiki/Open_access", TOPIC, L("foaf:name", "Open access"))
T_OS = res("https://en.wikipedia.org/wiki/Open_science", TOPIC, L("foaf:name", "Open science"))
T_EP = res("https://en.wikipedia.org/wiki/Enhanced_publication", TOPIC, L("foaf:name", "Enhanced publications"))
T_ORI = res("https://en.wikipedia.org/wiki/Open_research_information", TOPIC, L("foaf:name", "Open research information"))
T_PID = res("https://en.wikipedia.org/wiki/Persistent_identifier", TOPIC, L("foaf:name", "Persistent identifiers (PIDs)"))
T_FAIR = res("https://en.wikipedia.org/wiki/FAIR_data", TOPIC, L("foaf:name", "FAIR data and reproducibility"))
T_INFRA = res("https://en.wikipedia.org/wiki/Research_infrastructure", TOPIC,
              L("foaf:name", "Sustainable open science infrastructure"))

# ---------------------------------------------------------------- organisations
SURF = res("https://www.surf.nl/", AGENTS + "Association",
           L("foaf:name", "SURF"),
           L("dcterms:description", "The collaborative organisation for IT in Dutch education and research."),
           R("foaf:homepage", "https://www.surf.nl/en/themes/open-science"),
           *[L("dcterms:identifier", "%s: %s" % kv) for kv in ORCID_RECORD["surf_identifiers"].items()])
LUL = res("https://www.library.universiteitleiden.nl/", AGENTS + "Department",
          L("foaf:name", "Leiden University Library"))
LEIDEN = res("https://www.universiteitleiden.nl/", AGENTS + "University",
             L("foaf:name", "Leiden University"), R("foaf:member", LUL))
NWO = res("https://www.nwo.nl/", ORG, L("foaf:name", "Dutch Research Council (NWO)"))
OSNL = res("https://www.openscience.nl/", ORG, L("foaf:name", "Open Science NL"),
           L("dcterms:description", "National open science funding programme hosted by NWO."))
KE = res("https://www.knowledge-exchange.info/", ORG, L("foaf:name", "Knowledge Exchange"),
         L("dcterms:description", "European partnership of national research-infrastructure organisations (incl. SURF) supporting open scholarship."),
         R("foaf:member", SURF))
UNL = res("https://www.universiteitenvannederland.nl/", AGENTS + "Association",
          L("foaf:name", "Universities of the Netherlands (UNL)"))
VH = res("https://www.vereniginghogescholen.nl/", AGENTS + "Association",
         L("foaf:name", "Netherlands Association of Universities of Applied Sciences (VH)"))
UKB = res("https://www.ukb.nl/", AGENTS + "Association",
          L("foaf:name", "UKB — Dutch university libraries and the KB"))
KB = res("https://www.kb.nl/", AGENTS + "Institute", L("foaf:name", "KB, National Library of the Netherlands"))
SIA = res("https://regieorgaan-sia.nl/", ORG, L("foaf:name", "Regieorgaan SIA"),
          L("dcterms:description", "Funder of practice-oriented research at universities of applied sciences."))
UT = res("https://www.utwente.nl/", AGENTS + "University", L("foaf:name", "University of Twente"))

# ---------------------------------------------------------------- people
LEO = res(BASE + "person/leo-waaijers", PERSON, L("foaf:name", "Leo Waaijers"),
          L("dcterms:description", "Open access pioneer; led the SURF DARE programme and Cream of Science."),
          R("foaf:workplaceHomepage", SURF))
MARNIX = res(BASE + "person/marnix-van-bergen", PERSON, L("foaf:name", "Marnix van Bergen"))
ANNEMIEK = res(BASE + "person/annemiek-van-der-kuil", PERSON, L("foaf:name", "Annemiek van der Kuil"))
MARLON = res(BASE + "person/marlon-domingus", PERSON, L("foaf:name", "Marlon Domingus"))

# ---------------------------------------------------------------- publications & outputs
P_KE_URI = "https://doi.org/10.5281/zenodo.3454688"

# Organisations for co-author affiliations (names as in the Zenodo file); known ones map to existing nodes
AFFILIATIONS = {"SURF": SURF, "Leiden University": LEIDEN, "Universiteit Leiden": LEIDEN}
# RDNL partners, named in the Stakeholder Engagement Plan context
for partner in ("DANS", "4TU.ResearchData", "Health-RI"):
    AFFILIATIONS[partner] = res(BASE + "org/" + slug(partner), ORG, L("foaf:name", partner))
RDNL = res(BASE + "org/research-data-netherlands", ORG,
           L("foaf:name", "Research Data Netherlands (RDNL)"),
           L("dcterms:description", "Coalition of 4TU.ResearchData, DANS, SURF and Health-RI."),
           *[R("foaf:member", AFFILIATIONS[p]) for p in ("4TU.ResearchData", "DANS", "SURF", "Health-RI")])


def affiliation(name):
    if name not in AFFILIATIONS:
        AFFILIATIONS[name] = res(BASE + "org/" + slug(name), ORG, L("foaf:name", name))
    return AFFILIATIONS[name]


PEOPLE = {}  # key: ORCID or name -> uri


def person(creator):
    """Node for a Zenodo creator. ORCID URL as identifier only when the source supplies one."""
    orcid = creator.get("orcid")
    if orcid and "https://orcid.org/" + orcid == JOHN:
        return JOHN
    key = orcid or creator["name"]
    if key not in PEOPLE:
        uri = "https://orcid.org/" + orcid if orcid else BASE + "person/" + slug(display_name(creator["name"]))
        props = [L("foaf:name", display_name(creator["name"]))]
        if creator.get("affiliation"):
            props.append(R("foaf:workplaceHomepage", affiliation(creator["affiliation"])))
        PEOPLE[key] = res(uri, PERSON, *props)
    elif creator.get("affiliation"):
        # same person in several records: add an affiliation the earlier record did not give
        entry = next(r for r in resources if r[0] == PEOPLE[key])
        link = R("foaf:workplaceHomepage", affiliation(creator["affiliation"]))
        if link not in entry[2]:
            entry[2].append(link)
    return PEOPLE[key]


def zenodo_output(doi, rtype, *extra):
    """Publication node built from a Zenodo record: title, date, version, creators in source order."""
    rec = RECORDS[doi]
    creators = [person(c) for c in rec["creators"]]
    props = [L("dcterms:title", rec["title"]), L("dcterms:issued", rec["date"])]
    if rec.get("version"):
        props.append(L("dcterms:hasVersion", rec["version"]))
    props += [L("dcterms:publisher", "Zenodo"), L("dcterms:type", rec["type"]),
              L("dcterms:bibliographicCitation", "%s (%s). %s. Zenodo. %s" % (
                  "; ".join(c["name"] for c in rec["creators"]), rec["date"], rec["title"], doi_uri(doi)))]
    props += [R("dcterms:creator", c) for c in creators]
    return res(doi_uri(doi), rtype, *(props + list(extra)))


# Most recent output first
P_COMMONS = zenodo_output("10.5281/zenodo.21526773", PUB + "Report",
                          L("dcterms:description", "Keywords: " + ", ".join(RECORDS["10.5281/zenodo.21526773"]["keywords"])),
                          R("swan:relatedTo", P_KE_URI), R("dcterms:subject", T_INFRA))
G_BROCCOLI = RECORDS["10.5281/zenodo.19885633"]["grant"]
P_BROCCOLI = zenodo_output("10.5281/zenodo.19885633", PUB + "ResearchProposal",
                           L("dcterms:abstract", "BROCCOLI will bring accessible, reliable and reusable information on Dutch research actors, activities and outputs together in an open infrastructure that facilitates evidence-informed decision-making in the Dutch research system."),
                           L("dcterms:relation", "Grant: %s, %s, %s" % (G_BROCCOLI["funder"], G_BROCCOLI["title"], G_BROCCOLI["code"])),
                           R("foaf:fundedBy", OSNL), R("dcterms:subject", T_ORI))
P_SEP = zenodo_output("10.5281/zenodo.18622300", PUB + "Report",
                      L("dcterms:description", RECORDS["10.5281/zenodo.18622300"]["context"]),
                      R("foaf:fundedBy", OSNL), R("dcterms:subject", T_FAIR))
P_ORCID = zenodo_output("10.5281/zenodo.5836056", PUB + "Report",
                        L("dcterms:abstract", "Outcomes of SURF projects mobilising persistent identifiers in the Netherlands: the ORCID-NL pilot, the move to the ORCID-NL consortium of all research universities, Identifiers for FAIR research information, and work towards a national PID strategy."),
                        R("dcterms:subject", T_PID), R("dcterms:subject", T_ORI))

# From search snippets only: names without ORCIDs, no date
_dai_case = SNIPPETS["10.5281/zenodo.7327505"]
P_DAICASE = res(doi_uri(_dai_case["doi"]), PUB + "Report",
                L("dcterms:title", _dai_case["title"]), R("dcterms:subject", T_PID))
_dai_note = SNIPPETS["10.5281/zenodo.8383405"]
_dai_authors = []
for entry in _dai_note["creators_names_only"]:
    name = re.match(r"(.+?) \(.+\)$", entry).group(1)  # names only; no ORCIDs or affiliations
    given, family = name.split(" ", 1)
    _dai_authors.append(JOHN if name == "John Doove" else person({"name": family + ", " + given}))
P_DAI = res(doi_uri(_dai_note["doi"]), PUB + "PolicyDocument",
            L("dcterms:title", _dai_note["title"]),
            L("dcterms:language", "nl"),
            L("dcterms:abstract", "On the future of the Digital Author Identifier (DAI), developed in 2005 in the SURF DARE programme and used at all Dutch universities: background, the Dutch DAI infrastructure, the emerging international standards, and recommendations."),
            L("dcterms:bibliographicCitation", ", ".join(_dai_note["creators_names_only"]) + ". " + _dai_note["title"] + ". Zenodo. " + doi_uri(_dai_note["doi"])),
            *[R("dcterms:creator", a) for a in _dai_authors],
            R("dcterms:relation", P_DAICASE), R("dcterms:subject", T_PID))
P_ORIPROG = res("https://zenodo.org/records/15772562", PUB + "PolicyDocument",
                L("dcterms:title", "SURF Open Research Information (ORI) Program 2025 – 2030"),
                L("dcterms:abstract", "Programme within the SURF Innovation Zone Strengthening Open Science, with the ambition that all information about Dutch publicly funded research and its results is openly available and reusable."),
                L("dcterms:publisher", "SURF"), R("dcterms:subject", T_ORI))
P_KE = res("https://doi.org/10.5281/zenodo.3454688", PUB + "Report",
           L("dcterms:title", "Open Scholarship and the need for collective action"),
           L("dcterms:issued", "2019"),
           L("dcterms:publisher", "Knowledge Exchange"),
           L("dcterms:abstract", "Knowledge Exchange study on the economic and incentive challenges of the transition to open scholarship, using the KE Open Scholarship Framework of micro, meso and macro levels."),
           R("dcterms:subject", T_OS))
P_UNL = res("https://www.universiteitenvannederland.nl/files/publications/Alternatieve%20platformen%20als%20change%20agents%20van%20het%20publiceren%20versie%201.0.pdf",
            PUB + "PolicyDocument",
            L("dcterms:title", "Alternatieve open access platformen als change agents van het publiceren"),
            L("dcterms:language", "nl"), L("dcterms:publisher", "Universiteiten van Nederland"),
            R("dcterms:subject", T_OA))
P_EPBOOK = res("https://www.amazon.com/Enhanced-Publications-Research-Repositories-EU-Driver-ebook/dp/B0FTG1DFJ6",
               PUB + "Book",
               L("dcterms:title", "Enhanced Publications: Linking Publications and Research Data in Digital Repositories"),
               L("dcterms:issued", "2009"),
               L("dcterms:publisher", "Amsterdam University Press (SURF / EU DRIVER)"),
               R("dcterms:subject", T_EP))
P_EPSURVEY = res("http://hdl.handle.net/1854/LU-1942496", PUB + "Report",
                 L("dcterms:title", "Emerging Standards for Enhanced Publications and Repository Technology: Survey on Technology"),
                 L("dcterms:issued", "2009"),
                 L("dcterms:publisher", "DRIVER II / SURFfoundation / Amsterdam University Press"),
                 R("dcterms:subject", T_EP))
P_EPTALK = res("https://www.slideserve.com/kairos/challenges-in-data-publishing-enhanced-publications", PUB + "Lecture",
               L("dcterms:title", "Challenges in Data Publishing: Enhanced Publications"),
               R("dcterms:creator", JOHN), R("dcterms:subject", T_EP))
P_EPSLIDES = res("https://www.slideshare.net/dduin/enhanced-publications-by-john-doove", PUB + "Lecture",
                 L("dcterms:title", "Enhanced Publications (slides)"),
                 R("dcterms:creator", JOHN), R("dcterms:subject", T_EP))
P_OREPOST = res("https://groups.google.com/g/oai-ore/c/YJzxZarMjs4", PUB + "ContributionToPeriodical",
                L("dcterms:title", "Resource Maps (edit – store – visualise)"),
                L("dcterms:publisher", "OAI-ORE mailing list"),
                L("dcterms:abstract", "John announces the open-source SURF tools for Enhanced Publications: the ESCAPE resource map editor and repository, and the InContext visualiser."),
                R("dcterms:creator", JOHN), R("dcterms:subject", T_EP))
P_EPMODEL = res("https://wiki.surfnet.nl/pages/viewpage.action?pageId=11057404", PUB + "TechnicalDocumentation",
                L("dcterms:title", "Object model Enhanced Publications"),
                L("dcterms:publisher", "SURF Wiki"), R("dcterms:subject", T_EP))
P_DELTA = res("https://delta.tudelft.nl/article/een-nationale-etalage-voor-de-wetenschap", PUB + "ContributionToPeriodical",
              L("dcterms:title", "Een nationale etalage voor de wetenschap"),
              L("dcterms:publisher", "Delta (TU Delft)"), L("dcterms:language", "nl"),
              R("dcterms:subject", T_OA))
P_WERKEN = res("https://werkenbij.surf.nl/programmamanager-open-science-john-doove/", PUB + "ContributionToPeriodical",
               L("dcterms:title", "John vertelt over zijn werk als programmamanager open science bij SURF"),
               L("dcterms:publisher", "Werken bij SURF"), L("dcterms:language", "nl"),
               R("dcterms:subject", T_OS))
P_STORY = res("https://www.surf.nl/en/employee-stories/john-doove-open-access-programme-manager-at-surf",
              PUB + "ContributionToPeriodical",
              L("dcterms:title", "John Doove, Open Access Programme Manager at SURF"),
              L("dcterms:publisher", "SURF.nl"), R("dcterms:subject", T_OA))

# ---------------------------------------------------------------- projects & infrastructures
J_CREAM = res(BASE + "project/cream-of-science", PROJECT,
              L("foaf:name", "Cream of Science — professors in open repositories"),
              L("dcterms:description", "Getting researchers and professors to put their publications in open repositories (e-prints, DSpace), offering practical facilities to start open access in the Netherlands."),
              L("swrc:startDate", "2005"),
              R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_OA), R("swan:relatedTo", P_DELTA))
J_EP = res(BASE + "project/enhanced-publications", PROJECT,
           L("foaf:name", "Enhanced Publications (SURFshare)"),
           L("dcterms:description", "Dynamic papers: linking publications to research data, images and other resources with OAI-ORE resource maps."),
           R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_EP),
           R("escape-projects:outcomeDocument", P_EPBOOK), R("escape-projects:outcomeDocument", P_EPSURVEY),
           R("escape-projects:outcomeDocument", P_EPMODEL))
J_ESCAPE = res("http://code.google.com/p/surf-escape/", PROJECT,
               L("foaf:name", "ESCAPE — resource map editor and repository"),
               R("swrc:carriedOutBy", UT), R("swan:relatedTo", J_EP), R("dcterms:subject", T_EP))
J_INCONTEXT = res("https://github.com/surf-ori/incontext", PROJECT,
                  L("foaf:name", "InContext visualiser (the tool you are looking at)"),
                  L("dcterms:description", "Client-side visualiser for Enhanced Publications, originally at code.google.com/p/surf-incontext, revived on GitHub Pages."),
                  R("swrc:carriedOutBy", SURF), R("swan:relatedTo", J_EP), R("swan:relatedTo", J_ESCAPE),
                  R("dcterms:subject", T_EP))
J_DAI = res(BASE + "project/orcid-nl", PROJECT,
            L("foaf:name", "From DAI to ORCID-NL: author identifiers for the Netherlands"),
            R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_PID),
            R("escape-projects:outcomeDocument", P_DAI), R("escape-projects:outcomeDocument", P_ORCID))
J_HBOKB = res("https://www.hbo-kennisbank.nl/", PROJECT,
              L("foaf:name", "HBO Kennisbank"),
              L("dcterms:description", "National repository of research output of Dutch universities of applied sciences."),
              R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_OA))
J_SHAREKIT = res("https://www.surf.nl/en/services/surfsharekit", PROJECT,
                 L("foaf:name", "SURFsharekit"),
                 L("dcterms:description", "Repository service for sharing research outputs and educational resources."),
                 R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_INFRA))
J_PUBLINOVA = res("https://publinova.nl/en", PROJECT,
                  L("foaf:name", "Publinova"),
                  L("dcterms:description", "The national platform for open practice-oriented research: a collaboration between the Dutch universities of applied sciences, the Association of Universities of Applied Sciences, SIA and SURF."),
                  R("swrc:carriedOutBy", SURF), R("swrc:carriedOutBy", VH), R("foaf:fundedBy", SIA),
                  R("swan:relatedTo", J_HBOKB), R("swan:relatedTo", J_SHAREKIT),
                  R("dcterms:subject", T_OA), R("dcterms:subject", T_INFRA))
J_IZ = res("https://www.surf.nl/over/wat-surf-doet/onze-focus-voor-2022-2027/innovatiezones-surf", PROJECT,
           L("foaf:name", "SURF Innovation Zone Open Science"),
           L("dcterms:description", "Innovation zone accepted by the SURF members' board, running programmes on reproducibility (FAIR data), open scholarly communication and open research information; connected to the Research Infrastructure innovation zone."),
           R("swrc:carriedOutBy", SURF),
           R("dcterms:subject", T_OS), R("dcterms:subject", T_FAIR), R("dcterms:subject", T_ORI))
J_ORI = res(BASE + "project/open-research-information", PROJECT,
            L("foaf:name", "SURF Open Research Information programme"),
            L("dcterms:description", "Beyond the PDF: rich, open information about research, making research reproducible."),
            L("swrc:startDate", "2015"),
            R("swrc:carriedOutBy", SURF), R("swan:relatedTo", J_IZ), R("dcterms:subject", T_ORI),
            R("escape-projects:outcomeDocument", P_ORIPROG))
J_BROCCOLI = res(BASE + "project/broccoli", PROJECT,
                 L("foaf:name", "BROCCOLI — Dutch hub for open research information"),
                 L("escape-projects:startDate", "2026"), L("escape-projects:endDate", "2030"),
                 L("dcterms:source", "Project period 2026–2030: NWO project page for grant " + G_BROCCOLI["code"]),
                 L("dcterms:identifier", "Grant %s — %s, %s" % (G_BROCCOLI["code"], G_BROCCOLI["funder"], G_BROCCOLI["title"])),
                 R("swrc:carriedOutBy", SURF), R("foaf:fundedBy", OSNL), R("swan:relatedTo", J_ORI),
                 R("dcterms:subject", T_ORI), R("escape-projects:outcomeDocument", P_BROCCOLI))
_rdnl_context = RECORDS["10.5281/zenodo.18622300"]["context"]
J_RDNL = res(BASE + "project/rdnl", PROJECT,
             L("foaf:name", re.search(r"project '([^']+)'", _rdnl_context).group(1)),
             L("dcterms:description", _rdnl_context),
             L("dcterms:identifier", "Dossier " + re.search(r"dossier (\d+)", _rdnl_context).group(1)),
             L("escape-projects:startDate", "2025"), L("escape-projects:endDate", "2028"),
             R("swrc:carriedOutBy", RDNL), R("foaf:fundedBy", OSNL), R("dcterms:subject", T_FAIR),
             R("escape-projects:outcomeDocument", P_SEP))
J_LEERGANG = res(BASE + "project/leergang-open-science", PROJECT,
                 L("foaf:name", "Leergang Open Science"),
                 L("dcterms:description", "Learning track securing future-proof open science knowledge and practices."),
                 R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_OS))
J_UNLIIP = res(BASE + "project/unl-integrative-infrastructures", PROJECT,
               L("foaf:name", "UNL Strategic Plan Integrative Infrastructures"),
               R("swrc:carriedOutBy", UNL), R("dcterms:subject", T_INFRA))
J_NEXTCLOUD = res(BASE + "project/public-values-infrastructure", PROJECT,
                  L("foaf:name", "Public-value-driven infrastructure pilots (e.g. Nextcloud)"),
                  R("swrc:carriedOutBy", SURF), R("dcterms:subject", T_INFRA))

# ---------------------------------------------------------------- career milestones
E = EVENTS + "Event"
C1 = res(LI + "#career-2006", E, L("dcterms:title", "2006–2009 · Content manager, Leiden University Library"),
         L("escape-projects:startDate", "2006"), L("escape-projects:endDate", "2009"),
         R("swan:relatedTo", LUL), R("swan:relatedTo", T_OA))
C2 = res(LI + "#career-2009", E, L("dcterms:title", "2009 · Project coordinator, SURFfoundation"),
         L("dcterms:description", "Inspired by Leo Waaijers, John starts open science in the Netherlands at SURF and helps initiate the Dutch open access movement."),
         L("escape-projects:startDate", "2009"),
         R("swan:relatedTo", SURF), R("swan:relatedTo", LEO), R("swan:relatedTo", J_CREAM), R("swan:relatedTo", J_EP))
C3 = res(LI + "#career-2015", E, L("dcterms:title", "2015 · Programme manager Open Science, SURF"),
         L("dcterms:description", "Starts Open Research Information: beyond the PDF, rich information, reproducible data — and dynamic papers: Enhanced Publications."),
         L("escape-projects:startDate", "2015"),
         R("swan:relatedTo", SURF), R("swan:relatedTo", J_ORI), R("swan:relatedTo", J_DAI))
C4 = res(LI + "#career-2016-nwo", E, L("dcterms:title", "2016–2017 · Senior Policy Officer, NWO"),
         L("escape-projects:startDate", "2016"), L("escape-projects:endDate", "2017"),
         R("swan:relatedTo", NWO))
C5 = res(LI + "#career-2016-ke", E, L("dcterms:title", "2016–2022 · Steering group member, Knowledge Exchange"),
         L("dcterms:description", "European collaboration on open science: preprints, open access monographs, and the micro–meso–macro levels of open scholarship."),
         L("escape-projects:startDate", "2016"), L("escape-projects:endDate", "2022"),
         R("swan:relatedTo", KE), R("swan:relatedTo", P_KE))
C6 = res(LI + "#career-2022", E, L("dcterms:title", "2022–2024 · Team lead innovation in education, SURF"),
         L("dcterms:description", "Aligning research and education on shared infrastructural needs."),
         L("escape-projects:startDate", "2022"), L("escape-projects:endDate", "2024"),
         R("swan:relatedTo", SURF), R("swan:relatedTo", J_SHAREKIT))
C7 = res(LI + "#career-2024", E, L("dcterms:title", "2024 – now · Team lead SURF Open Science"),
         L("dcterms:description", "Lead of the SURF Innovation Zone Open Science; steering group UNL Integrative Infrastructures; strategic stakeholder management (UKB, KB, SHB, DCC-po, VH, UNL, NWO/OSNL); business development and coalition forming; NWO OSC advisory panel."),
         L("escape-projects:startDate", "2024"),
         R("swan:relatedTo", SURF), R("swan:relatedTo", J_IZ), R("swan:relatedTo", J_UNLIIP),
         R("swan:relatedTo", UNL), R("swan:relatedTo", VH), R("swan:relatedTo", UKB), R("swan:relatedTo", KB),
         R("swan:relatedTo", OSNL))

# ---------------------------------------------------------------- John himself
res(JOHN, PERSON,
    L("foaf:name", "John Doove"),
    L("foaf:title", "Team lead Open Science, SURF"),
    L("dcterms:description", "John Doove embodies open science principles and integrates them into every conversation and context. He co-initiated the open science movement in the Netherlands at SURF, alongside Leo Waaijers. Since 2006 he has driven open access and the development of sustainable open science infrastructures such as Publinova. He now leads an innovation team of experts at SURF committed to the long-term future of open science — a natural connector across strategic, operational, technical and organisational levels."),
    L("foaf:plan", "I'm coordinating and aligning innovative activities that will facilitate the transition to open science nationally as well as internationally."),
    L("dcterms:abstract", "Specialties: promoting (international) collaboration, combining innovative ideas, motivating people to innovate."),
    L("dcterms:provenance", "The ORCID record lists no works; it gives one employment (%s), the keyword '%s' and the country %s. The publications shown here come from Zenodo and from the nomination text." % (
        ORCID_RECORD["employment"], ", ".join(ORCID_RECORD["keywords"]), ORCID_RECORD["country"])),
    R("foaf:homepage", LI),
    R("foaf:workplaceHomepage", SURF),
    R("foaf:knows", LEO), R("foaf:knows", MARNIX), R("foaf:knows", ANNEMIEK), R("foaf:knows", MARLON),
    R("foaf:topic_interest", T_OS), R("foaf:topic_interest", T_OA), R("foaf:topic_interest", T_EP),
    R("foaf:topic_interest", T_ORI), R("foaf:topic_interest", T_PID), R("foaf:topic_interest", T_INFRA),
    *[R("swan:relatedTo", c) for c in (C1, C2, C3, C4, C5, C6, C7)],
    *[R("foaf:currentProject", p) for p in (J_IZ, J_ORI, J_BROCCOLI, J_RDNL, J_LEERGANG, J_UNLIIP, J_NEXTCLOUD)],
    *[R("foaf:pastProject", p) for p in (J_CREAM, J_EP, J_INCONTEXT, J_DAI, J_HBOKB, J_SHAREKIT, J_PUBLINOVA)],
    R("swan:relatedTo", P_UNL), R("swan:relatedTo", P_WERKEN), R("swan:relatedTo", P_STORY))

# ---------------------------------------------------------------- relation annotations
annotations = [
    (JOHN, "foaf:knows", LEO, "Leo Waaijers inspired John to start working on open science at SURF in 2009."),
    (JOHN, "foaf:knows", MARNIX, "Together they initiated the Dutch open access movement."),
    (JOHN, "foaf:knows", ANNEMIEK, "Together they initiated the Dutch open access movement."),
    (JOHN, "foaf:knows", MARLON, "Together they initiated the Dutch open access movement."),
    (JOHN, "foaf:pastProject", J_PUBLINOVA, "John was an initiator of Publinova, the repository for applied sciences."),
    (JOHN, "foaf:pastProject", J_CREAM, "Asking researchers to add their publications to repositories: starting open access by providing practical facilities."),
    (JOHN, "foaf:currentProject", J_IZ, "John initiated the SURF Open Science Innovation Zone, gaining strategic buy-in from universities and universities of applied sciences, and connected it to the Research Infrastructure zone."),
    (JOHN, "swan:relatedTo", P_UNL, "Supervision of the UNL study on alternative open access platforms."),
    (JOHN, "foaf:pastProject", J_EP, "Making dynamic papers: John presented and promoted Enhanced Publications internationally."),
    (JOHN, "foaf:workplaceHomepage", SURF, "Employment from the ORCID record: " + ORCID_RECORD["employment"] + ".", JOHN),
    (P_COMMONS, "dcterms:creator", JOHN, "John's most recent output (version %s, %s)." % (
        RECORDS["10.5281/zenodo.21526773"]["version"], RECORDS["10.5281/zenodo.21526773"]["date"])),
]
# Author position of John on each Zenodo record, from the source order
for doi, rec in RECORDS.items():
    names = [c["name"] for c in rec["creators"]]
    pos = names.index("Doove, John")
    text = "Author %d of %d" % (pos + 1, len(names))
    if pos:
        text += ", after " + ", ".join(display_name(n) for n in names[:pos])
    annotations.append((doi_uri(doi), "dcterms:creator", JOHN, text + "."))

for i, (subj, pred, obj, text, *source) in enumerate(annotations, 1):
    res(BASE + "annotation/%d" % i, ANNOT,
        L("dcterms:description", text),
        *[R("dcterms:source", src) for src in source],
        R("escape-annotations:subject", subj),
        R("escape-annotations:predicate", NS[pred.split(":")[0]] + pred.split(":")[1]),
        R("escape-annotations:object", obj))

# ---------------------------------------------------------------- write
ids = [u for u, _, _ in resources]
assert len(ids) == len(set(ids)), "duplicate URIs"
known = set(ids) | {JOHN}
for u, _, props in resources:
    for p, v, is_uri in props:
        if is_uri and p in ("foaf:homepage", "dcterms:source"):
            continue
        if is_uri and p != "escape-annotations:predicate" and v not in known:
            raise SystemExit("dangling reference %s -> %s" % (u, v))

out = ['<?xml version="1.0" encoding="UTF-8"?>',
       "<!-- Generated by scripts/gen_john_data.py from scratch/john_zenodo.json — do not edit manually.",
       "     The career of John Doove (%s) as an Enhanced Publication, shown by index.html#john." % JOHN,
       "     Uses the vocabulary of example_schema.json. -->",
       "<rdf:RDF " + "\n  ".join('xmlns:%s="%s"' % kv for kv in NS.items()) + ">", ""]
out += ['  <rdf:Description rdf:about=%s>' % quoteattr(REM),
        '    <rdf:type rdf:resource="http://www.openarchives.org/ore/terms/ResourceMap"/>',
        '    <dcterms:created>2026-09-29</dcterms:created>',
        '    <ore:describes rdf:resource=%s/>' % quoteattr(AGG),
        '    <dcterms:creator>SURF Open Science team</dcterms:creator>',
        '  </rdf:Description>', '']
out += ['  <rdf:Description rdf:about=%s>' % quoteattr(AGG),
        '    <rdf:type rdf:resource="http://purl.org/info:eu-repo/semantics/EnhancedPublication"/>',
        '    <rdf:type rdf:resource="http://www.openarchives.org/ore/terms/Aggregation"/>',
        '    <dcterms:title>John Doove — a career in open science</dcterms:title>',
        '    <dcterms:creator rdf:resource=%s/>' % quoteattr(JOHN),
        '    <dcterms:source>%s</dcterms:source>' % escape(DATA["source"])]
out += ['    <ore:aggregates rdf:resource=%s/>' % quoteattr(u) for u in ids]
out += ['  </rdf:Description>', '']
for u, t, props in resources:
    out.append('  <rdf:Description rdf:about=%s>' % quoteattr(u))
    out.append('    <rdf:type rdf:resource=%s/>' % quoteattr(t))
    for p, v, is_uri in props:
        if is_uri:
            out.append('    <%s rdf:resource=%s/>' % (p, quoteattr(v)))
        else:
            out.append('    <%s>%s</%s>' % (p, escape(v), p))
    out.append('  </rdf:Description>')
    out.append('')
out.append('</rdf:RDF>')

open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote %d resources" % len(resources))
