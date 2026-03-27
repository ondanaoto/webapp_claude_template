#!/usr/bin/env python3
"""
Generate ERD HTML from ent schema files.
Usage: python generate_erd.py <schema_dir> <output_html>
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Field:
    name: str
    type: str
    pk: bool = False
    fk: bool = False
    nullable: bool = False


@dataclass
class Edge:
    name: str
    target: str
    unique: bool = False
    required: bool = False
    is_from: bool = False  # edge.From vs edge.To


@dataclass
class Mixin:
    name: str
    fields: list[Field] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


@dataclass
class Entity:
    name: str
    fields: list[Field] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


def parse_go_type(go_code: str) -> str:
    """Map Go field type to ERD type."""
    if "UUID" in go_code or "uuid.UUID" in go_code:
        return "UUID"
    if "String" in go_code:
        return "STRING"
    if "Text" in go_code:
        return "TEXT"
    if "Int" in go_code:
        return "INTEGER"
    if "Float" in go_code:
        return "FLOAT"
    if "Bool" in go_code:
        return "BOOLEAN"
    if "Time" in go_code:
        return "TIMESTAMP"
    if "Enum" in go_code:
        return "ENUM"
    if "JSON" in go_code:
        return "JSON"
    if "Bytes" in go_code:
        return "BYTES"
    return "UNKNOWN"


def parse_fields_block(fields_block: str) -> list[Field]:
    """Parse fields from a Fields() function block."""
    fields = []
    field_pattern = re.compile(r'field\.(\w+)\("(\w+)"')
    for match in field_pattern.finditer(fields_block):
        field_type = match.group(1)
        field_name = match.group(2)

        # Get the field definition context
        start = match.start()
        end = fields_block.find('),', start)
        if end == -1:
            end = len(fields_block)
        field_context = fields_block[start:end]

        f = Field(
            name=field_name,
            type=parse_go_type(field_type),
            pk=field_name == "id",
            fk="_id" in field_name and field_name != "id",
            nullable=".Optional()" in field_context or ".Nillable()" in field_context
        )
        fields.append(f)
    return fields


def parse_edges_block(edges_block: str) -> list[Edge]:
    """Parse edges from an Edges() function block."""
    edges = []

    # Parse edge.To
    to_pattern = re.compile(r'edge\.To\("(\w+)",\s*(\w+)\.Type\)')
    for match in to_pattern.finditer(edges_block):
        edge_name = match.group(1)
        target = match.group(2)

        start = match.start()
        end = edges_block.find('),', start)
        if end == -1:
            end = len(edges_block)
        else:
            end += 1  # ')' を含める
        edge_context = edges_block[start:end]

        edges.append(Edge(
            name=edge_name,
            target=target,
            unique=".Unique()" in edge_context,
            required=".Required()" in edge_context,
            is_from=False
        ))

    # Parse edge.From
    from_pattern = re.compile(r'edge\.From\("(\w+)",\s*(\w+)\.Type\)')
    for match in from_pattern.finditer(edges_block):
        edge_name = match.group(1)
        target = match.group(2)

        start = match.start()
        end = edges_block.find('),', start)
        if end == -1:
            end = len(edges_block)
        else:
            end += 1  # ')' を含める
        edge_context = edges_block[start:end]

        edges.append(Edge(
            name=edge_name,
            target=target,
            unique=".Unique()" in edge_context,
            required=".Required()" in edge_context,
            is_from=True
        ))

    return edges


def parse_mixin_definitions(schema_dir: Path) -> dict[str, Mixin]:
    """Parse all mixin definitions from schema files.

    Mixins are identified by embedding mixin.Schema instead of ent.Schema.
    """
    mixins: dict[str, Mixin] = {}

    for go_file in schema_dir.glob("*.go"):
        content = go_file.read_text()

        # Find mixin structs (embed mixin.Schema)
        mixin_pattern = re.compile(r'type\s+(\w+)\s+struct\s*\{\s*mixin\.Schema')
        for match in mixin_pattern.finditer(content):
            mixin_name = match.group(1)
            mixin = Mixin(name=mixin_name)

            # Extract Fields function for this mixin
            fields_match = re.search(
                rf'func\s+\({mixin_name}\)\s+Fields\(\)\s+\[\]ent\.Field\s*\{{([\s\S]*?)^\}}',
                content,
                re.MULTILINE
            )
            if fields_match:
                mixin.fields = parse_fields_block(fields_match.group(1))

            # Extract Edges function for this mixin
            edges_match = re.search(
                rf'func\s+\({mixin_name}\)\s+Edges\(\)\s+\[\]ent\.Edge\s*\{{([\s\S]*?)^\}}',
                content,
                re.MULTILINE
            )
            if edges_match:
                mixin.edges = parse_edges_block(edges_match.group(1))

            mixins[mixin_name] = mixin
            print(f"Found mixin: {mixin_name} ({len(mixin.fields)} fields, {len(mixin.edges)} edges)")

    return mixins


def parse_entity_mixins(content: str) -> list[str]:
    """Extract mixin names from entity's Mixin() function."""
    mixin_names = []

    # Match: func (X) Mixin() []ent.Mixin { return []ent.Mixin{...} }
    mixin_func_match = re.search(
        r'func\s+\(\w+\)\s+Mixin\(\)\s+\[\]ent\.Mixin\s*\{([\s\S]*?)^\}',
        content,
        re.MULTILINE
    )
    if mixin_func_match:
        mixin_block = mixin_func_match.group(1)
        # Find mixin usages like: LanguageMixin{}, AnotherMixin{}
        mixin_usage_pattern = re.compile(r'(\w+)\{\}')
        for match in mixin_usage_pattern.finditer(mixin_block):
            mixin_names.append(match.group(1))

    return mixin_names


