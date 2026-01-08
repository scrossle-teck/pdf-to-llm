
---
title: {{symbolic_identifier}}            # e.g., POST_Login, GET_Agent, DELETE_RetireAgent
type: endpoint
product: Commvault Platform
vendor: Commvault
language: HTTP
domain: {{functional_grouping}}           # e.g., authentication, agent, alert
llm_use: procedural
prerequisites:
  - {{explicit_dependency_1}}
  - {{explicit_dependency_2}}
inputs: {{inputs_block_or_list}}          # Preserve required/optional, types, positions, enums
outputs: {{outputs_block_or_list}}        # Preserve response schema & codes
state_effect: {{creates|updates|deletes|queries|none}}
tags:
  - REST
  - {{additional_tags}}
source:
  type: pdf
  title: Commvault 11.36 REST API
  section: {{pdf_section_heading}}
---

# {{Exact Title}}                         <!-- Copy as printed in the PDF -->

## Purpose
{{verbatim_purpose_text}}

## Prerequisites
- {{bullet_1}}
- {{bullet_2}}
- Refer to **shared/common-concepts.md** for authentication headers, tokens, and status codes.

## Syntax
```text
{{verbatim_syntax_from_pdf}}
```

## Parameters / Inputs
<!-- Preserve REQUIRED vs OPTIONAL, data types, positions, enumerations, wildcard/pattern behavior, streaming -->
{{verbatim_parameters_from_pdf}}

## Output / Response
{{verbatim_response_structure_from_pdf}}

## Examples
```text
{{ALL_examples_verbatim_from_PDF}}
```

## Notes
{{warnings_constraints_limits_rest_notes_verbatim}}
