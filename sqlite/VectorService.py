import os

from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SQLiteVSS
from sqlite.SqliteDB import SqliteDB


class VectorService:
    _instance = None
    _vector_store = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            local_model_path = os.path.join(os.path.dirname(__file__), "..", "resources/models/embedding", "BAAI-bge-small-zh-v1.5")
            cls._instance = super(VectorService, cls).__new__(cls)
            # 只在第一次调用时初始化模型和数据库
            cls._embeddings = HuggingFaceEmbeddings(
                model_name=local_model_path,
                model_kwargs={'device': 'cpu'},  # 指定运行设备
                encode_kwargs={"normalize_embeddings": True}
            )
            cls._vector_store = SQLiteVSS(
                embedding=cls._embeddings,
                table="novel_embedding",
                connection=SqliteDB.get_conn()
            )
        return cls._instance

    def search(self, query: str, k: int = 3):
        return self._vector_store.similarity_search(query, k=k)

    def split_text(self, text, chapter_title):
        # 使用语义分块器（SemanticTextSplitter）
        semantic_splitter = SemanticChunker(
            embeddings=self._embeddings,
            sentence_split_regex=r"[。！？\n]+" # 适配中文的分隔符
        )

        # 分割文本
        texts = semantic_splitter.split_text(text)

        # 3. 为每个文本块生成元数据（关键步骤，便于检索溯源）
        metadata_list = [{"source": chapter_title, "chunk_index": i} for i in range(len(texts))]

        # 4. 【修复点】使用正确的实例方法 from_texts 进行入库
        self._vector_store.add_texts(texts=texts, metadatas=metadata_list)

# 全局实例
vector_service = VectorService()