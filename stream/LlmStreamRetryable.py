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
            max_retries: int = 3,
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
        # 循环次数
        attempt = 1
        # 拒绝次数,超过5次循环次数+1
        refusal_num = 1
        while True:
            # 超过限制
            if attempt > self.max_retries:
                return ""

            # 是否首次续写检测
            before_refusal_check = True

            # 校验对象
            validator = self.validator_factory()

            # 流式对象
            a_stream = self.chain.astream(inputs)
            try:
                # 循环处理
                async for chunk in a_stream:
                    if 1 == APP_STATE.get(self.project_id):
                        return ""

                    text = chunk if isinstance(chunk, str) else str(chunk)

                    # 实时校验
                    result = validator.feed(text)

                    if result is None:
                        # 检测到循环，需要重试
                        last_error = f"检测到重复内容（循环模式或行级复读）"

                        # 报错打印
                        if self.on_retry:
                            self.on_retry(f"重复 {attempt}/3", last_error)

                        # 循环次数+1
                        attempt += 1
                        # 跳出 for chunk，进入下一次重试
                        continue

                    # 模型拒绝判断
                    if before_refusal_check:
                        # 本次输出chunk内容大于0
                        if text is not None and len(text) > 0:
                            # 已输出内容大于30
                            if len(validator.total_valid_text) > 30:
                                # 是否拒绝
                                refusal, reason_str = is_refusal(validator.total_valid_text)
                                # 拒绝执行
                                if refusal:
                                    self.on_retry(f"伦理拒绝 {refusal_num}/5", f"对话请求被模型伦理拒绝,{reason_str}")
                                    # 拒绝次数超过5次
                                    if refusal_num > 5:
                                        # 循环次数+1
                                        attempt += 1
                                        # 拒绝次数重置
                                        refusal_num = 1
                                    break
                                # 一次循环只校验一次
                                before_refusal_check = False


                    if result and self.on_chunk:
                        self.on_chunk(result)

                else:
                    # 正常结束，获取全部内容
                    res_str = self.get_this_text(validator)
                    # 判断文本长度是否满足
                    if len(res_str) < old_len:
                        # 是否需要拼接提示词
                        self.on_retry(f"阈值未达标 {attempt}/3", f"输出内容长度为：{len(res_str)}")
                        attempt += 1
                        continue
                    # 正常完成（没有 break）
                    return res_str

            except Exception as e:
                last_error = str(e)
                if self.on_retry:
                    self.on_retry(f"异常 {attempt}/3", last_error)
                attempt += 1
                continue
            finally:
                if a_stream is not None:
                    try:
                        await a_stream.aclose()
                    except:
                        pass

        # 重试耗尽
        raise RuntimeError(f"流式生成失败，已重试 {self.max_retries} 次。最后错误: {last_error}")

    def get_this_text(self, validator):
        """
        获取已经生成好的内容
        """
        tail = validator.flush()
        if tail and self.on_chunk:
            self.on_chunk(tail)
        return validator.get_valid_text()