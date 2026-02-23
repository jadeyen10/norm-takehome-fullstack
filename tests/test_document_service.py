from app.services.document_service import DocumentService

from pathlib import Path


def test_extracts_hierarchy_from_laws_pdf():
    service = DocumentService(Path(__file__).parent.parent / "docs" / "laws.pdf")

    docs = service.create_documents()

    thievery_parent = next(
        d for d in docs if d.metadata["section_id"] == "6"
    )

    assert thievery_parent.metadata["title"] == "Thievery"
    assert "thievery" in thievery_parent.text.lower()

    sub_61 = next(
        d for d in docs if d.metadata["section_id"] == "6.1"
    )

    assert sub_61.metadata["parent_id"] == "6"
    assert sub_61.metadata["level"] == 2
    assert "losing a finger" in sub_61.text.lower()

    sub_423 = next(
        d for d in docs if d.metadata["section_id"] == "4.2.3"
    )

    assert sub_423.metadata["parent_id"] == "4.2"
    assert sub_423.metadata["level"] == 3
    assert "trial of seven" in sub_423.text.lower()

    assert len(sub_61.metadata["citations"]) > 0
    print(docs[:5])
