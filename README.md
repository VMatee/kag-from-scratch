# KAG from Scratch — Knowledge Graph Evidence Traversal

[![Tests](https://github.com/VMatee/kag-from-scratch/actions/workflows/tests.yml/badge.svg)](https://github.com/VMatee/kag-from-scratch/actions/workflows/tests.yml)

This repository implements **source-aware graph traversal** over explicit subject–relation–object triples. A curated JSONL graph is indexed into adjacency lists and queried with bounded breadth-first search. Every returned path can be checked against its original edge and source identifiers. It uses only the Python standard
library and does **not** train an LLM.

Here **KAG** means *knowledge-graph-augmented generation* in a general educational
sense, **not** a reimplementation of OpenSPG's KAG framework.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m kag_lab "GitHub" "code review" --hops 3
python -m kag_lab "Git" "pull requests" --hops 2
python -m kag_lab "GitHub" "code review" --hops 3 --stats
python -m kag_lab.evaluate
```

## Mathematical model

The knowledge graph is a directed, labeled multigraph $G=(V,E)$. A returned path must contain a sequence of real source-labeled edges, preserve endpoint continuity, and respect a maximum hop count:

$
P=(e_1,\ldots,e_h),\qquad e_i\in E,\qquad 1\le h\le H.
$

The mathematical walkthrough explains BFS queue states, path validation, an actual three-hop query, and why enumerating multiple paths can become expensive even when a graph is small.

**[Read the graph-theory and verification walkthrough →](docs/mathematics.md)**

## Explicit graph algorithms and evidence verification

The graph search now exposes bounded BFS expansion counts and queue size,
plus an **independent path verifier** that checks every relationship and
source ID against the stored triples. An illustrative evaluation exercises
both supported and unsupported relationship questions.

See [the graph traversal and verification guide](docs/implementation.md).

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

## Reproducible notebook

Open [the step-by-step notebook](notebooks/01_walkthrough.ipynb) in Jupyter after installing this repository with `python -m pip install -e ".[dev]"`.

## Architecture walk-through

See [the implementation map](docs/architecture.md) for a component-by-component overview.

## Related educational reading

Sebastian Raschka maintains a useful [independent educational reference](https://github.com/rasbt/llm-architecture-gallery). This repository uses its own small code examples and does not reproduce his book content.
