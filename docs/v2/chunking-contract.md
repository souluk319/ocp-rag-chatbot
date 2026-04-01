# v2 Chunking Contract

## Purpose

This document defines the first implementation-ready chunking contract for the v2 OCP operations assistant.

The contract exists to close the earlier feedback that chunking strategy was underspecified.

It must satisfy both:

- retrieval quality
- citation alignment to the HTML document view

## Scope

This contract applies to the normalized `openshift-docs` corpus produced from the P0 validation slice first.

It is designed for:

- official OCP documentation
- sectioned AsciiDoc source
- Korean Q&A generated from English source material
- citation click-through through internal HTML views

## Design assumptions

1. chunking happens after `.adoc` normalization into a canonical document model
2. chunking does not operate on raw `.adoc`
3. every chunk must map back to one document section and one citation target
4. chunk boundaries are subordinate to document meaning, not just token limits

## Chunk types

### `prose`

Use for explanatory paragraphs and narrative guidance.

Rules:

- preferred size: `350-650` tokens
- soft overlap: `60-100` tokens only when a long section must split
- do not cross into a different section heading just to satisfy target size

### `procedure`

Use for ordered steps, runbooks, installation procedures, and upgrade flows.

Rules:

- keep the full step sequence intact whenever possible
- if the procedure is too long, split only at stable sub-step boundaries
- preserve explicit step numbers or bullet order in the chunk text

### `code`

Use for commands, CLI examples, shell snippets, YAML blocks, and code fences.

Rules:

- code becomes its own chunk
- keep the nearest heading and short explanatory context in metadata
- do not mix large prose blocks into the same chunk

### `reference`

Use for short option lists, release-note style advisories, parameter descriptions, and concise lookup material.

Rules:

- chunk the smallest self-contained reference unit that still makes sense
- avoid combining unrelated reference entries into one large chunk

## Boundary rules

The following rules are mandatory:

1. a chunk starts inside one heading path and stays inside that heading path
2. a chunk must not span unrelated sibling sections
3. a chunk must not break a short ordered procedure into separate answers without reason
4. a chunk must not split a code block in the middle
5. a chunk must preserve enough local context for citation inspection

## Section and citation alignment

Each chunk must resolve to:

- one `document_id`
- one `section_id`
- one `section_anchor`
- one `viewer_url`

Citation alignment rules:

1. `viewer_url#section_anchor` must open the correct HTML section
2. the `section_title` shown in retrieval metadata must match the cited section
3. `heading_hierarchy` must remain stable enough to explain where the chunk came from

## Metadata requirements

Chunk metadata must include at least:

- `chunk_id`
- `document_id`
- `section_id`
- `chunk_type`
- `chunk_index`
- `token_count`
- `section_title`
- `heading_hierarchy`
- `section_anchor`
- `viewer_url`
- `source_url`
- `product`
- `version`
- `category`
- `trust_level`

Recommended:

- `char_start`
- `char_end`
- `excerpt`
- `prev_chunk_id`
- `next_chunk_id`

## First implementation plan

The first implementation should be done in this order:

1. derive a stable section tree from the normalized document
2. emit section metadata first
3. split sections into chunk candidates by type
4. apply size and overlap rules
5. emit chunk records with citation metadata
6. verify that chunk -> HTML section mapping still works

## Validation checklist

Stage 3 is complete only if all of the following are true:

1. chunk types are fixed
2. token and overlap targets are fixed
3. procedure and code handling rules are fixed
4. chunk metadata fields are fixed
5. citation alignment rules are fixed
6. one sample normalized document can be expressed as chunk records using this contract

## Sample interpretation

Example:

- a top-level installation narrative becomes one or more `prose` chunks
- a numbered install procedure becomes one or more `procedure` chunks
- an `oc` command block becomes a `code` chunk tied to the nearest section
- a short release-note advisory becomes a `reference` chunk

## Handoff to Stage 4

Once this contract is fixed, the next stage is:

- emit HTML citation views
- emit stable `viewer_url`
- confirm section-anchor alignment on sample documents
