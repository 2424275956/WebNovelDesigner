from sqlite.ChapterGraphManager import GraphManager

ggraph_manager = GraphManager()
results = ggraph_manager.retriever("陆嫁嫁")
print(f"关键词检索结果数: {len(results)}")
if results:
    for node in results:
        print(f"  结果文本: {node.text}...")
else:
    print("❌ 关键词检索未找到结果")
