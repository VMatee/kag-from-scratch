# Evidence-constrained graph traversal from scratch

This project builds a deterministic directed knowledge graph from subject, relation, object and source tuples. Search logic lives in src/kag_lab/graph.py and depends only on the Python standard library.

## Algorithm

1. Normalize entity names and construct adjacency lists keyed by subject.
2. Sort every adjacency list deterministically by destination, relation and source.
3. Start bounded breadth-first search at the source with an empty path and visited-entity set.
4. Pop the next queue state, enumerate only its outgoing edges and skip nodes already on that path.
5. If the destination is reached, emit its complete evidence chain. Otherwise append a new queue state.
6. Stop when max_hops is exceeded, the queue is exhausted, or max_paths is reached.

This returns short paths before longer ones and prohibits traversed cycles. The implementation reports queue usage, expanded states and examined edges without changing the original find_paths interface.

## Independent path certificate

KnowledgeGraph.verify_path checks each step against the ingested full triple including source ID; it also validates continuity, hop budget and path cycles. A fabricated or changed source ID fails verification.

These checks prove a returned path is supported by the curated input graph. They do not prove that the curated facts are independently true or that a model performed language generation.

## Try it

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m kag_lab "GitHub" "code review" --hops 3 --stats
python -m kag_lab.evaluate
~~~

Example data is handcrafted and small; reported sanity-check accuracy is not a research benchmark.
