#!/usr/bin/env python3
"""Generate the PhiSQL documentation site from the spec artifacts.

The spec is a set of machine-readable artifacts under ``spec/<version>/``:
the grammar (``grammar/PhiSQL.ebnf``), the catalog YAML files, and the
example ``.phisql``/``.json`` pairs. There is no prose specification document
-- the artifacts are the spec. This script renders those artifacts into the
Markdown pages that MkDocs builds into the published site, so the published
reference can never drift from the catalogs it is generated from.

It runs two ways:

* As an `mkdocs-gen-files`_ plugin script during ``mkdocs build``/``serve``.
  The generated pages are virtual (never written to the working tree), so
  there is nothing generated to commit and nothing to keep in sync by hand.

* Standalone for inspection or CI dry-runs::

      python scripts/gen_docs.py --out /tmp/phisql-docs

  which writes the same Markdown tree to a real directory.

.. _mkdocs-gen-files: https://oprypin.github.io/mkdocs-gen-files/
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# The spec version this site documents. The directory under spec/ that the
# pages are generated from. (The site itself is versioned separately, by
# `mike`, tracking documentation releases.)
SPEC_VERSION = "v1.0"

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "spec" / SPEC_VERSION
CATALOG_DIR = SPEC_DIR / "catalog"
GRAMMAR_DIR = SPEC_DIR / "grammar"
EXAMPLES_DIR = SPEC_DIR / "examples"

# Link to the grammar and catalog sources on GitHub so readers can jump from
# a rendered page to the artifact it was generated from.
SRC_BASE = f"https://github.com/philterd/phisql/blob/main/spec/{SPEC_VERSION}"


# --------------------------------------------------------------------------
# Artifact loading
# --------------------------------------------------------------------------

def load_catalog(name: str) -> dict:
    with (CATALOG_DIR / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_ebnf(text: str) -> dict[str, str]:
    """Parse the EBNF into an ordered map of rule name -> full production text.

    Block comments ``(* ... *)`` are stripped first, then the grammar is split
    on the ``;`` that terminates every production. The rule name is the text
    before the first `` = `` separator; ``=`` only appears bare as a separator
    because the ``"="`` terminal is always quoted.
    """
    text = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    rules: dict[str, str] = {}
    for chunk in text.split(";"):
        chunk = chunk.strip()
        if not chunk or " = " not in chunk:
            continue
        name, _ = chunk.split(" = ", 1)
        name = " ".join(name.split())
        rules[name] = chunk + " ;"
    return rules


# --------------------------------------------------------------------------
# Example introspection
# --------------------------------------------------------------------------

# Maps the leading token(s) of a statement to a stable verb id used to
# cross-link verbs and the examples that exercise them.
_VERB_BY_LEAD = {
    ("POLICY",): "policy",
    ("CONFIGURE",): "configure",
    ("REDACT",): "redact",
    ("DEIDENTIFY",): "deidentify",
    ("IGNORE",): "ignore",
    ("DEFINE", "IDENTIFIER"): "define-identifier",
    ("DEFINE", "DICTIONARY"): "define-dictionary",
    ("DEFINE", "SECTION"): "define-section",
    ("DETECT",): "detect",
    ("FIND",): "discovery",
    ("DISCOVER",): "discovery",
    ("SCAN",): "discovery",
    ("SELECT",): "discovery",
}


def strip_phisql_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"--[^\n]*", "", src)
    return src


def verbs_in_example(src: str) -> set[str]:
    """Return the set of verb ids whose statements appear in this example."""
    found: set[str] = set()
    for stmt in strip_phisql_comments(src).split(";"):
        tokens = stmt.split()
        if not tokens:
            continue
        lead1 = (tokens[0].upper(),)
        lead2 = tuple(t.upper() for t in tokens[:2])
        if lead2 in _VERB_BY_LEAD:
            found.add(_VERB_BY_LEAD[lead2])
        elif lead1 in _VERB_BY_LEAD:
            found.add(_VERB_BY_LEAD[lead1])
    return found


def example_title(src: str, stem: str) -> str:
    """First ``--`` comment line of an example, used as its title."""
    for line in src.splitlines():
        line = line.strip()
        if line.startswith("--"):
            return line.lstrip("-").strip().rstrip(".")
    return stem


def load_examples() -> list[dict]:
    examples = []
    for phisql_path in sorted(EXAMPLES_DIR.glob("*.phisql")):
        stem = phisql_path.stem
        src = phisql_path.read_text(encoding="utf-8")
        json_path = phisql_path.with_suffix(".json")
        examples.append(
            {
                "stem": stem,
                "title": example_title(src, stem),
                "phisql": src.rstrip() + "\n",
                "json": json_path.read_text(encoding="utf-8").rstrip() + "\n"
                if json_path.exists()
                else None,
                "verbs": verbs_in_example(src),
            }
        )
    return examples


# --------------------------------------------------------------------------
# Page rendering helpers
# --------------------------------------------------------------------------

def grammar_block(rules: dict[str, str], *names: str) -> str:
    """An EBNF code block containing the named production(s)."""
    bodies = [rules[n] for n in names if n in rules]
    return "```ebnf\n" + "\n\n".join(bodies) + "\n```\n"


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def front(title: str) -> str:
    return f"# {title}\n\n"


GENERATED_NOTE = (
    "*This page is generated from the PhiSQL "
    f"[spec artifacts]({SRC_BASE}) for `{SPEC_VERSION}`. "
    "Do not edit it by hand; change the artifact and rebuild.*\n\n"
)


# --------------------------------------------------------------------------
# Individual pages
# --------------------------------------------------------------------------

def page_grammar(rules: dict[str, str], ebnf_text: str) -> str:
    out = front("Grammar")
    out += GENERATED_NOTE
    out += (
        "PhiSQL's grammar is defined in two equivalent forms. The "
        f"[ANTLR4 grammar]({SRC_BASE}/grammar/PhiSQL.g4) is the executable "
        "normative reference that the [reference implementation]"
        "(https://github.com/philterd/phisql/tree/main/reference) generates "
        f"its parser from. The [ISO&nbsp;14977 EBNF]({SRC_BASE}/grammar/PhiSQL.ebnf) "
        "below is a tool-independent presentation, cross-validated against the "
        "ANTLR4 grammar.\n\n"
    )
    out += (
        "Keywords and entity-type identifiers are case-insensitive. "
        "User-defined names (policy names, dictionary names, custom-identifier "
        "classifications) are case-sensitive.\n\n"
    )
    out += "## Production rules\n\n"
    out += "| Rule | Defined in |\n|---|---|\n"
    for name in rules:
        anchor = name.replace(" ", "-")
        out += f"| [`{name}`](#{anchor}) | EBNF |\n"
    out += "\n## Full grammar\n\n"
    # Render each production with an anchor heading so the table links resolve.
    for name, body in rules.items():
        out += f"### {name}\n\n```ebnf\n{body}\n```\n\n"
    return out


def page_verbs(rules: dict[str, str], examples: list[dict]) -> str:
    # The narrative ordering and one-line summary for each verb; the grammar
    # and example links are pulled from the artifacts.
    verbs = [
        ("policy", "POLICY", ["policy decl"],
         "Declares a named policy and, optionally, a human-readable "
         "description. The name is optional and, when present, must match the "
         "file basename after hyphen/underscore normalization."),
        ("configure", "CONFIGURE", ["configure stmt"],
         "Sets document-wide configuration: encryption keys (read from "
         "environment variables), and splitting, PDF, post-filter, analysis, "
         "and graphical-redaction settings."),
        ("redact", "REDACT", ["redact stmt"],
         "Applies a strategy to one or more entity types, optionally gated by "
         "a `WHERE` predicate and tuned with per-filter `OPTIONS`."),
        ("deidentify", "DEIDENTIFY", ["deidentify stmt", "entity assignment"],
         "Assigns a strategy to each of several entity types in one statement "
         "using `<entity> AS <strategy>` pairs."),
        ("ignore", "IGNORE", ["ignore stmt"],
         "Suppresses detections that match a list of terms or a regular "
         "expression, either policy-wide or scoped to specific entities."),
        ("define-identifier", "DEFINE IDENTIFIER", ["define identifier stmt"],
         "Defines a custom identifier from a regular expression and redacts "
         "what it matches."),
        ("define-dictionary", "DEFINE DICTIONARY", ["define dictionary stmt"],
         "Defines a custom dictionary of terms, optionally fuzzy-matched, and "
         "redacts them."),
        ("define-section", "DEFINE SECTION", ["define section stmt"],
         "Redacts everything between a start and end regular expression."),
        ("detect", "DETECT PHEYE", ["detect stmt"],
         "Runs PhEye (AI/NER) detection -- for example, person-name detection "
         "-- with optional labels and a custom endpoint."),
        ("discovery", "FIND PII / DISCOVER ENTITIES / SCAN / SELECT",
         ["discovery stmt", "in clause", "where discovery", "discovery predicate",
          "projection list", "projection", "aggregate"],
         "Discovery and query verbs: scan a source for PII (`FIND PII`, "
         "`DISCOVER ENTITIES`, `SCAN`) or query the findings store "
         "(`SELECT ... FROM findings`)."),
    ]
    out = front("Verbs")
    out += GENERATED_NOTE
    out += (
        "A PhiSQL document is a sequence of statements, each terminated by "
        "`;`. Each statement begins with a verb. The verbs below are the "
        "top-level alternatives of the `statement` production.\n\n"
    )
    out += grammar_block(rules, "document", "statement")
    out += "\n"
    for vid, heading, rule_names, summary in verbs:
        out += f"## {heading}\n\n{summary}\n\n"
        present = [n for n in rule_names if n in rules]
        if present:
            out += grammar_block(rules, *present) + "\n"
        ex = [e for e in examples if vid in e["verbs"]]
        if ex:
            out += "**Examples:** " + ", ".join(
                f"[{e['stem']}](../examples/{e['stem']}.md)" for e in ex[:12]
            ) + "\n\n"
    return out


def page_clauses(rules: dict[str, str]) -> str:
    clauses = [
        ("WITH (strategy expression)", ["strategy expr", "strategy name",
                                        "strategy args", "named arg"],
         "Attaches a filter strategy -- and its named arguments -- to a "
         "statement. See [Strategies](strategies.md) for each strategy's "
         "arguments."),
        ("WHERE (redaction predicate)", ["predicate", "confidence predicate",
                                         "compare op"],
         "Gates a redaction strategy on a condition. In v1.0 the only "
         "predicate is `CONFIDENCE`; see [Predicates](predicates.md)."),
        ("WHERE (discovery predicate)", ["where discovery", "discovery predicate"],
         "Filters discovered entities by findings-table columns before they "
         "reach the findings store. See [Findings](findings.md) for the "
         "columns."),
        ("OPTIONS", ["options clause", "setting list", "setting",
                     "setting key", "setting value", "object value",
                     "array value"],
         "Sets arbitrary leaf properties on the filter a statement compiles "
         "to, including nested objects and arrays."),
        ("IN", ["in clause"],
         "Names the discovery source URI. See [Sources](sources.md) for the "
         "recognized URI schemes."),
        ("GROUP BY", ["group by clause"],
         "Groups `SELECT ... FROM findings` rows for aggregation."),
        ("LIMIT", ["limit clause"],
         "Caps the number of rows returned by a `SELECT`."),
    ]
    out = front("Clauses")
    out += GENERATED_NOTE
    out += (
        "Clauses modify a verb. The same clause grammar is shared across "
        "statements -- for example, `WITH` and `OPTIONS` appear on most "
        "redaction verbs.\n\n"
    )
    for heading, rule_names, summary in clauses:
        out += f"## {heading}\n\n{summary}\n\n"
        present = [n for n in rule_names if n in rules]
        if present:
            out += grammar_block(rules, *present) + "\n"
    return out


def page_type_system(rules: dict[str, str]) -> str:
    out = front("Type system")
    out += GENERATED_NOTE
    out += (
        "PhiSQL's vocabulary is fixed by the catalog artifacts and the "
        "lexical grammar. This page summarizes the value types; the catalogs "
        "linked below are the source of truth for the named vocabularies.\n\n"
    )
    out += "## Literal value types\n\n"
    out += (
        "The right-hand side of a strategy argument, an `OPTIONS` setting, or "
        "a predicate is one of these lexical literals.\n\n"
    )
    out += grammar_block(
        rules, "literal", "string literal", "numeric literal",
        "boolean literal", "id",
    )
    out += "\n## Named vocabularies\n\n"
    out += (
        "| Vocabulary | What it names | Reference |\n|---|---|---|\n"
        "| Entity types | The PII categories a statement can target | "
        "[Entity types](entity-types.md) |\n"
        "| Strategies | How a detected value is transformed | "
        "[Strategies](strategies.md) |\n"
        "| Predicates | Conditions in a `WHERE` clause | "
        "[Predicates](predicates.md) |\n"
        "| Sources | URI schemes for discovery `IN` clauses | "
        "[Sources](sources.md) |\n"
        "| Findings columns | The findings-table schema queried by `SELECT` | "
        "[Findings](findings.md) |\n"
        "| Reserved keywords | Names that cannot be used as identifiers | "
        "[Keywords](keywords.md) |\n"
    )
    out += "\n## Strategy argument types\n\n"
    out += (
        "Each strategy argument declares a type in "
        "[`strategies.yaml`]("
        f"{SRC_BASE}/catalog/strategies.yaml): one of `string`, `integer`, "
        "`boolean`, or `enum`. `enum` arguments accept a bare identifier whose "
        "value must be one of the declared enum values.\n"
    )
    return out


def page_entity_types(cat: dict) -> str:
    out = front("Entity types")
    out += GENERATED_NOTE
    out += (
        "Each entity type targets a category of PII. The Phileas field is the "
        "property the type compiles to in the redaction policy JSON.\n\n"
    )
    out += "| Entity type | Description | Phileas field |\n|---|---|---|\n"
    for e in cat["entities"]:
        out += (
            f"| `{e['name']}` | {md_escape(e.get('description', ''))} | "
            f"`{e['phileas_field']}` |\n"
        )
    ci = cat.get("custom_identifier")
    if ci:
        out += (
            "\n## Custom identifiers\n\n"
            "Custom identifiers are referenced with `IDENTIFIER('<classification>')` "
            "and compile to an entry under "
            f"`{ci['phileas_path']}`. Define one with "
            "[`DEFINE IDENTIFIER`](verbs.md#define-identifier).\n"
        )
    deferred = cat.get("deferred")
    if deferred:
        out += "\n## Deferred to a later version\n\n"
        for d in deferred:
            out += f"### `{d['name']}`\n\n{d['rationale'].strip()}\n\n"
    return out


def page_strategies(cat: dict) -> str:
    out = front("Strategies")
    out += GENERATED_NOTE
    out += (
        "A strategy transforms a detected value. Attach one to a statement "
        "with the [`WITH`](clauses.md) clause.\n\n"
    )
    for s in cat["strategies"]:
        out += f"## {s['name']}\n\n{s.get('description', '').strip()}\n\n"
        out += f"Compiles to Phileas strategy `{s['phileas_enum']}`.\n\n"
        args = s.get("args")
        if args:
            out += "| Argument | Type | Required | Phileas field |\n"
            out += "|---|---|---|---|\n"
            for a in args:
                typ = a["type"]
                if typ == "enum":
                    typ = "enum: " + ", ".join(a.get("enum_values", []))
                req = "yes" if a.get("required") else "no"
                out += (
                    f"| `{a['name']}` | {typ} | {req} | "
                    f"`{a['phileas_field']}` |\n"
                )
            out += "\n"
        else:
            out += "*No arguments.*\n\n"
    return out


def page_predicates(cat: dict) -> str:
    out = front("Predicates")
    out += GENERATED_NOTE
    out += (
        "Predicates appear in a `WHERE` clause and gate a strategy on a "
        "condition. They compile to the Phileas `conditions` string on the "
        "strategy object.\n\n"
    )
    compose = cat.get("compose", {})
    ops = ", ".join(f"`{o['logical']}`" for o in compose.get("operators", []))
    if ops:
        out += f"Predicates combine with {ops} and may be parenthesized.\n\n"
    for p in cat["predicates"]:
        out += f"## {p['name']}\n\n{p.get('description', '').strip()}\n\n"
        cops = ", ".join(f"`{o}`" for o in p.get("compare_ops", []))
        out += f"- **Comparison operators:** {cops}\n"
        out += f"- **Value type:** {p.get('value_type', '')}\n"
        out += f"- **Compiles to:** `{p.get('phileas_template', '')}`\n\n"
    return out


def page_sources(cat: dict) -> str:
    out = front("Sources")
    out += GENERATED_NOTE
    out += (
        "Discovery statements (`FIND PII`, `DISCOVER ENTITIES`, `SCAN`) name "
        "their source with an `IN '<uri>'` clause. These are the recognized "
        "URI schemes. A conforming engine that does not support a scheme must "
        "reject the statement rather than silently no-op.\n\n"
    )
    out += "| Scheme | Source | URI template | Example |\n|---|---|---|---|\n"
    for s in cat["schemes"]:
        out += (
            f"| `{s['scheme']}` | {s['label']} | `{s['uri_template']}` | "
            f"`{s['example']}` |\n"
        )
    out += "\n"
    for s in cat["schemes"]:
        out += f"## {s['label']} (`{s['scheme']}`)\n\n"
        out += f"{md_escape(s.get('description', ''))}\n\n"
        out += f"- **URI template:** `{s['uri_template']}`\n"
        out += f"- **Example:** `{s['example']}`\n\n"
    return out


def page_findings(cat: dict) -> str:
    out = front("Findings")
    out += GENERATED_NOTE
    table = cat["table"]
    out += (
        f"Discovery scans produce rows in the `{table['name']}` table "
        f"(default namespace `{table['default_namespace']}`). "
        "`SELECT ... FROM findings` projects, filters, and aggregates over "
        "these columns; the discovery `WHERE` clause filters on the same "
        "column names.\n\n"
    )
    out += "| Column | Type | Required | Description |\n|---|---|---|---|\n"
    for c in cat["columns"]:
        req = "yes" if c.get("required") else "no"
        out += (
            f"| `{c['name']}` | {c['type']} | {req} | "
            f"{md_escape(c.get('description', ''))} |\n"
        )
    filt = cat.get("filterable_columns")
    if filt:
        out += "\n## Filterable columns\n\nColumns valid on the left-hand "
        out += "side of a `WHERE` predicate:\n\n"
        out += ", ".join(f"`{c}`" for c in filt) + "\n"
    grp = cat.get("groupable_columns")
    if grp:
        out += "\n## Groupable columns\n\nColumns valid in a `GROUP BY` "
        out += "clause:\n\n"
        out += ", ".join(f"`{c}`" for c in grp) + "\n"
    return out


def page_policy_naming(cat: dict) -> str:
    out = front("Policy naming")
    out += GENERATED_NOTE
    out += (
        "The Phileas JSON policy schema has no top-level name or description "
        "field; policy identity comes from the filename. These rules bridge "
        "that convention with PhiSQL's optional `POLICY` declaration.\n\n"
    )

    def section(key: str, heading: str) -> str:
        node = cat.get(key)
        if not node:
            return ""
        body = node.get("description") or node.get("rule") or ""
        return f"## {heading}\n\n{str(body).strip()}\n\n"

    out += section("policy_name", "Policy name")
    out += section("policy_declaration", "The POLICY declaration")
    cr = cat.get("consistency_rule")
    if cr:
        out += "## Consistency rule\n\n"
        out += (
            "When the filename is known and a `POLICY` name is declared, the "
            "declared name must match the file basename after normalization "
            "(hyphens and underscores are treated as equivalent). A mismatch "
            "is a compile error.\n\n"
        )
        if cr.get("rationale"):
            out += f"> {md_escape(cr['rationale'])}\n\n"
    out += section("string_only_compilation", "Compiling from a string")
    out += section("description_clause", "The DESCRIPTION clause")
    return out


def page_keywords(cat: dict) -> str:
    out = front("Reserved keywords")
    out += GENERATED_NOTE
    out += (
        "These keywords are reserved by the language. Implementations must "
        "reject them as user-defined identifier names. Matching is "
        "case-insensitive. Entity-type identifiers and strategy names are also "
        "reserved in their syntactic positions and are not duplicated here.\n\n"
    )
    kws = cat["keywords"]
    cols = 4
    rows = (len(kws) + cols - 1) // cols
    out += "| " + " | ".join([""] * cols) + " |\n"
    out += "|" + "---|" * cols + "\n"
    for r in range(rows):
        cells = []
        for c in range(cols):
            i = c * rows + r
            cells.append(f"`{kws[i]}`" if i < len(kws) else "")
        out += "| " + " | ".join(cells) + " |\n"
    return out


def page_example(e: dict) -> str:
    out = front(e["title"])
    out += (
        f"*Source: [`{e['stem']}.phisql`]({SRC_BASE}/examples/{e['stem']}.phisql)*\n\n"
    )
    out += "## PhiSQL\n\n```sql\n" + e["phisql"] + "```\n\n"
    if e["json"] is not None:
        out += "## Compiles to\n\n```json\n" + e["json"] + "```\n"
    return out


def page_examples_index(examples: list[dict]) -> str:
    out = front("Examples")
    out += GENERATED_NOTE
    out += (
        f"{len(examples)} worked examples, each a PhiSQL source paired with "
        "the redaction policy JSON it compiles to. Every example is parsed by "
        "the reference implementation's test suite on each build.\n\n"
    )
    out += "| Example | Description |\n|---|---|\n"
    for e in examples:
        out += f"| [`{e['stem']}`]({e['stem']}.md) | {md_escape(e['title'])} |\n"
    return out


# --------------------------------------------------------------------------
# Site assembly
# --------------------------------------------------------------------------

def build_pages() -> dict[str, str]:
    """Return a map of output path -> Markdown content for every page."""
    rules = parse_ebnf((GRAMMAR_DIR / "PhiSQL.ebnf").read_text(encoding="utf-8"))
    ebnf_text = (GRAMMAR_DIR / "PhiSQL.ebnf").read_text(encoding="utf-8")
    examples = load_examples()

    entity_cat = load_catalog("entity-types.yaml")
    strategy_cat = load_catalog("strategies.yaml")
    predicate_cat = load_catalog("predicates.yaml")
    source_cat = load_catalog("sources.yaml")
    findings_cat = load_catalog("findings.yaml")
    policy_cat = load_catalog("policy.yaml")
    keyword_cat = load_catalog("keywords.yaml")

    pages = {
        "reference/grammar.md": page_grammar(rules, ebnf_text),
        "reference/verbs.md": page_verbs(rules, examples),
        "reference/clauses.md": page_clauses(rules),
        "reference/type-system.md": page_type_system(rules),
        "reference/entity-types.md": page_entity_types(entity_cat),
        "reference/strategies.md": page_strategies(strategy_cat),
        "reference/predicates.md": page_predicates(predicate_cat),
        "reference/sources.md": page_sources(source_cat),
        "reference/findings.md": page_findings(findings_cat),
        "reference/policy-naming.md": page_policy_naming(policy_cat),
        "reference/keywords.md": page_keywords(keyword_cat),
        "examples/index.md": page_examples_index(examples),
    }
    for e in examples:
        pages[f"examples/{e['stem']}.md"] = page_example(e)

    pages["SUMMARY.md"] = build_nav(examples)
    return pages


def build_nav(examples: list[dict]) -> str:
    """A literate-nav SUMMARY.md defining the sidebar."""
    lines = [
        "* [Home](index.md)",
        "* Reference",
        "    * [Grammar](reference/grammar.md)",
        "    * [Verbs](reference/verbs.md)",
        "    * [Clauses](reference/clauses.md)",
        "    * [Type system](reference/type-system.md)",
        "    * [Entity types](reference/entity-types.md)",
        "    * [Strategies](reference/strategies.md)",
        "    * [Predicates](reference/predicates.md)",
        "    * [Sources](reference/sources.md)",
        "    * [Findings](reference/findings.md)",
        "    * [Policy naming](reference/policy-naming.md)",
        "    * [Keywords](reference/keywords.md)",
        "* Examples",
        "    * [Overview](examples/index.md)",
    ]
    for e in examples:
        lines.append(f"    * [{e['stem']}](examples/{e['stem']}.md)")
    return "\n".join(lines) + "\n"


def run_with_gen_files() -> None:
    import mkdocs_gen_files

    for path, content in build_pages().items():
        with mkdocs_gen_files.open(path, "w") as fh:
            fh.write(content)


def run_standalone(out_dir: Path) -> None:
    for path, content in build_pages().items():
        dest = out_dir / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    print(f"Wrote {len(build_pages())} pages to {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        help="Write pages to this directory instead of using mkdocs-gen-files.",
    )
    args = parser.parse_args()
    if args.out:
        run_standalone(args.out)
    else:
        run_with_gen_files()
    return 0


# When imported by mkdocs-gen-files, there is no __main__ guard hit and the
# module body runs the generation. When run as a script, argparse drives it.
if __name__ == "__main__":
    sys.exit(main())
else:
    # Executed as an mkdocs-gen-files script (no __main__).
    run_with_gen_files()
