import os

import chromadb
from llama_index.core import StorageContext, load_index_from_storage, PropertyGraphIndex, Document, Settings
from llama_index.core.graph_stores import SimplePropertyGraphStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.indices.property_graph import VectorContextRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class GraphManager:
    def __init__(self, persist_dir: str = "resources/db/graph_storage"):
        # 创建可复用且禁用代理的 HTTP 客户端
        self.persist_dir = persist_dir
        self.graph_store = None
        self.index = None
        self.storage_context = None

        # 初始化 ChromaDB 持久化客户端
        self.chroma_client = chromadb.PersistentClient(path="resources/db/chroma_db")

        # 3. 创建或获取一个 Collection
        self.chroma_collection = self.chroma_client.get_or_create_collection("my_knowledge_base")

        self.vector_store= ChromaVectorStore(chroma_collection=self.chroma_collection)

        # 使用兼容 OpenAI 格式的第三方服务（如DeepSeek等）[citation:9]
        local_model_path = os.path.join(os.path.dirname(__file__), "..", "resources/models", "BAAI-bge-small-zh-v1.5")
        self.embed_model = HuggingFaceEmbedding(
            model_name=local_model_path,
            device="cpu",
            trust_remote_code=True  # 防止部分模型加载时报错
        )
        Settings.embed_model = self.embed_model
        Settings.llm = None

        # 初始化加载
        self._load_or_create_index()

    def _load_or_create_index(self):
        """加载已持久化的索引，或创建新索引"""
        os.makedirs(self.persist_dir, exist_ok=True)
        doc_store_path = os.path.join(self.persist_dir, "docstore.json")

        # 如果之前没创建过，这里会创建一个内存中的空图存储；
        self.graph_store = SimplePropertyGraphStore()
        # 1. 先准备好存储上下文（但先不加载）
        # 注意：这里先不创建 storage_context，而是先判断文件是否存在
        if os.path.exists(doc_store_path):
            try:
                # 文件存在时，再创建 storage_context 并加载
                self.storage_context = StorageContext.from_defaults(
                    property_graph_store=self.graph_store,
                    vector_store=self.vector_store,  # 注意：这里应该传入 vector_store，而不是 chroma_collection
                    persist_dir=self.persist_dir
                )
                self.index = load_index_from_storage(self.storage_context)
                print(f"✅ 从 {self.persist_dir} 加载索引成功")
                return
            except Exception as e:
                print(f"⚠️ 加载索引失败: {e}，将创建新索引")
                # 如果加载失败，建议删除损坏的 json 文件，避免死循环
                if os.path.exists(doc_store_path):
                    os.remove(doc_store_path)

        # 2. 文件不存在或加载失败，创建新的存储上下文和空索引
        print(f"📦 在 {self.persist_dir} 未找到索引，正在创建新索引...")
        self.storage_context = StorageContext.from_defaults(
            property_graph_store=self.graph_store,
            vector_store=self.vector_store,
        )

        self.index = PropertyGraphIndex(
            nodes=[],
            embed_model=self.embed_model,
            storage_context=self.storage_context,
        )
        # 立即持久化，创建 docstore.json 等文件
        self.storage_context.persist(persist_dir=self.persist_dir)
        print(f"✅ 新索引已创建并持久化到 {self.persist_dir}")

    def add_chapter(self, chapter_text: str, chapter_metadata: dict):
        """增量添加一个章节"""
        print(1.1)
        # 创建章节文档对象
        doc = Document(
            text=chapter_text,
            metadata=chapter_metadata  # 包含章节号、时间等
        )

        print(1.2)
        # 将新文档插入现有索引（关键步骤）
        self.index.insert(doc)
        print(1.3)

        # 如果支持增量持久化
        self.storage_context.persist(persist_dir=self.persist_dir)
        print(f"✅ 章节 {chapter_metadata.get('chapter_id')} 已合并到索引")


    def retriever(self, query):
        """
        检索
        """
        print(11.1)
        # 创建向量检索器
        retriever = self.index.as_retriever(
            retriever_mode="vector",
            include_text=True,
            similarity_top_k=5)
        print(11.2)
        # retriever = VectorContextRetriever(
        #     self.storage_context.property_graph_store,
        #     embed_model=self.embed_model,
        #     vector_store=self.vector_store,
        #     similarity_top_k=5,
        #     include_text=True
        # )
        return retriever.retrieve(query)

graph_manager = GraphManager()