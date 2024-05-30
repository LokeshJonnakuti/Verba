from wasabi import msg

from goldenverba.components.reader.simplereader import SimpleReader
from goldenverba.components.reader.githubreader import GithubReader
from goldenverba.components.reader.unstructuredpdf import UnstructuredPDF
from goldenverba.components.reader.pdfreader import PDFReader
from goldenverba.components.reader.interface import Reader
from goldenverba.components.reader.document import Document
from typing import Optional


class ReaderManager:
    def __init__(self):
        self.readers: dict[str, Reader] = {
            "SimpleReader": SimpleReader(),
            "PDFReader": PDFReader(),
            "GithubReader": GithubReader(),
            "UnstructuredPDF": UnstructuredPDF(),
        }
        self.selected_reader: Reader = self.readers["SimpleReader"]

    def load(
        self,
        bytes: Optional[list[str]] = None,
        contents: Optional[list[str]] = None,
        paths: Optional[list[str]] = None,
        fileNames: Optional[list[str]] = None,
        document_type: str = "Documentation",
    ) -> list[Document]:
        """Ingest data into Weaviate
        @parameter: bytes : list[str] - List of bytes
        @parameter: contents : list[str] - List of string content
        @parameter: paths : list[str] - List of paths to files
        @parameter: fileNames : list[str] - List of file names
        @parameter: document_type : str - Document type
        @returns list[Document] - Lists of documents
        """
        bytes = [] if bytes is None else bytes
        contents = [] if contents is None else contents
        paths = [] if paths is None else paths
        fileNames = [] if fileNames is None else fileNames
        return self.selected_reader.load(
            bytes, contents, paths, fileNames, document_type
        )

    def set_reader(self, reader: str) -> bool:
        if reader in self.readers:
            self.selected_reader = self.readers[reader]
            return True
        else:
            msg.warn(f"Reader {reader} not found")
            return False

    def get_readers(self) -> dict[str, Reader]:
        return self.readers
