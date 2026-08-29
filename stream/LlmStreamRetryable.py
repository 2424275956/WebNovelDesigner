from typing import Callable, Optional

from config.GlobalMap import APP_STATE
from stream.LlmRejectTemplate import is_refusal
from stream.LlmStreamValidator import StreamingValidator


class RetryableStreamChain:
    """
    可重试的流式 LangChain 封装。
    内部处理 astream + 重复校验 + 自动重试。
    """

    def __init__(
            self,
            chain,
            validator_factory: Callable[[], StreamingValidator],
            project_id,
            max_retries: int = 5,
            on_chunk: Optional[Callable[[str], None]] = None,  # 实时回调（如更新 UI）
            on_retry: Optional[Callable[[str, str], None]] = None  # 重试通知
    ):
        self.chain = chain
        self.validator_factory = validator_factory
        self.max_retries = max_retries
        self.on_chunk = on_chunk
        self.on_retry = on_retry
        self.project_id = project_id

    async def ainvoke_with_retry(self, inputs: dict, old_len: int=0, target_len: int=3500) -> str:
        """
        带重试的流式调用。
        返回最终有效文本。
        """
        last_error = ""
        # 是否续写
        is_next_polish = True
        # 是否首次续写检测
        before_refusal_check = True
        # 结果对象
        result_validator = self.validator_factory()
        for attempt in range(self.max_retries):
            # 循环内对象
            validator = self.validator_factory()
            # 将已有内容放入
            validator.total_valid_text = result_validator.total_valid_text

            a_stream = self.chain.astream(inputs)
            try:

                async for chunk in a_stream:
                    if 1 == APP_STATE.get(self.project_id):
                        return ""

                    text = chunk if isinstance(chunk, str) else str(chunk)

                    # 实时校验
                    result = validator.feed(text)

                    if result is None:
                        # 检测到循环，需要重试
                        last_error = f"检测到重复内容（循环模式或行级复读）"
                        if self.on_retry:
                            self.on_retry(f"重复 {attempt + 1}/3", last_error)
                        # 判断是否首次进入
                        if is_next_polish:
                            self.next_polish_inputs(inputs)
                            is_next_polish = False
                        inputs['wait_polish_text'] = self.get_this_text(validator)
                        result_validator.total_valid_text = validator.total_valid_text
                        break  # 跳出 for chunk，进入下一次重试

                    # 模型拒绝判断
                    if before_refusal_check:
                        if text is not None and len(text) > 0:
                            if len(validator.total_valid_text) > 30:
                                refusal, reason_str = is_refusal(validator.total_valid_text)
                                if refusal:
                                    self.on_retry(f"伦理拒绝 {attempt + 1}/3", f"对话请求被模型伦理拒绝,{reason_str}")
                                    break
                                before_refusal_check = False


                    if result and self.on_chunk:
                        self.on_chunk(result)

                else:
                    # 正常结束，获取全部内容
                    res_str = self.get_this_text(validator)
                    # 传递给返回校验组
                    result_validator.total_valid_text = res_str
                    # 判断文本长度是否满足
                    if len(res_str) <= target_len or len(res_str) <= old_len:
                        # 是否需要拼接提示词
                        if is_next_polish:
                            self.next_polish_inputs(inputs)
                        inputs['wait_polish_text'] = res_str
                        self.on_retry(f"阈值未达标 {attempt + 1}/3", f"输出内容长度为：{len(res_str)}")
                        break
                    # 正常完成（没有 break）
                    return result_validator.total_valid_text

            except Exception as e:
                last_error = str(e)
                if self.on_retry:
                    self.on_retry(f"异常 {attempt + 1}/3", last_error)
                continue
            finally:
                if a_stream is not None:
                    try:
                        await a_stream.aclose()
                    except:
                        pass

        # 重试耗尽
        raise RuntimeError(f"流式生成失败，已重试 {self.max_retries} 次。最后错误: {last_error}")

    def next_polish_inputs(self, inputs):
        inputs['system_prompt'] += """
                            【续写任务】
                            上文已完成，请从断点处继续往下写。
                            1. 绝对禁止重复上文已出现过的任何句子、段落、情节。
                            2. 不要从头重写，不要复述前文，直接接着写后续内容。
                            3. 继续扩写原文脉络。
                            4. 时间线严格向前，禁止回溯。
                            5. 禁止输出"接下来""上文提到""如前所述"等过渡性元评论。
                            """
        inputs['user_prompt'] += "\n【待续写内容】\n{wait_polish_text}"

    def get_this_text(self, validator):
        """
        获取已经生成好的内容
        """
        tail = validator.flush()
        if tail and self.on_chunk:
            self.on_chunk(tail)
        return validator.get_valid_text()