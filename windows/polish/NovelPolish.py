from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from sqlite.Sqlite3Utils import query_wait_polish_chapter


def polish(params):
    """润色小说"""
    self, transmit = params
    # 获取项目ID
    project_id = transmit['project_id']
    # 获取全部待完成章节
    chapter_list = query_wait_polish_chapter(project_id)
    # 没有待处理章节
    if chapter_list is None or len(chapter_list) <= 0:
        return

    # 模型数组
    model_map = {}
    # 循环初始化模型
    for model in transmit['model_map']:
        llm = ChatOpenAI(model=model['model_id'],
                         api_key=model['api_key'],
                         base_url=model['url'],
                         temperature=model['temperature'],
                         max_tokens=model['max_token'],
                         top_p=model['top_p'],
                         timeout=model['time_out'])
        model_map['model_id'] = llm

    # 定义提示词
    ## 角色分析提示词模版
    role_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['original_text']),
        ("user", transmit['role_user'])
    ])
    ## 关系分析提示词模版
    relation_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['relation_system']),
        ("user", transmit['relation_user'])
    ])
    ## 流程控制提示词模版
    process_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['process_system']),
        ("user", transmit['process_user'])
    ])
    ## 原文改写
    ### 原文改写-场景分析
    original_scene_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['scene_system']),
        ("user", transmit['scene_user'])
    ])
    ### 原文改写-脉络改写
    original_framework_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['framework_system']),
        ("user", transmit['framework_user'])
    ])
    ## 番外撰写
    ### 番外撰写-场景分析
    extra_scene_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['extra_scene_system']),
        ("user", transmit['extra_scene_user'])
    ])
    ### 番外撰写-脉络生成
    extra_framework_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['extra_framework_system']),
        ("user", transmit['extra_framework_user'])
    ])
    ## 结果润色
    polish_prompt_template = ChatPromptTemplate.from_messages([
        ("system", transmit['polish_system']),
        ("user", transmit['polish_user'])
    ])

    # 定义LangChain流程
    ## 公共前置LangChain链
    common_chain = (
        {"role_analysis": role_prompt_template | model_map.get(transmit['role_model_id']) | StrOutputParser()} |
        {"relation_analysis": relation_prompt_template | model_map.get(transmit['relation_model_id']) | StrOutputParser()} |
        {"process_analysis": process_prompt_template | model_map.get(transmit['process_model_id']) | StrOutputParser()}
    )
    ## 原文改写LangChain链
    original_chain = (
        {"original_scene_analysis": original_scene_prompt_template | model_map.get(transmit['scene_model_id']) | StrOutputParser()} |
        {"original_framework_analysis": original_framework_prompt_template | model_map.get(transmit['framework_model_id']) | StrOutputParser()} |
        {"polish_analysis": polish_prompt_template | model_map.get(transmit['polish_model_id']) | StrOutputParser()}
    )
    ## 番外撰写LangChain链
    extra_chain = (
        {"extra_scene_analysis": extra_scene_prompt_template | model_map.get(transmit['extra_scene_model_id']) | StrOutputParser()} |
        {"extra_framework_analysis": extra_framework_prompt_template | model_map.get(transmit['extra_framework_model_id']) | StrOutputParser()} |
        {"polish_analysis": polish_prompt_template | model_map.get(transmit['polish_model_id']) | StrOutputParser()}
    )

    # 循环处理
    for chapter in chapter_list:
        # 从开头开始
        if 400 > chapter['point']:
            # 判断是否需要切割
            if 100 == chapter['point']:
                # todo 首次进入正常执行
                123
            elif 200 == chapter['point']:
                # todo 截取执行
                123
            else:
                # todo 流程控制执行
                321

        # 如果进入说明，上次失败导致进度卡住了
        if 2 == chapter['type']:
            # 说明刚到就退出了
            if 410 == chapter['point']:
                # todo 正常执行番外撰写
                123
            elif 411 == chapter['point']:
                # todo 截取并执行
                123
            else:
                # todo 润色
                123
        else:
            # 先判断节点
            if 400 == chapter['point']:
                # 判断是否需要扩写内容
                is_extra = False
                if is_extra:
                    """需要进行番外扩写"""
                    # todo 新增番外章节
                    # todo 改写当前章节
                else:
                    """不需要扩写，正常执行"""
            elif 401 == chapter['point']:
                # todo 截取执行
                123
            else:
                # todo 润色
                123

def chapter_polish(self, chapter, transmit):
    123