def parse_schema_file(file_path: Path, mixins: dict[str, Mixin] | None = None) -> Entity | None:
    """Parse a single ent schema file.

    Args:
        file_path: Path to the Go schema file
        mixins: Dictionary of parsed mixin definitions to merge fields from
    """
    content = file_path.read_text()

    # Extract struct name (entity name)
    struct_match = re.search(r'type\s+(\w+)\s+struct\s*\{\s*ent\.Schema', content)
    if not struct_match:
        return None

    entity_name = struct_match.group(1)
    entity = Entity(name=entity_name)

    # Collect mixin fields first (they come before entity's own fields)
    mixin_fields: list[Field] = []
    mixin_edges: list[Edge] = []
    if mixins:
        entity_mixin_names = parse_entity_mixins(content)
        for mixin_name in entity_mixin_names:
            if mixin_name in mixins:
                mixin = mixins[mixin_name]
                mixin_fields.extend(mixin.fields)
                mixin_edges.extend(mixin.edges)

    # Extract entity's own Fields
    entity_fields: list[Field] = []
    fields_match = re.search(r'func\s+\(\w+\)\s+Fields\(\)\s+\[\]ent\.Field\s*\{([\s\S]*?)^\}', content, re.MULTILINE)
    if fields_match:
        entity_fields = parse_fields_block(fields_match.group(1))

    # Merge fields: entity fields first, then mixin fields at the end
    # Entity fields override mixin fields with the same name
    entity_field_names = {f.name for f in entity_fields}
    entity.fields.extend(entity_fields)
    for mixin_field in mixin_fields:
        if mixin_field.name not in entity_field_names:
            entity.fields.append(mixin_field)

    # Extract entity's own Edges
    entity_edges: list[Edge] = []
    edges_match = re.search(r'func\s+\(\w+\)\s+Edges\(\)\s+\[\]ent\.Edge\s*\{([\s\S]*?)^\}', content, re.MULTILINE)
    if edges_match:
        entity_edges = parse_edges_block(edges_match.group(1))

    # Merge edges: entity edges first, then mixin edges at the end
    entity_edge_names = {e.name for e in entity_edges}
    entity.edges.extend(entity_edges)
    for mixin_edge in mixin_edges:
        if mixin_edge.name not in entity_edge_names:
            entity.edges.append(mixin_edge)

    return entity


