# absolute-structural

Private plugin for Absolute Drafting. Not for distribution.

## What it does

Adds one skill, `as-structural-design`, which Claude loads when asked to size, check or
document a structural member or a house frame:

- Timber to AS 1720.1, and house framing, bracing and tie-down to AS 1684.2
- Reinforced concrete to AS 3600, site classes to AS 2870
- Structural steel to AS 4100
- Loads and combinations to AS/NZS 1170 and AS 4055

It includes a calculator that prints calc sheets with clause references, reference files per
standard, and a framing schedule template.

## Before relying on it

Most design values in the reference files are marked `[U]` - written from memory of the
standards and not yet checked against them. Values marked `[C]` were matched to a published
secondary source. Check the `[U]` values against the purchased standards in the Knowledge
Vault before using a result in issued documentation.

The AS 1684.2 span tables are not included; member sizes are read from the standard or a
manufacturer's table.

## Requirements

- Python 3 for the calculator (no extra packages)
- Desktop Commander, to read the Knowledge Vault at `D:\Knowledge Vault 2026\`

## Installing

Open the `absolute-structural.plugin` file in the Claude desktop app and accept it. If the
standalone `as-structural-design` skill was installed earlier, remove it so the skill is not
loaded twice.
