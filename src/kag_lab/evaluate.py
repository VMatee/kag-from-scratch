"""Reproducible small-graph sanity checks, not an external benchmark."""
from pathlib import Path

from . import KnowledgeGraph, load_triples


QUESTIONS = [
    ("GitHub", "code review", 3, True),
    ("Git", "repositories", 2, True),
    ("Linux", "tests", 3, True),
    ("Git", "nonexistent concept", 3, False),
]


def run() -> float:
    graph_path = Path(__file__).resolve().parents[2] / "data" / "triples.jsonl"
    graph = KnowledgeGraph(load_triples(graph_path))
    correct = 0
    for start, end, hops, should_exist in QUESTIONS:
        paths = graph.find_paths(start, end, max_hops=hops)
        supported = bool(paths) and all(graph.verify_path(start, end, p, hops) for p in paths)
        if (supported if should_exist else not paths):
            correct += 1
    accuracy = correct / len(QUESTIONS)
    print(f"Sanity checks on {len(QUESTIONS)} handcrafted graph queries: {correct}/{len(QUESTIONS)} ({accuracy:.0%})")
    return accuracy


if __name__ == "__main__":
    run()
