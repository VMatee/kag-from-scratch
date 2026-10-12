# Architecture note — Knowledge-graph evidence search

```text
source triples -> directed adjacency -> bounded BFS -> source-annotated paths
```

## Fidelity and assumptions

Triple extraction and LLM generation are outside this educational scope.

Read the source implementation and the tests together. New features should
add controlled experiments or unit tests before using benchmark claims.
