import pytest
from pathlib import Path
from kag_lab import KnowledgeGraph, Triple, load_triples, render_path


def graph():
    return KnowledgeGraph([
        Triple("A", "connects to", "B", "src:1"),
        Triple("B", "connects to", "C", "src:2"),
        Triple("C", "loops to", "A", "src:3"),
        Triple("A", "connects to", "C", "src:4"),
    ])


def test_direct_and_multi_hop():
    assert len(graph().find_paths("a", "C", max_hops=1)) == 1
    paths = graph().find_paths("A", "C", max_hops=2)
    assert [len(p) for p in paths] == [1, 2]
    assert "[SOURCE:src:4]" in render_path(paths[0])


def test_no_invented_edges_or_cycles():
    assert graph().find_paths("C", "B", max_hops=3) == [[
        Triple("C", "loops to", "A", "src:3"), Triple("A", "connects to", "B", "src:1")
    ]]
    assert graph().find_paths("C", "unknown") == []
    assert graph().find_paths("a", "a") == []


def test_budget_validation():
    with pytest.raises(ValueError):
        graph().find_paths("A", "C", max_hops=0)
    with pytest.raises(ValueError):
        graph().find_paths("A", "C", max_paths=0)


def test_parsing_invalid_source(tmp_path: Path):
    source = tmp_path / "facts.jsonl"
    source.write_text('{"subject": "A", "relation":"r", "object":"B"}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_triples(source)


def test_bundled_graph_has_provenance():
    triples = load_triples(Path(__file__).resolve().parents[1] / "data" / "triples.jsonl")
    paths = KnowledgeGraph(triples).find_paths("GitHub", "code review", max_hops=3)
    assert paths and len(paths[0]) == 3
    assert "[SOURCE:lesson:github-01]" in render_path(paths[0])
