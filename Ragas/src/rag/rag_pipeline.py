from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os

from src.rag.prompts import ACTIVE_PROMPT


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using Gemini."""

    def __init__(
        self,
        model: str = "gemini-3.1-flash-lite",
        temperature: float = 0.7,
        eval_mode: bool = False
    ):
        self.model = model
        self.eval_mode = eval_mode
        # Use temperature 0.0 for evaluation, 0.7 for production
        self.temperature = 0.0 if eval_mode else temperature

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )

        self.vector_store = None
        self.retriever = None

    def load_documents(self, documents: list[str]) -> None:
        """Chunk and embed documents into the vector store."""

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = []

        for doc in documents:
            chunks.extend(
                splitter.split_text(doc)
            )

        self.vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            collection_name=f"rag_collection_{id(self)}",
        )

        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 3}
        )

    def query(self, user_query: str) -> dict:
        """Run retrieval + generation for a single query."""

        if self.retriever is None:
            raise RuntimeError(
                "Retriever is not initialized. Load documents first."
            )

        retrieved_docs = self.retriever.invoke(
            user_query
        )

        retrieved_context = [
            doc.page_content
            for doc in retrieved_docs
        ]

        prompt = ChatPromptTemplate.from_template(
            ACTIVE_PROMPT
        )

        chain = (
            {
                "context": lambda _: "\n".join(retrieved_context),
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
        )

        response = chain.invoke(
            user_query
        )

        if hasattr(response, "content"):

            content = response.content

            if isinstance(content, str):
                answer_text = content

            elif isinstance(content, list):

                text_parts = []

                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    else:
                        text_parts.append(str(part))

                answer_text = "\n".join(text_parts)

            else:
                answer_text = str(content)

        else:
            answer_text = str(response)

        return {
            "query": user_query,
            "answer": answer_text,
            "retrieved_context": retrieved_context,
        }


_pipeline: RAGPipeline | None = None


def get_pipeline(
    model: str = "gemini-3.1-flash-lite",
    temperature: float = 0.7,
    eval_mode: bool = False
) -> RAGPipeline:

    global _pipeline

    if (
        _pipeline is None
        or _pipeline.retriever is None
        or _pipeline.eval_mode != eval_mode
    ):

        _pipeline = RAGPipeline(
            model=model,
            temperature=temperature,
            eval_mode=eval_mode
        )

        _pipeline.load_documents(
            _load_knowledge_base()
        )

    return _pipeline


def _load_knowledge_base() -> list[str]:
    """Load your company's knowledge base."""

    return [
        "Refund Policy: All customers are eligible for a 30-day full refund on any purchase. Returns must be initiated within 30 days of the original purchase date.",

        "Shipping: Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. Overnight options are available in most regions.",

        "Payment Methods: We accept Visa, MasterCard, American Express, PayPal, Apple Pay, and Google Pay.",

        "Order Tracking: Orders can be tracked in Account Dashboard under Order History. Customers receive automatic email updates when orders ship and arrive.",

        "Password Reset: Click 'Forgot Password' on the login page. Reset links are sent to your registered email and expire after 24 hours.",

        "Bulk Orders: Discounts are available for purchases exceeding 50 units. Contact sales@company.com for enterprise pricing.",
    ]
