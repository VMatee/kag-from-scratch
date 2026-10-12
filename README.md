# KAG from Scratch — Knowledge Graph Evidence Traversal

[![Tests](https://github.com/VMatee/kag-from-scratch/actions/workflows/tests.yml/badge.svg)](https://github.com/VMatee/kag-from-scratch/actions/workflows/tests.yml)

Learn **knowledge-graph-augmented answer construction** from explicit subject–
relation–object triples. Starting with a curated JSONL knowledge graph, this
implementation performs bounded multi-hop search and returns inspectable
relationship paths with source provenance. It uses only the Python standard
library and does **not** train an LLM.

Here **KAG** means *knowledge-graph-augmented generation* in a general educational
sense, **not** a reimplementation of OpenSPG's KAG framework.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m kag_lab "GitHub" "code review" --hops 3
python -m kag_lab "Git" "pull requests" --hops 2
```

## Core idea

```text
source documents --> curated triples --> adjacency index
                                           |
                              start entity + end entity
                                           |
                             bounded BFS multi-hop paths
                                           |
                                  path + evidence IDs
```

`src/kag_lab/graph.py` implements a source-aware directed multigraph and BFS.
`src/kag_lab/__main__.py` displays evidence chains. See `data/triples.jsonl`.

## Guarantees & limitations

- Rejects malformed triples and non-positive hop budgets.
- Never invents graph edges or produces unsupported paths.
- Cycles are avoided on each path, and results are deterministic.
- No information extraction, entity linking, embeddings, semantic matching,
  LLM generation, or graph database. Those are later engineering layers.
- The triples are **manually curated illustrations**. Evidence sources are
  synthetic example identifiers, not external research citations.

**Reading:** Pan et al. (2023), *Unifying Large Language Models and Knowledge Graphs*;
Edge et al. (2024), *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*.

## Interactive notebook

Open [the step-by-step notebook](notebooks/01_walkthrough.ipynb) in Jupyter after installing this repository with `python -m pip install -e ".[dev]"`.

## Architecture walk-through

See [the implementation map](docs/architecture.md) for a component-by-component overview.

## Related educational reading

Sebastian Raschka maintains a useful [independent educational reference](https://github.com/rasbt/llm-architecture-gallery). This repository uses its own small code examples and does not reproduce his book content.
