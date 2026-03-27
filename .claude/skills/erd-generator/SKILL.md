---
name: erd-generator
description: >
  Generate ERD (Entity Relationship Diagram) from ent schema files.
  Use when ent schema files (apps/api-server/ent/schema/*.go) are updated,
  user asks to update or regenerate the ERD, user asks to visualize database schema,
  or after adding/modifying database entities.
  Triggers on keywords like ERD, ER diagram, schema diagram, database diagram, update erd, generate erd.
---

# ERD Generator

Generate Mermaid-based ERD from Go ent schema files.

## Workflow

1. Run the generation task:
   ```bash
   task docs:erd
   ```

2. This generates both:
   - `docs/generated/erd.html` - Interactive HTML with Mermaid rendering
   - `docs/generated/erd.md` - Markdown with Mermaid code block

3. Open in browser to verify:
   ```bash
   open docs/generated/erd.html
   ```

## When to Trigger

Run this skill automatically when:
- Any file in `apps/api-server/ent/schema/*.go` is modified
- User adds a new entity or modifies existing entity fields/edges
- User explicitly requests ERD update

## Script Details

The `scripts/generate_erd.py` script:
- Parses Go ent schema files to extract entities, fields, and edges
- Maps Go types to ERD types (UUID, STRING, INTEGER, TIMESTAMP, etc.)
- Identifies PK/FK relationships from field names and edge definitions
- Generates Mermaid ERD syntax with proper cardinality (1:1, 1:N)
- Outputs styled HTML and Markdown files
