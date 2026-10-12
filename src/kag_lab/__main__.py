import argparse
from pathlib import Path
from . import KnowledgeGraph, load_triples, render_path


def main():
    parser = argparse.ArgumentParser(description="Trace source-aware knowledge graph paths")
    parser.add_argument("start")
    parser.add_argument("end")
    parser.add_argument("--hops", type=int, default=3)
    parser.add_argument("--paths", type=int, default=5)
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parents[2] / "data" / "triples.jsonl")
    args = parser.parse_args()
    graph = KnowledgeGraph(load_triples(args.data))
    answers = graph.find_paths(args.start, args.end, max_hops=args.hops, max_paths=args.paths)
    if not answers:
        print("No supported relationship found in the toy graph.")
        return
    for idx, path in enumerate(answers, 1):
        print(f"Path {idx}:\n{render_path(path)}\n")


if __name__ == "__main__":
    main()
