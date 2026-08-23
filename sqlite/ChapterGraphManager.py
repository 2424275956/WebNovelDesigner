import json
import os

import httpx
from llama_index.core.indices.property_graph import VectorContextRetriever
from llama_index.core import StorageContext, load_index_from_storage, PropertyGraphIndex, Document, Settings
from llama_index.core.graph_stores import SimplePropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class GraphManager:
    def __init__(self, persist_dir: str = "resources/db/graph_storage"):
        # 创建可复用且禁用代理的 HTTP 客户端
        self.http_client = httpx.Client(proxy=None, timeout=300.0)
        self.persist_dir = persist_dir
        self.graph_store = None
        self.index = None
        self.storage_context = None


        # 使用兼容 OpenAI 格式的第三方服务（如DeepSeek等）[citation:9]
        local_model_path = os.path.join(os.path.dirname(__file__), "..", "resources/models", "BAAI-bge-small-zh-v1.5")
        print(local_model_path)
        self.embed_model = HuggingFaceEmbedding(
            model_name=local_model_path,
            trust_remote_code=True  # 防止部分模型加载时报错
        )
        # self.llm = OpenAILike(
        #     model="porschefreak:Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-mlx-4Bit",
        #     api_key="sk-omlx-mKkDjqQpMTrP010mZIWp1uek",
        #     api_base="http://127.0.0.1:8000/v1",  # 注意是 api_base
        #     is_chat_model=True,
        #     temperature=0.1,
        #     timeout=300.0,
        #     stream=False,
        #     http_client=self.http_client
        # )
        # Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # 尝试加载已有索引
        self._load_or_create_index()

    def _load_or_create_index(self):
        """加载已持久化的索引，或创建新索引"""
        try:
            # 尝试加载已存在的存储上下文
            self.storage_context = StorageContext.from_defaults(
                persist_dir=self.persist_dir
            )
            self.index = load_index_from_storage(self.storage_context)
            self.graph_store = self.storage_context.property_graph_store
            print(str(self.storage_context.property_graph_store))
            # 加载后立即检查
            if hasattr(self.index, 'index_struct') and hasattr(self.index.index_struct, 'nodes'):
                print(f"   索引中包含 {len(self.index.index_struct.nodes)} 个节点")
            else:
                print("   ⚠️ 无法获取索引节点数量")
        except FileNotFoundError:
            # 首次使用，创建空索引
            self.graph_store = SimplePropertyGraphStore()
            self.storage_context = StorageContext.from_defaults(
                property_graph_store=self.graph_store
            )
            self.index = PropertyGraphIndex.from_documents(
                [],  # 空文档列表
                storage_context=self.storage_context,
                embed_model=self.embed_model,
                show_progress=True,
                # llm=self.llm
            )

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

        # 持久化更新
        self.storage_context.persist(persist_dir=self.persist_dir)
        print(f"✅ 章节 {chapter_metadata.get('chapter_id')} 已合并到索引")

    def retriever(self, query):
        print(11.1)
        # 创建向量检索器
        retriever = VectorContextRetriever(
            self.storage_context.property_graph_store,
            embed_model=self.embed_model,  # 使用你配置的 Embedding 模型
            similarity_top_k=5,  # 返回最相似的5个节点
        include_text=True
        )
        print(11.2)
        print(type(self.storage_context.property_graph_store))
        print(type(self.embed_model))
        print(type(retriever))
        ret = retriever.retrieve(query)
        print(type(ret))
        print(len(ret))
        return

    def inspect_graph_store(self):
        """直接查看图存储中的所有节点 (兼容 0.14.24 版本)"""
        try:
            # 在 0.14.x 版本中，推荐通过 index_struct 来访问节点
            # 首先确保索引已加载
            if not self.index:
                print("❌ 索引未加载")
                return

            # 方法1：通过 index_struct 获取节点（推荐）
            all_nodes = []
            if hasattr(self.index, 'index_struct') and hasattr(self.index.index_struct, 'nodes'):
                # 尝试直接获取节点列表
                all_nodes = list(self.index.index_struct.nodes.values())
            elif hasattr(self.index, '_index_struct') and hasattr(self.index._index_struct, 'nodes'):
                # 兼容不同版本命名
                all_nodes = list(self.index._index_struct.nodes.values())
            elif hasattr(self.index, 'property_graph_store'):
                # 方法2：尝试从图存储的底层 _nodes 字典获取（调试用）
                if hasattr(self.index.property_graph_store, '_nodes'):
                    all_nodes = list(self.index.property_graph_store._nodes.values())
                elif hasattr(self.index.property_graph_store, '_graph'):
                    # 某些版本可能使用 _graph 存储
                    graph_data = self.index.property_graph_store._graph
                    if isinstance(graph_data, dict) and 'nodes' in graph_data:
                        all_nodes = graph_data['nodes']

            if not all_nodes:
                print("⚠️ 未能获取到任何节点，请检查索引是否正确构建。")
                print("  可能原因：")
                print("  1. 索引为空，请先调用 add_chapter 添加数据。")
                print("  2. 持久化目录中没有数据，或数据未正确加载。")
                return

            print(f"📊 图存储中共有 {len(all_nodes)} 个节点")

            # 打印前 3 个节点的文本预览
            keyword = "宋侧"
            found = False

            for i, node in enumerate(all_nodes[:5]):
                print(f"\n--- 节点 {i+1} ---")
                # 节点对象可能具有不同的属性名
                node_text = getattr(node, 'text', None) or getattr(node, 'get_text', lambda: None)()
                node_metadata = getattr(node, 'metadata', None) or getattr(node, 'get_metadata', lambda: None)()

                print(f"节点类型: {type(node).__name__}")
                if node_text:
                    print(f"文本预览: {node_text[:150]}...")
                    if keyword in node_text:
                        print(f"✅ 在此节点中找到 '{keyword}'")
                        found = True
                if node_metadata:
                    print(f"元数据: {node_metadata}")

            # 全量搜索关键词
            if not found:
                for node in all_nodes:
                    node_text = getattr(node, 'text', None) or getattr(node, 'get_text', lambda: None)()
                    if node_text and keyword in node_text:
                        print(f"\n✅ 在节点中找到 '{keyword}': {node_text[:100]}...")
                        found = True
                        break

            if not found:
                print(f"\n❌ 在所有节点的 text 中均未找到 '{keyword}'")
                print("  请检查数据录入时，角色名是否被写入了节点的 text 属性。")

        except Exception as e:
            print(f"❌ 检查失败: {e}")
            print("  请尝试查看日志或重新构建索引。")

    def get_node_count(self):
        """获取索引中的节点数量（兼容 0.14.x 版本）"""
        try:
            # 方法1：通过 property_graph_store 获取
            if hasattr(self.index, 'property_graph_store'):
                graph_store = self.index.property_graph_store

                # 尝试获取所有节点
                if hasattr(graph_store, 'get_all_nodes'):
                    nodes = graph_store.get_all_nodes()
                    return len(nodes)
                elif hasattr(graph_store, '_nodes'):
                    # 直接访问内部字典（调试用）
                    return len(graph_store._nodes)
                elif hasattr(graph_store, '_graph'):
                    # 某些版本可能使用 _graph
                    graph_data = graph_store._graph
                    if isinstance(graph_data, dict) and 'nodes' in graph_data:
                        return len(graph_data['nodes'])

            # 方法2：通过 storage_context 获取
            if hasattr(self, 'storage_context'):
                if hasattr(self.storage_context, 'graph_store'):
                    graph_store = self.storage_context.graph_store
                    if hasattr(graph_store, '_nodes'):
                        return len(graph_store._nodes)

            # 方法3：检查 index_struct 的其他属性
            if hasattr(self.index, 'index_struct'):
                index_struct = self.index.index_struct
                # 尝试各种可能的属性名
                for attr in ['nodes', '_nodes', 'node_ids', 'graph_nodes']:
                    if hasattr(index_struct, attr):
                        nodes = getattr(index_struct, attr)
                        if isinstance(nodes, (list, dict)):
                            return len(nodes) if isinstance(nodes, list) else len(nodes)

            print("⚠️ 无法获取节点数量，可能索引为空或版本不兼容")
            return 0

        except Exception as e:
            print(f"❌ 获取节点数量失败: {e}")
            return 0

    def test_insert_single_doc(self):
        """测试插入单个文档并立即检查"""
        print("="*50)
        print("🧪 开始测试插入单个文档...")

        # 1. 创建测试文档
        test_text = "宋侧是一个性格孤僻的剑客，喜欢独自在月下练剑。"
        test_metadata = {"chapter_id": 999, "title": "测试章节", "characters": ["宋侧"]}
        doc = Document(text=test_text, metadata=test_metadata)

        print(f"📄 文档创建完成")
        print(f"   文本长度: {len(test_text)}")
        print(f"   文本预览: {test_text[:50]}...")
        print(f"   元数据: {test_metadata}")

        # 2. 插入索引
        print("\n⏳ 正在插入索引...")
        try:
            self.index.insert(doc)
            print("✅ 插入操作完成（无报错）")
        except Exception as e:
            print(f"❌ 插入操作报错: {e}")
            return

        # 3. 持久化
        print("\n⏳ 正在持久化...")
        try:
            self.storage_context.persist(persist_dir=self.persist_dir)
            print(f"✅ 持久化完成，目录: {self.persist_dir}")
        except Exception as e:
            print(f"❌ 持久化报错: {e}")
            return

        # 4. 立即检查 property_graph_store.json 文件
        json_path = os.path.join(self.persist_dir, "property_graph_store.json")
        print(f"\n⏳ 检查持久化文件: {json_path}")

        if not os.path.exists(json_path):
            print("❌ 文件不存在！数据可能没有被写入")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✅ 文件存在，大小: {len(json.dumps(data))} 字符")
        print(f"   顶层键: {list(data.keys())}")

        # 查找节点
        if 'nodes' in data:
            nodes = data['nodes']
            print(f"📊 文件中包含 {len(nodes)} 个节点")

            # 检查我们的测试文本
            found = False
            for node_id, node_data in nodes.items():
                if isinstance(node_data, dict):
                    text = node_data.get('text', '')
                    if test_text in text:
                        print(f"✅ 在节点 {node_id} 中找到测试文本: {text[:50]}...")
                        found = True
                        break

            if not found:
                print("❌ 文件中未找到测试文本")
        else:
            print("⚠️ 文件中没有 'nodes' 键")
            # 打印文件的全部内容以便分析
            print("\n📄 文件完整内容:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")

        # 5. 尝试通过关键词检索器验证
        print("\n⏳ 尝试通过关键词检索器验证...")
        try:
            from llama_index.core.indices.property_graph import LLMSynonymRetriever
            retriever = LLMSynonymRetriever(
                self.index.property_graph_store,
                similarity_top_k=5,
            )
            results = retriever.retrieve("宋侧")
            print(f"关键词检索结果数: {len(results)}")
            if results:
                for node in results:
                    print(f"  结果文本: {node.text[:100]}...")
            else:
                print("❌ 关键词检索未找到结果")
        except Exception as e:
            print(f"❌ 关键词检索报错: {e}")

graph_manager = GraphManager()