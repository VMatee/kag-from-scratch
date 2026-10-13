# Knowledge-graph reasoning: graph theory and evidence verification

*A mathematical explanation of bounded multi-hop traversal, deterministic search and source-aware path checking.*

A knowledge graph represents relationships explicitly. Instead of asking a language model to invent a connection between two concepts, a graph-based system looks for a sequence of supported relationships linking them. This repository implements that search in pure Python and records the source label attached to each relationship.

The word *reasoning* here refers to following and checking graph paths. No language model, entity-extraction model or graph database is used.

## 1. Model the information as a directed, labeled multigraph

Let $G=(V,E)$ be a directed graph. Each edge carries not only a destination but also a relation and a source label:

```math
e=(u,r,v,s),\qquad u,v\in V.
```

The symbols represent a subject $u$, a relation $r$, an object $v$, and a source identifier $s$. For example:

```math
(\mathrm{GitHub},\mathrm{hosts},\mathrm{repositories},\mathrm{lesson{:}github\text{-}01})
```

records that the source label **lesson:github-01** supports the relationship **GitHub hosts repositories** *within the curated sample graph*. A source label in this dataset is an illustrative identifier; it is not an independent citation proving the real-world assertion.

Multiple relations and sources may connect the same two entities. That is why the representation is naturally a **multigraph**, rather than a simple mapping from each entity to one neighbor.

Before indexing, the [graph module](../src/kag_lab/graph.py) normalizes each entity by lowercasing it, trimming surrounding whitespace and collapsing repeated spaces. Thus **GitHub** and **github** point to the same search key. Relation strings and source IDs remain part of the stored triples.

## 2. Construct an adjacency index

For every subject entity $u$, the implementation builds a list of its outgoing edges:

```math
\mathrm{Adj}(u)
=\{e\in E:\mathrm{subject}(e)=u\}.
```

This is an adjacency-list representation. It avoids searching the entire graph every time the traversal reaches a vertex: if the current entity is **repositories**, only the edges leaving **repositories** need to be examined.

The outgoing edges are sorted by normalized destination, relation and source. This deterministic ordering makes repeated searches produce the same ordered paths when the input graph is unchanged.

## 3. Define a valid multi-hop explanation

Suppose a query asks how a start entity $v_0$ is connected to a destination $v_h$. A candidate explanation is a sequence of edges

```math
P=(e_1,e_2,\ldots,e_h).
```

For this to be a valid directed path, its edges must join continuously:

```math
\mathrm{subject}(e_1)=v_0,
```

```math
\mathrm{object}(e_i)
=\mathrm{subject}(e_{i+1})
\quad\text{for }i=1,\ldots,h-1,
```

```math
\mathrm{object}(e_h)=v_{\mathrm{target}}.
```

Entity comparisons in the implementation use their normalized versions. An additional constraint prevents a path from revisiting a previously visited entity. The query also sets a maximum hop budget $H$, so only $1\le h\le H$ is permitted.

### Worked example: a three-hop connection

The bundled [triples.jsonl](../data/triples.jsonl) contains these edges:

1. **GitHub** —hosts→ **repositories**, source **lesson:github-01**.
2. **repositories** —contain→ **pull requests**, source **lesson:github-02**.
3. **pull requests** —request→ **code review**, source **lesson:github-03**.

The resulting path is

```math
\mathrm{GitHub}
\xrightarrow{\mathrm{hosts}}
\mathrm{repositories}
\xrightarrow{\mathrm{contain}}
\mathrm{pull\ requests}
\xrightarrow{\mathrm{request}}
\mathrm{code\ review}.
```

Its length is three. Therefore, searching with a hop budget of 3 can return this explanation, whereas a budget of 2 cannot return this particular three-edge chain.

Each edge also retains its source label. This is the difference between returning only a list of related words and returning an explanation that can be checked against the graph's evidence records.

## 4. Why the code uses breadth-first search

To discover short relationship chains before long ones, the [search routine](../src/kag_lab/graph.py) uses **breadth-first search (BFS)**. A queue entry contains three pieces of information:

```math
\mathrm{state}=(v,P,S),
```

where $v$ is the current entity, $P$ is the path accumulated so far, and $S$ is the set of entities visited *on that path*.

At each iteration, the algorithm:

1. Removes the first queue entry.
2. Stops extending it when its path already reaches the hop limit.
3. Examines every outgoing edge from the current entity.
4. Skips an edge when its destination already appears in $S$.
5. Records a complete path when the destination is the requested target; otherwise, adds the extended state to the queue.

A first-in, first-out queue explores shorter paths before deeper ones. The implementation additionally stops after collecting the specified maximum number of paths.

### A subtle complexity point

Standard single-visit BFS has a familiar $O(|V|+|E|)$ bound for reachability. **This implementation searches for multiple simple paths**, however, and stores a different visited set for each partial path. In the worst case, with branching factor $b$ and depth limit $H$, the number of explored path prefixes can grow on the order of

```math
1+b+b^2+\cdots+b^{H}
=O(b^H)\quad\text{for }b>1.
```

The hop and path budgets are therefore meaningful resource controls. The command's **--stats** mode reports the observed queue peak, expanded states and examined edges; no unmeasured runtime or scalability benchmark is claimed.

## 5. Verify a returned explanation independently

Generating a path is not enough. A graph search bug, or a modified result object, could return a relationship that never existed. The [verify_path](../src/kag_lab/graph.py) function checks a candidate path independently from the search:

```math
\mathrm{valid}(P)
=
\mathbf{1}\!\left[
\begin{array}{l}
1\le |P|\le H,\\
e_i\in E\ \text{for every }i,\\
\text{all adjacent endpoints are continuous},\\
\text{no entity is revisited},\\
\text{the final endpoint equals the requested target}
\end{array}
\right].
```

Membership checks use the **entire edge tuple**, including the relation and the source string. Replacing **lesson:github-03** with a fictitious source makes that edge fail validation, even if its subject and object are unchanged.

This is a useful form of provenance checking, but it has a clear boundary. The verifier establishes *consistency with the ingested graph*. If the original graph contains incorrect facts or unreliable sources, a valid path can still describe incorrect real-world information. Provenance verification does not replace external fact-checking.

## 6. What can be measured here

The [evaluation script](../src/kag_lab/evaluate.py) runs a short handcrafted set of positive and negative relationship queries. A simple agreement measure is

```math
\mathrm{accuracy}
=\frac{\text{number of queries matching the expected path-existence label}}
{\text{number of evaluation queries}}.
```

An expected positive example is correct only when at least one path is found and its returned edges pass verification. An expected negative example is correct when no path is returned. This checks the tiny curated graph; it is not a benchmark of automatic knowledge extraction, factual reasoning or LLM answer quality.

### Run the implementation

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m kag_lab "GitHub" "code review" --hops 3 --stats
python -m kag_lab.evaluate
~~~

**Source crosswalk:** [graph construction, BFS and verifier](../src/kag_lab/graph.py) · [command-line interface](../src/kag_lab/__main__.py) · [curated source-labeled triples](../data/triples.jsonl) · [verification tests](../tests/test_path_verification.py).

**Interpretation.** The project is an inspectable, source-aware graph traversal engine. Its guarantees apply to paths through the given curated triples and do not extend to semantic search, knowledge extraction or language generation.
