"""Small, deterministic knowledge-graph search with independently verified paths."""
from collections import defaultdict, deque
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Triple:
    subject: str
    relation: str
    object: str
    source: str


@dataclass(frozen=True)
class SearchResult:
    paths: list[list[Triple]]
    expanded_states: int
    examined_edges: int
    maximum_queue: int


def normalize(entity: str) -> str:
    return " ".join(entity.lower().strip().split())


def load_triples(path: str | Path) -> list[Triple]:
    triples = []
    for number, row in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not row.strip():
            continue
        try:
            raw = json.loads(row)
            values = [raw[key] for key in ("subject", "relation", "object", "source")]
            if not all(isinstance(value, str) and value.strip() for value in values):
                raise ValueError("Fields must be nonempty strings")
            triples.append(Triple(*(x.strip() for x in values)))
        except (KeyError, ValueError, TypeError) as error:
            raise ValueError(f"Invalid triple on line {number}") from error
    return triples


class KnowledgeGraph:
    def __init__(self, triples: Sequence[Triple]):
        self.adjacency: dict[str, list[Triple]] = defaultdict(list)
        self._edge_set: set[Triple] = set()
        for triple in triples:
            if not all((triple.subject.strip(), triple.relation.strip(), triple.object.strip(), triple.source.strip())):
                raise ValueError("Triple fields must be nonempty")
            self.adjacency[normalize(triple.subject)].append(triple)
            self._edge_set.add(triple)
        for outgoing in self.adjacency.values():
            outgoing.sort(key=lambda t: (normalize(t.object), t.relation, t.source))

    def search(self, start: str, end: str, max_hops: int = 3, max_paths: int = 5) -> SearchResult:
        """Bounded breadth-first traversal of real directed edges.

        Each queue state includes a visited-entity set, so cycles never become
        fabricated explanations. Results are shortest-hop-first, then stable
        lexical edge order, limited by max_paths.
        """
        if max_hops < 1 or max_paths < 1:
            raise ValueError("hop and path budgets must be positive")
        if not start.strip() or not end.strip():
            raise ValueError("entities cannot be empty")
        source, destination = normalize(start), normalize(end)
        if source == destination:
            return SearchResult([], 0, 0, 0)
        work = deque([(source, [], {source})])
        paths: list[list[Triple]] = []
        expanded, examined, queue_peak = 0, 0, 1
        while work and len(paths) < max_paths:
            current, path, seen = work.popleft()
            expanded += 1
            if len(path) >= max_hops:
                continue
            for edge in self.adjacency.get(current, []):
                examined += 1
                nxt = normalize(edge.object)
                if nxt in seen:
                    continue
                candidate = path + [edge]
                if nxt == destination:
                    paths.append(candidate)
                    if len(paths) == max_paths:
                        break
                else:
                    work.append((nxt, candidate, seen | {nxt}))
                    queue_peak = max(queue_peak, len(work))
        return SearchResult(paths, expanded, examined, queue_peak)

    def find_paths(self, start: str, end: str, max_hops: int = 3, max_paths: int = 5) -> list[list[Triple]]:
        """Backward-compatible public API returning paths only."""
        return self.search(start, end, max_hops, max_paths).paths

    def verify_path(self, start: str, end: str, path: Sequence[Triple], max_hops: int = 3) -> bool:
        """Check every edge and its provenance independently of path search."""
        if max_hops < 1 or not path or len(path) > max_hops or not start.strip() or not end.strip():
            return False
        current = normalize(start)
        visited = {current}
        for triple in path:
            if triple not in self._edge_set or normalize(triple.subject) != current:
                return False
            nxt = normalize(triple.object)
            if nxt in visited:
                return False
            visited.add(nxt)
            current = nxt
        return current == normalize(end)


def render_path(path: Sequence[Triple]) -> str:
    if not path:
        return "No supported relationship found."
    return "\n".join(
        f"{idx}. {edge.subject} --{edge.relation}--> {edge.object} [SOURCE:{edge.source}]"
        for idx, edge in enumerate(path, 1)
    )
