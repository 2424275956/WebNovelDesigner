# 简介
	WebNovelDesigner是一款专为小说改写与番外生成的润色工具。核心为将每一步骤进行精细控制来保证数据质量。
# 基础架构
1. Python语言
2. PySide6 GUI界面框架
3. SQLite3 数据存储
4. LangChain 模型框架
# 核心特性
1. 将对一个章节的润色细节拆分为最小粒度并支持控制，用以保证输出质量以便随时调整。
2. 支持同一章节不同阶段的模型与提示词支持修改。
# 模型界面
<img width="124" height="404" alt="image" src="https://github.com/user-attachments/assets/712dc000-c533-4d8d-b039-76ed22659386" />

从上而下为：
## 项目管理
<img width="3200" height="1976" alt="image" src="https://github.com/user-attachments/assets/2b6948ee-cf9b-4a12-9de3-d190972ab02c" />

### 导入文件（右上角）
### 项目页面
<img width="3200" height="1976" alt="image" src="https://github.com/user-attachments/assets/2e82ad16-1206-4b7e-a461-f696d86fcab5" />

#### 章节导航
<img width="516" height="486" alt="image" src="https://github.com/user-attachments/assets/3384b0c3-a8f8-4122-9d6f-6c68e9e78b8e" />

未开始：展示原文长度
进行中：展示阶段状态（角色分析、流程控制、番外场景分析、番外脉络撰写、原文场景分析、原文脉络改写、结果润色、角色关系分析）
已完成：展示原文与改写后长度
### 文本区域
<img width="1242" height="362" alt="image" src="https://github.com/user-attachments/assets/e01d436e-26d8-4a56-9271-d533adcd4c1f" />

选择章节后，点击按钮查看阶段内容
### 章节处理状态
<img width="446" height="446" alt="image" src="https://github.com/user-attachments/assets/7b5e4e58-a443-49a9-bd03-70cb9dc22ab4" />

### 章节润色配置
<img width="826" height="480" alt="image" src="https://github.com/user-attachments/assets/0bbb6b50-1e0c-44e2-98ac-8cabf4b574b9" />

从上而下：
1. 选择整体使用的提示词模版。
2. 改写/撰写附带前置多少章节简述剧情，作为滑动窗口。
3. 改写/撰写附带后续多少章节简述剧情，作为模型发挥限制。
4. 章节插入时会进行排序1、2、3、4...；番外会占用当前章节序号并让后续章节序号+1，控制从多少章节后开始插入番外，默认为5来保证开头内容的锚点内容，保证后续剧情发展更加合理适配。
### 模型配置
<img width="1216" height="1072" alt="image" src="https://github.com/user-attachments/assets/5503269e-2fc0-4667-b70e-d11b42296ec5" />

1. 选择阶段使用的模型。
2. 文本区域 展示提示词内容。
### 主角团队内容
<img width="1216" height="218" alt="image" src="https://github.com/user-attachments/assets/73b958c4-e50c-4780-8778-86d52fa21b61" />

用于提示词中单独主角的一些设定使用，必选项。用于核心剧情具体以哪些角色为主，不进行配置会导致内容发展脱离主角，无法受控。
## 模型管理
<img width="3200" height="1976" alt="image" src="https://github.com/user-attachments/assets/5e0dbdb6-d3d8-4f6e-8afb-f76fcd8d139a" />

### 模型列表
展示所有已配置的模型。
### 新增模型配置/编辑
1. 模型名称：润色使用的模型标识。如：DeepseekV4、Qwen3.8等。
2. 模型类型：作为区分，实际使用为是否需要API Key。
3. API Key：用于的唯一认证标识，请求接收者认证所需。
4. Base URL：请求的地址，如：oMLX（localhost:8000）、Ollama（localhost:11434）、Customer（硅基流动等网络请求地址）。
5. 模型ID：具体要调用的模型，如：本地模型（Qwen3.6:27B）、网络模型（DeepSeek V4）等。
6. 温度：模型的自由度，较低时输出更加标准（分析等流程使用）、较高时改写撰写使用（更有创造性）
7. TOP-P：模型输出时，选择下个词的范围。较低时会选择可能性更高的词来输出，较高时输出的词有更多选择。
8. MaxToken：输出内容长度
## 提示词管理
<img width="3200" height="1976" alt="image" src="https://github.com/user-attachments/assets/367f91bb-22f0-460e-97aa-7e1f976716dd" />

### 新增提示词/导入提示词模版
新增提示词配置
### 角色分析提示词
1. 角色分析系统提示词：核心设定
2. 角色分析用户提示词：可接受忽视的设定
### 关系分析提示词
### 流程控制提示词
### 改写-场景分析提示词
### 改写-脉络改写提示词
### 番外-场景分析提示词
### 番外=脉络生成提示词
### 结果润色提示词
