from sqlite.VectorService import vector_service


def novel_rag_store(chapter):
    """
    润色结果存储到rag中
    """
    title = chapter['title']
    if "番外" in title:
        title = f"番外：sort：{chapter['sort']}"
    vector_service.split_text(chapter['new_content'], title)