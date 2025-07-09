import os

try:
    import faiss
except ImportError:
    faiss = None


class VectorMemory:
    """
    Wrapper around a FAISS vector store for semantic memory.
    """
    def __init__(self, dimension: int, index_path: str = None):
        if not faiss:
            raise RuntimeError("faiss is required for VectorMemory but not installed")
        self.index_path = index_path or os.getenv("VECTOR_INDEX_PATH", "faiss.index")
        self.dimension = dimension
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(dimension)

    def add(self, vectors, metadata=None):
        """
        Add embeddings (nxD numpy array) to the index.
        Metadata handling can be implemented alongside external store.
        """
        self.index.add(vectors)

    def search(self, queries, top_k: int = 5):
        """
        Search the index for the nearest neighbors of queries (nxD numpy array).
        Returns distances and indices.
        """
        return self.index.search(queries, top_k)

    def save(self):
        """
        Persist index to disk.
        """
        faiss.write_index(self.index, self.index_path)
