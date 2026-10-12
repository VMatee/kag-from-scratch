"""Inspect source-verified knowledge-graph relationships from local triples."""
import argparse
from pathlib import Path
from . import KnowledgeGraph, load_triples, render_path


def main():
    parser = argparse.ArgumentParser(description="Trace source-aware knowledge graph paths")
    parser.add_argument("start")
    parser.add_argument("end")
    parser.add_argument("--hops", type=int, default=3)
    parser.add_argument("--paths", type=int, default=5)
    parser.add_argument("--stats", action="store_true", help="show BFS expansion and evidence validation")
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[2] / "data" / "triples.jsonl")
    args = parser.parse_args()
    graph = KnowledgeGraph(load_triples(args.data))
    result = graph.search(args.start, args.end, max_hops=args.hops, max_paths=args.paths)
    if not result.paths:
        print("No supported relationship found in the toy graph.")
    for idx, path in enumerate(result.paths, 1):
        print(f"Path {idx}:\n{render_path(path)}")
        if args.stats:
            print(f"Evidence verified: {graph.verify_path(args.start, args.end, path, args.hops)}")
        print()
    if args.stats:
        print(f"Expanded BFS states: {result.expanded_states}")
        print(f"Edges inspected: {result.examined_edges}")
        print(f"Peak queue size: {result.maximum_queue}")


if __name__ == "__main__":
    main()