def generate_mermaid(entities: list[Entity]) -> str:
    """Generate Mermaid ERD from entities."""
    lines = ["erDiagram"]

    # Entity definitions
    for entity in entities:
        lines.append(f"    {entity.name} {{")
        for f in entity.fields:
            suffix = ""
            if f.pk:
                suffix = " PK"
            elif f.fk:
                suffix = " FK"
            if f.nullable and not suffix:
                suffix = " \"?\""
            lines.append(f"        {f.type} {f.name}{suffix}")
        lines.append("    }")

    # Relationships (only from edge.To to avoid duplicates)
    lines.append("")
    entity_map = {e.name: e for e in entities}

    for entity in entities:
        for edge in entity.edges:
            if edge.is_from:
                continue  # Skip edge.From to avoid duplicate relationships

            if edge.target not in entity_map:
                continue

            # Determine cardinality
            if edge.unique:
                rel = "||--||"  # One-to-One
            else:
                rel = "||--o{"  # One-to-Many

            lines.append(f'    {entity.name} {rel} {edge.target} : "{edge.name}"')

    return "\n".join(lines)


def generate_html(mermaid_code: str, title: str = "ER Diagram") -> str:
    """Generate HTML with Mermaid diagram."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .legend {{
            max-width: 600px;
            margin: 20px auto;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend h3 {{
            margin-top: 0;
            color: #555;
        }}
        .legend ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .legend li {{
            margin: 5px 0;
            color: #666;
        }}
        .legend code {{
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .mermaid {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>

    <div class="legend">
        <h3>Legend</h3>
        <ul>
            <li><code>||--||</code> One-to-One (1:1)</li>
            <li><code>||--o{{</code> One-to-Many (1:N)</li>
            <li><code>PK</code> Primary Key</li>
            <li><code>FK</code> Foreign Key</li>
            <li><code>?</code> Nullable field</li>
        </ul>
    </div>

    <div class="mermaid">
{mermaid_code}
    </div>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            er: {{
                layoutDirection: 'TB',
                minEntityWidth: 100,
                minEntityHeight: 75,
                entityPadding: 15
            }}
        }});
    </script>
</body>
</html>
'''


def generate_markdown(mermaid_code: str, title: str = "ER Diagram") -> str:
    """Generate Markdown with Mermaid diagram."""
    return f'''# {title}

## Legend

- `||--||` One-to-One (1:1)
- `||--o{{` One-to-Many (1:N)
- `PK` Primary Key
- `FK` Foreign Key
- `?` Nullable field

## Diagram

```mermaid
{mermaid_code}
```
'''


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_erd.py <schema_dir> <output_html>")
        print("Example: python generate_erd.py apps/api-server/ent/schema docs/generated/erd.html")
        sys.exit(1)

    schema_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not schema_dir.exists():
        print(f"Error: Schema directory not found: {schema_dir}")
        sys.exit(1)

    # Pass 1: Parse mixin definitions
    print("=== Parsing mixins ===")
    mixins = parse_mixin_definitions(schema_dir)

    # Pass 2: Parse all schema files with mixin support
    print("\n=== Parsing entities ===")
    entities = []
    for go_file in schema_dir.glob("*.go"):
        entity = parse_schema_file(go_file, mixins)
        if entity:
            entities.append(entity)
            print(f"Parsed: {entity.name} ({len(entity.fields)} fields, {len(entity.edges)} edges)")

    if not entities:
        print("Error: No entities found in schema directory")
        sys.exit(1)

    # Sort entities by name for consistent output
    entities.sort(key=lambda e: e.name)

    # Generate Mermaid code
    mermaid_code = generate_mermaid(entities)

    # Generate and write HTML
    title = "Curripedia Entity Relationship Diagram"
    html_content = generate_html(mermaid_code, title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content)
    print(f"\nGenerated: {output_path}")

    # Also generate markdown if requested
    md_output = output_path.with_suffix('.md')
    md_content = generate_markdown(mermaid_code, title)
    md_output.write_text(md_content)
    print(f"Generated: {md_output}")

    print(f"\nTotal: {len(entities)} entities, {len(mixins)} mixins")


if __name__ == "__main__":
    main()
