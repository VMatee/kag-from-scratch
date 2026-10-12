"""Validate that graph paths are real, ordered, sourced and bounded."""
from kag_lab import KnowledgeGraph, Triple
from kag_lab.evaluate import run


def make_graph():
    return KnowledgeGraph([
        Triple("A", "connected", "B", "s:1"),
        Triple("B", "connected", "C", "s:2"),
        Triple("A", "shortcut", "C", "s:3"),
        Triple("C", "loop", "A", "s:4"),
    ])


def test_bfs_order_and_search_statistics_preserve_existing_api():
    graph = make_graph()
    old = graph.find_paths("A", "C", max_hops=3)
    result = graph.search("A", "C", max_hops=3)
    assert result.paths == old
    assert [len(path) for path in old] == [1, 2]
    assert result.expanded_states >= 1
    assert result.examined_edges >= 3
    assert result.maximum_queue >= 1
    assert all(graph.verify_path("A", "C", path) for path in old)


def test_forged_edges_or_sources_are_rejected():
    graph = make_graph()
    legitimate = graph.find_paths("A", "C", max_hops=1)[0]
    forged_source = [Triple("A", "shortcut", "C", "unverified-source")]
    forged_relation = [Triple("A", "invented", "C", "s:3")]
    assert graph.verify_path("A", "C", legitimate)
    assert not graph.verify_path("A", "C", forged_source)
    assert not graph.verify_path("A", "C", forged_relation)
    assert not graph.verify_path("A", "B", legitimate)
    assert not graph.verify_path("A", "C", legitimate, max_hops=0)


def test_path_budget_and_cycles():
    graph = make_graph()
    assert len(graph.find_paths("A", "C", max_paths=1)) == 1
    assert graph.find_paths("A", "A") == []
    assert graph.find_paths("C", "C") == []
    assert graph.verify_path("C", "B", [
        Triple("C", "loop", "A", "s:4"),
        Triple("A", "connected", "B", "s:1")
    ])
    assert not graph.verify_path("A", "A", [
        Triple("A", "connected", "B", "s:1"),
        Triple("B", "connected", "C", "s:2"),
        Triple("C", "loop", "A", "s:4")
    ])


def test_bundled_query_sanity_checks():
    assert run() == 1.0
