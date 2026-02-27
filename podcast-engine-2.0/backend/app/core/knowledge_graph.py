import logging
import os

import chromadb

logging.basicConfig(level=logging.INFO)


class KnowledgeGraph:
    def __init__(self, db_dir="data/chroma_db", collection_name="user_knowledge"):
        """
        Initializes the ChromaDB client to store and retrieve the user's knowledge graph.
        """
        os.makedirs(db_dir, exist_ok=True)
        # Using the persistent client to save graph locally
        self.client = chromadb.PersistentClient(path=db_dir)

        # Create or load the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Default similarity metric
        )
        logging.info(f"Initialized Knowledge Graph. DB Path: {db_dir}")

    def add_concepts(self, concepts, metadata=None):
        """
        Adds newly learned concepts to the graph.
        concepts: list of strings (e.g. summarized paragraphs or key definitions)
        metadata: optional list of dicts (e.g. source podcast, timestamp)
        """
        if not concepts:
            return

        # Generate unique IDs for each concept based on content hash or counter
        ids = [f"concept_{hash(c)}" for c in concepts]

        # Add to ChromaDB. It automatically handles basic embedding if an embedding function isn't specfied.
        self.collection.add(
            documents=concepts, metadatas=metadata if metadata else [{} for _ in concepts], ids=ids
        )
        logging.info(f"Added {len(concepts)} concepts to the Knowledge Graph.")

    def check_if_known(self, chunk, threshold=0.8, n_results=3):
        """
        Queries the vector DB to see if the transcript 'chunk' summarizes a concept already known.
        Returns a boolean and the supporting similar documents.
        """
        if self.collection.count() == 0:
            return False, []

        results = self.collection.query(query_texts=[chunk], n_results=n_results)

        # ChromaDB returns distances. For cosine space, smaller roughly means more similar
        # Depending on the embedding model, we check distance
        distances = results["distances"][0]
        documents = results["documents"][0]

        # Check if the closest match is below the distance threshold (meaning highly similar)
        # threshold needs tuning based on embedding model defaults
        if distances and min(distances) < threshold:
            logging.info(f"Concept likely known. Closest distance: {min(distances)}")
            return True, documents
        return False, []


if __name__ == "__main__":
    kg = KnowledgeGraph()
    print(f"Total concepts known: {kg.collection.count()}")
