from app.utils import Citation, Output


def test_output_serialization():
    """Output and Citation serialize to dict/JSON for API."""
    out = Output(
        query="What if I steal?",
        response="Theft is punishable by hanging.",
        citations=[
            Citation(source="Law 1", text="Theft is punishable by hanging."),
        ],
    )
    d = out.model_dump()
    assert d["query"] == "What if I steal?"
    assert d["response"] == "Theft is punishable by hanging."
    assert len(d["citations"]) == 1
    assert d["citations"][0]["source"] == "Law 1"

