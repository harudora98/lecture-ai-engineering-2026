"""expand_neighbors の単体テスト（APIは呼ばない）。"""

from app.retrieval import expand_neighbors


def _page(doc_id: str, n: int, lecture: int = 1) -> dict:
    return {
        "page_id": f"{doc_id}-p{n:03d}",
        "document_id": doc_id,
        "lecture": lecture,
        "document_title": f"資料{doc_id}",
        "section": "章",
        "title": f"タイトル{n}",
        "page": n,
        "content": f"本文{n}",
    }


def _hit(page: dict, distance: float = 0.1) -> dict:
    return {**page, "distance": distance}


PAGES = (
    [_page("doc-a", n) for n in (1, 2, 3, 4, 5)]
    + [_page("doc-b", n, lecture=2) for n in (1, 2, 3)]
)


def test_adds_previous_and_next_pages():
    hit = _hit(PAGES[2])  # doc-a p3
    results = expand_neighbors([hit], window=1, pages=PAGES)
    assert [r["page_id"] for r in results] == [
        "doc-a-p003", "doc-a-p002", "doc-a-p004",
    ]
    assert results[0]["retrieved_by"] == "search"
    assert results[0]["distance"] == 0.1
    assert results[1]["retrieved_by"] == "neighbor"
    assert results[1]["neighbor_of"] == "doc-a-p003"
    assert results[1]["distance"] is None
    assert results[2]["retrieved_by"] == "neighbor"
    assert results[2]["neighbor_of"] == "doc-a-p003"


def test_does_not_cross_document_boundary():
    hit = _hit(PAGES[4])  # doc-a p5（末尾）
    results = expand_neighbors([hit], window=1, pages=PAGES)
    assert [r["page_id"] for r in results] == ["doc-a-p005", "doc-a-p004"]
    assert all(r["document_id"] == "doc-a" for r in results)


def test_deduplicates_by_page_id():
    hits = [_hit(PAGES[1], 0.05), _hit(PAGES[2], 0.1)]  # p2, p3
    results = expand_neighbors(hits, window=1, pages=PAGES)
    ids = [r["page_id"] for r in results]
    assert ids == ["doc-a-p002", "doc-a-p001", "doc-a-p003", "doc-a-p004"]
    assert len(ids) == len(set(ids))


def test_first_and_last_page():
    first = expand_neighbors([_hit(PAGES[0])], window=1, pages=PAGES)
    assert [r["page_id"] for r in first] == ["doc-a-p001", "doc-a-p002"]
    last_b = expand_neighbors([_hit(PAGES[7])], window=2, pages=PAGES)  # doc-b p3
    assert [r["page_id"] for r in last_b] == [
        "doc-b-p003", "doc-b-p002", "doc-b-p001",
    ]


def test_window_zero_returns_hits_only():
    hit = _hit(PAGES[2])
    results = expand_neighbors([hit], window=0, pages=PAGES)
    assert len(results) == 1
    assert results[0]["page_id"] == "doc-a-p003"
    assert results[0]["retrieved_by"] == "search"
    assert "neighbor_of" not in results[0]
