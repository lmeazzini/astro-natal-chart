"""BM25 service for sparse keyword search."""
import re
from collections import Counter
from typing import Any

import numpy as np
from loguru import logger
from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]


class BM25Service:
    """
    Service for BM25 sparse keyword search.

    Memory Considerations:
        This implementation stores the entire tokenized corpus in memory. For large
        corpora (>100k documents), memory usage can become significant. Consider:

        1. For corpora >100k docs: Use a database-backed BM25 implementation or
           disk-based index (e.g., Whoosh, Elasticsearch).

        2. For corpora >1M docs: Consider using approximate methods like:
           - SPLADE (learned sparse representations)
           - BM25 with inverted index sharding
           - Hybrid approaches with vector-only retrieval

        3. For incremental updates: The current implementation rebuilds the index
           on each add/remove operation. For frequent updates, consider batching
           changes and rebuilding periodically, or using a streaming BM25 variant.

        Current implementation is optimized for corpora <50k documents with
        infrequent updates, which is typical for astrological knowledge bases.
    """

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        """
        Initialize BM25 service.

        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.corpus: list[list[str]] = []
        self.document_ids: list[str] = []
        self.bm25: BM25Okapi | None = None
        self.stopwords = self._get_stopwords()

    def _get_stopwords(self) -> set[str]:
        """Get common English, Portuguese and astrological stopwords."""
        # Common English stopwords
        english_stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "been", "by", "for",
            "from", "has", "have", "he", "in", "is", "it", "its", "of", "on",
            "that", "the", "to", "was", "will", "with", "this", "these", "those",
            "i", "you", "we", "they", "them", "their", "what", "which", "who",
            "when", "where", "why", "how", "all", "would", "there", "could",
        }

        # Common Portuguese stopwords
        portuguese_stopwords = {
            # Artigos
            "o", "a", "os", "as", "um", "uma", "uns", "umas",
            # Pronomes
            "eu", "tu", "ele", "ela", "nós", "vós", "eles", "elas",
            "me", "te", "se", "nos", "vos", "lhe", "lhes",
            "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas",
            "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas",
            "vosso", "vossa", "vossos", "vossas", "este", "esta", "estes", "estas",
            "esse", "essa", "esses", "essas", "aquele", "aquela", "aqueles", "aquelas",
            "isto", "isso", "aquilo", "mesmo", "mesma", "mesmos", "mesmas",
            "próprio", "própria", "próprios", "próprias", "todo", "toda", "todos", "todas",
            "outro", "outra", "outros", "outras", "muito", "muita", "muitos", "muitas",
            "pouco", "pouca", "poucos", "poucas", "algum", "alguma", "alguns", "algumas",
            "nenhum", "nenhuma", "nenhuns", "nenhumas", "qual", "quais", "quanto", "quanta",
            "quantos", "quantas", "que", "quem", "onde", "quando", "como",
            # Preposições
            "de", "em", "para", "por", "com", "sem", "sob", "sobre", "entre",
            "até", "desde", "durante", "mediante", "perante", "contra", "através",
            # Conjunções
            "e", "ou", "mas", "porém", "todavia", "contudo", "portanto", "logo",
            "pois", "porque", "embora", "também",
            # Verbos auxiliares e comuns
            "ser", "estar", "ter", "haver", "fazer", "ir", "vir", "dar", "poder",
            "dever", "querer", "saber", "foi", "é", "são", "era", "eram", "será",
            "serão", "seja", "sejam", "fosse", "fossem", "for", "forem", "sou",
            "está", "estão", "estava", "estavam", "estará", "estarão", "esteja",
            "estejam", "estivesse", "estivessem", "estiver", "estiverem", "estou",
            "tem", "têm", "tinha", "tinham", "terá", "terão", "tenha", "tenham",
            "tivesse", "tivessem", "tiver", "tiverem", "tenho", "há", "havia",
            "haverá", "haja", "hajam", "houvesse", "houvessem", "houver", "houverem",
            # Advérbios comuns
            "não", "sim", "mais", "menos", "bem", "mal",
            "apenas", "só", "somente", "sempre", "nunca", "agora",
            "então", "depois", "antes", "ontem", "hoje", "amanhã", "aqui", "aí",
            "ali", "lá", "cá", "dentro", "fora", "acima", "abaixo", "atrás",
            "adiante", "longe", "perto", "assim", "talvez",
            # Palavras comuns
            "coisa", "coisas", "vez", "vezes", "dia", "dias", "ano", "anos",
            "tempo", "parte", "lugar", "pessoa", "pessoas", "homem", "mulher",
            "momento", "forma", "jeito", "modo", "maneira", "caso", "vida",
        }

        # Common astrological stopwords (bilingual)
        astro_stopwords = {
            # English
            "degree", "degrees", "sign", "house", "planet", "aspect",
            # Portuguese
            "grau", "graus", "signo", "casa", "planeta", "aspecto",
            "astrologia", "astrológico", "astrológica", "natal", "mapa",
        }

        return english_stopwords | portuguese_stopwords | astro_stopwords

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text for BM25.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep astrological symbols
        text = re.sub(r"[^\w\s°♈♉♊♋♌♍♎♏♐♑♒♓]", " ", text)

        # Split into tokens
        tokens = text.split()

        # Remove stopwords and short tokens
        tokens = [
            token for token in tokens
            if token not in self.stopwords and len(token) > 2
        ]

        return tokens

    def build_index(
        self,
        documents: list[str],
        document_ids: list[str],
    ) -> None:
        """
        Build BM25 index from documents.

        Args:
            documents: List of document texts
            document_ids: List of document IDs
        """
        if len(documents) != len(document_ids):
            raise ValueError("Documents and IDs must have same length")

        # Tokenize all documents
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.document_ids = document_ids

        # Build BM25 index
        self.bm25 = BM25Okapi(
            self.corpus,
            k1=self.k1,
            b=self.b,
        )

        logger.info(f"Built BM25 index with {len(documents)} documents")

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search documents using BM25.

        Args:
            query: Search query
            limit: Maximum number of results
            min_score: Minimum BM25 score

        Returns:
            List of search results with scores
        """
        if not self.bm25 or not self.corpus:
            logger.warning("BM25 index not built, returning empty results")
            return []

        # Tokenize query
        query_tokens = self.tokenize(query)
        if not query_tokens:
            logger.warning("Empty query after tokenization")
            return []

        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Get top results
        ranked_indices = np.argsort(scores)[::-1][:limit]

        # Filter by minimum score and format results
        results = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score >= min_score:
                results.append({
                    "document_id": self.document_ids[idx],
                    "score": score,
                    "tokens": self.corpus[idx][:10],  # First 10 tokens for preview
                })

        logger.debug(f"BM25 search found {len(results)} results for query: {query}")
        return results

    def add_document(self, document: str, document_id: str) -> None:
        """
        Add a single document to existing index.

        Args:
            document: Document text
            document_id: Document ID
        """
        if not self.bm25:
            # Initialize with single document if index doesn't exist
            self.build_index([document], [document_id])
            return

        # Tokenize new document
        tokens = self.tokenize(document)

        # Add to corpus
        self.corpus.append(tokens)
        self.document_ids.append(document_id)

        # Rebuild BM25 (required as BM25Okapi doesn't support incremental updates)
        self.bm25 = BM25Okapi(
            self.corpus,
            k1=self.k1,
            b=self.b,
        )

        logger.debug(f"Added document {document_id} to BM25 index")

    def add_documents_batch(
        self,
        documents: list[str],
        document_ids: list[str],
    ) -> None:
        """
        Add multiple documents efficiently (rebuilds index once).

        Args:
            documents: List of document texts
            document_ids: List of document IDs
        """
        if len(documents) != len(document_ids):
            raise ValueError("Documents and IDs must have same length")

        if not documents:
            return

        if not self.bm25:
            # Initialize with all documents if index doesn't exist
            self.build_index(documents, document_ids)
            return

        # Tokenize all new documents
        for doc, doc_id in zip(documents, document_ids, strict=True):
            tokens = self.tokenize(doc)
            self.corpus.append(tokens)
            self.document_ids.append(doc_id)

        # Rebuild BM25 once after all additions
        self.bm25 = BM25Okapi(
            self.corpus,
            k1=self.k1,
            b=self.b,
        )

        logger.info(f"Added {len(documents)} documents to BM25 index in batch")

    def remove_document(self, document_id: str) -> bool:
        """
        Remove a document from the index.

        Args:
            document_id: Document ID to remove

        Returns:
            True if document was found and removed
        """
        if document_id not in self.document_ids:
            return False

        # Find index
        idx = self.document_ids.index(document_id)

        # Remove from corpus and IDs
        del self.corpus[idx]
        del self.document_ids[idx]

        # Rebuild BM25 if documents remain
        if self.corpus:
            self.bm25 = BM25Okapi(
                self.corpus,
                k1=self.k1,
                b=self.b,
            )
        else:
            self.bm25 = None

        logger.debug(f"Removed document {document_id} from BM25 index")
        return True

    def get_term_frequencies(self, text: str) -> dict[str, int]:
        """
        Get term frequencies for a text.

        Args:
            text: Input text

        Returns:
            Dictionary of term frequencies
        """
        tokens = self.tokenize(text)
        return dict(Counter(tokens))

    def calculate_score(self, query: str, document: str) -> float:
        """
        Calculate BM25 score for a query-document pair.

        Args:
            query: Search query
            document: Document text

        Returns:
            BM25 score
        """
        # Build temporary index with single document
        temp_bm25 = BM25Okapi(
            [self.tokenize(document)],
            k1=self.k1,
            b=self.b,
        )

        # Calculate score
        query_tokens = self.tokenize(query)
        scores = temp_bm25.get_scores(query_tokens)

        return float(scores[0]) if scores.size > 0 else 0.0

    def get_index_stats(self) -> dict[str, Any]:
        """
        Get statistics about the BM25 index.

        Returns:
            Dictionary with index statistics
        """
        if not self.corpus:
            return {
                "num_documents": 0,
                "avg_doc_length": 0,
                "total_terms": 0,
                "unique_terms": 0,
            }

        # Calculate statistics
        doc_lengths = [len(doc) for doc in self.corpus]
        all_terms = [term for doc in self.corpus for term in doc]
        unique_terms = set(all_terms)

        return {
            "num_documents": len(self.corpus),
            "avg_doc_length": np.mean(doc_lengths) if doc_lengths else 0,
            "total_terms": len(all_terms),
            "unique_terms": len(unique_terms),
            "k1": self.k1,
            "b": self.b,
        }


# Global instance for shared BM25 index
bm25_service = BM25Service()
