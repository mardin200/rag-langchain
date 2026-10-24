import pytest

from app.document_loader import load_document


def test_load_txt_document(tmp_path):
    # Arrange: create a temporary text file
    file_path = tmp_path / "sample.txt"
    expected_text = "This is a test document."
    file_path.write_text(expected_text, encoding="utf-8")

    # Act: load the document
    documents = load_document(file_path)

    # Assert: verify the result
    assert len(documents) == 1
    assert documents[0].page_content == expected_text


def test_reject_unsupported_file_type(tmp_path):
    # Arrange: create a file with an unsupported extension
    file_path = tmp_path / "sample.csv"
    file_path.write_text("id,name", encoding="utf-8")

    # Act and Assert: verify that loading fails
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document(file_path)
        
