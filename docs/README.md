# Radspion documentation

Secret-organization-themed mission platform for coursework. Students (**agents**) in **groups** complete **missions** using unlock and completion codes, **Mission Briefs**, and **Debriefs**.

## Start here (for development)

Read in order:

1. [design/01-overview.md](design/01-overview.md) — product scope and V1 goals  
2. [design/02-entities.md](design/02-entities.md) — data model (conceptual)  
3. [design/03-database-schema.md](design/03-database-schema.md) — tables (SQLite)  
4. [design/04-example-data-walkthrough.md](design/04-example-data-walkthrough.md) — canonical example in SQL rows  
5. [design/05-example-class.md](design/05-example-class.md) — example class cheat sheet  
6. [design/06-agent-experience.md](design/06-agent-experience.md) — agent UI rules  
7. [design/07-operator-setup.md](design/07-operator-setup.md) — how you configure data today  
8. [design/use-cases.md](design/use-cases.md) — V1 use cases ordered by dependency (work backlog)

**UI mockups:** [ui/README.md](ui/README.md) — static HTML/CSS prototypes (build before Jinja templates)

**SQL:** [src/radspion/sql/schema.sql](../src/radspion/sql/schema.sql), [src/radspion/sql/seed_example_class.sql](../src/radspion/sql/seed_example_class.sql)

**Development:** [dev.md](dev.md) · **API outline:** [api.yaml](api.yaml)
