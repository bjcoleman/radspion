# Radspion documentation

Secret-organization-themed mission platform for coursework. Students (**agents**) complete **missions** in story **arcs** using **clearance** to list new missions and **data** to complete them.

## Start here (for development)

Read in order:

1. [design/01-overview.md](design/01-overview.md) — product scope and V1 goals  
2. [design/02-entities.md](design/02-entities.md) — data model (conceptual)  
3. [design/03-database-schema.md](design/03-database-schema.md) — tables (SQLite)  
4. [design/04-example-data-walkthrough.md](design/04-example-data-walkthrough.md) — Testing Storyline test data in SQL  
5. [design/05-testing-storyline.md](design/05-testing-storyline.md) — Testing Storyline acceptance cheat sheet (dev/test only)  
6. [design/06-agent-experience.md](design/06-agent-experience.md) — clearance, data, and agent UI  
7. [design/07-operator-setup.md](design/07-operator-setup.md) — how you configure data today  
8. [design/use-cases.md](design/use-cases.md) — V1 use cases ordered by dependency (work backlog)

**UI mockups:** [ui/README.md](ui/README.md) — static HTML/CSS prototypes (build before Jinja templates)

**SQL (infrastructure):** [src/radspion/sql/README.md](../src/radspion/sql/README.md) — schema and seeds (mission markdown inlined)

**Development:** [dev.md](dev.md) · **JSON API (OpenAPI):** [api.yaml](api.yaml)

**Mission packs:** [radspion-missions](https://github.com/MoravianUniversity/radspion-missions) — `docs/authoring-guide.md` for pack authors
