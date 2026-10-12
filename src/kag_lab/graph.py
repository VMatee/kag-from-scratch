"""Source-aware, bounded knowledge-graph traversal without external libraries."""
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
        for triple in triples:
            if not all((triple.subject.strip(), triple.relation.strip(), triple.object.strip(), triple.source.strip())):
                raise ValueError("Triple fields must be nonempty")
            self.adjacency[normalize(triple.subject)].append(triple)
        for outgoing in self.adjacency.values():
            outgoing.sort(key=lambda t: (normalize(t.object), t.relation, t.source))

    def find_paths(self, start: str, end: str, max_hops: int = 3, max_paths: int = 5) -> list[list[Triple]]:
        if max_hops < 1 or max_paths < 1:
            raise ValueError("hop and path budgets must be positive")
        if not start.strip() or not end.strip():
            raise ValueError("entities cannot be empty")
        a, b = normalize(start), normalize(end)
        if a == b:
            return []  # request a non-trivial explanation, not a zero-hop identity
        work = deque([(a, [], {a})])
        paths = []
        while work and len(paths) < max_paths:
            current, path, seen = work.popleft()
            if len(path) >= max_hops:
                continue
            for edge in self.adjacency.get(current, []):
                nxt = normalize(edge.object)
                if nxt in seen:
                    continue
                new_path = path + [edge]
                if nxt == b:
                    paths.append(new_path)
                    if len(paths) == max_paths:
                        break
                else:
                    work.append((nxt, new_path, seen | {nxt}))
        return paths


def render_path(path: Sequence[Triple]) -> str:
    if not path:
        return "No supported relationship found."
    return "\n".join(
        f"{idx}. {edge.subject} --{edge.relation}--> {edge.object} [SOURCE:{edge.source}]"
        for idx, edge in enumerate(path, 1)
    )
