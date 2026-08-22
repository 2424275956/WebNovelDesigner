import os

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, \
    QListWidgetItem, QDialog, QPlainTextEdit, QScrollArea, QLineEdit, QFileDialog, QMessageBox
import json as std_json

from sqlite.Sqlite3Utils import query_all_prompt, save_prompt_info, remove_prompt, query_prompt_info_by_id, \
    import_prompt_template, query_prompt_template
from resources.style.StyleSheet import button_style_sheet, title_style_sheet, line_edit_style_sheet
from windows.prompt.InsertPrompt import InsertModel


"""触发事件"""
def on_item_clicked(self, item: QListWidgetItem):
    model = item.data(Qt.ItemDataRole.UserRole)
    # 设置配置ID
    self.prompt_id = model['id']
    prompt_page_info(self, model)

"""提示词处理"""
def prompt_page_review_info(model, system_prompt, user_prompt, point_type):
    # 系统提示词
    system = query_prompt_template(model['id'], point_type, 1)
    if system:
        system_prompt.setPlainText(system[0]['context'])
    else:
        system_prompt.setPlainText("")
    # 用户提示词
    user = query_prompt_template(model['id'], point_type, 2)
    if user:
        user_prompt.setPlainText(user[0]['context'])
    else:
        user_prompt.setPlainText("")

"""页面信息"""
def prompt_page_info(self, model):
    # 标题
    self.conf_page_model_name.setText(model['name'])
    """角色分析"""
    prompt_page_review_info(model, self.role_system_prompt, self.role_user_prompt, 1)
    """关系分析"""
    prompt_page_review_info(model, self.relation_system_prompt, self.relation_user_prompt, 2)
    """流程控制"""
    prompt_page_review_info(model, self.process_system_prompt, self.process_user_prompt, 6)
    """改写-场景分析"""
    prompt_page_review_info(model, self.scene_system_prompt, self.scene_user_prompt, 3)
    # 清空场景提示词
    self.scene_prompt_list.clear()
    # 渲染
    review_scene_prompt_list(self.scene_prompt_list, model['id'], 3, 3)
    """改写-脉络改写"""
    prompt_page_review_info(model, self.framework_system_prompt, self.framework_user_prompt, 4)
    """番外-场景分析"""
    prompt_page_review_info(model, self.extra_scene_system_prompt, self.extra_scene_user_prompt, 7)
    # 清空场景提示词
    self.extra_scene_prompt_list.clear()
    # 渲染
    review_scene_prompt_list(self.extra_scene_prompt_list, model['id'], 7, 3)
    """番外-脉络生成"""
    prompt_page_review_info(model, self.extra_framework_system_prompt, self.extra_framework_user_prompt, 8)
    """结果润色"""
    prompt_page_review_info(model, self.polish_system_prompt, self.polish_user_prompt, 5)

"""删除提示词模版"""
def delete_prompt(self):
    remove_prompt(self.prompt_id)
    # 渲染左侧列表
    self.all_models = review_prompt_list(self.model_list)
    if len(self.all_models) > 0:
        prompt_page_info(self, self.all_models[0])

"""导入配置校验"""
def import_prompt_check(self, rules, msg):
    if len(rules) <= 0:
        QMessageBox.warning(self, "错误", msg)
        return False
    return True

"""导入配置"""
def import_prompt(self):
    """使用文件对话框选择文件"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "选择文件",
        "",
        "文本文件 (*.json)"
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = std_json.load(file)
            # 长度校验
            if len(json_data) <= 0:
                QMessageBox.warning(self, "错误", "❌ json数据解析为空")
                return False
            # 名称
            if not import_prompt_check(self, json_data['prompt_name'], "❌ 提示词模版名称为空"):
                return False
            """角色分析"""
            if not import_prompt_check(self, json_data['role_system'], "❌ 角色分析系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['role_user'], "❌ 角色分析用户提示词规则为空"):
                return False
            """关系分析"""
            if not import_prompt_check(self, json_data['relation_system'], "❌ 关系分析系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['relation_user'], "❌ 关系分析用户提示词规则为空"):
                return False
            """流程控制"""
            if not import_prompt_check(self, json_data['process_system'], "❌ 流程控制系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['process_user'], "❌ 流程控制用户提示词规则为空"):
                return False
            """改写-场景分析"""
            if not import_prompt_check(self, json_data['scene_system'], "❌ 改写-场景分析系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['scene_user'], "❌ 改写-场景分析用户提示词规则为空"):
                return False
            # 场景提示词
            scene = json_data['scene']
            if len(scene) <= 0:
                QMessageBox.warning(self, "错误", f"❌ 改写-场景提示词规则为空")
                return False
            for i, item in enumerate(scene):
                scene_name = item['scene_name']
                if len(scene_name) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，改写-场景提示词场景名称为空")
                    return False
                scene_identify = item['scene_identify']
                if len(scene_identify) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，改写-场景提示词识别规则为空")
                    return False
                scene_rules = item['scene_rules']
                if len(scene_rules) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，改写-场景提示词改写规则为空")
                    return False
            """改写-脉络改写"""
            if not import_prompt_check(self, json_data['framework_system'], "❌ 改写-脉络改写系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['framework_user'], "❌ 改写-脉络改写用户提示词规则为空"):
                return False
            """番外-场景分析"""
            if not import_prompt_check(self, json_data['extra_scene_system'], "❌ 番外-场景分析系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['extra_scene_user'], "❌ 番外-场景分析用户提示词规则为空"):
                return False
            # 场景提示词
            extra_scene = json_data['extra_scene']
            if len(extra_scene) <= 0:
                QMessageBox.warning(self, "错误", f"❌ 番外-场景提示词规则为空")
                return False
            for i, item in enumerate(extra_scene):
                scene_name = item['scene_name']
                if len(scene_name) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，番外-场景提示词场景名称为空")
                    return False
                scene_identify = item['scene_identify']
                if len(scene_identify) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，番外-场景提示词识别规则为空")
                    return False
                scene_rules = item['scene_rules']
                if len(scene_rules) <= 0:
                    QMessageBox.warning(self, "错误", f"❌ 第{i + 1}条，番外-场景提示词改写规则为空")
                    return False
            """番外-脉络生成"""
            if not import_prompt_check(self, json_data['extra_framework_system'], "❌ 番外-脉络生成系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['extra_framework_user'], "❌ 番外-脉络生成用户提示词规则为空"):
                return False
            """结果润色"""
            if not import_prompt_check(self, json_data['polish_system'], "❌ 结果润色系统提示词规则为空"):
                return False
            if not import_prompt_check(self, json_data['polish_user'], "❌ 结果润色用户提示词规则为空"):
                return False
            # 请求组装
            req_json = {
                "name": json_data['prompt_name'],
                "role_system": json_data['role_system'],
                "role_user": json_data['role_user'],
                "relation_system": json_data['relation_system'],
                "relation_user": json_data['relation_user'],
                "process_system": json_data['process_system'],
                "process_user": json_data['process_user'],
                "scene_system": json_data['scene_system'],
                "scene_user": json_data['scene_user'],
                "scene": json_data['scene'],
                "framework_system": json_data['framework_system'],
                "framework_user": json_data['framework_user'],
                "extra_scene_system": json_data['extra_scene_system'],
                "extra_scene_user": json_data['extra_scene_user'],
                "extra_scene": json_data['extra_scene'],
                "extra_framework_system": json_data['extra_framework_system'],
                "extra_framework_user": json_data['extra_framework_user'],
                "polish_system": json_data['polish_system'],
                "polish_user": json_data['polish_user']
            }
            # 保存
            import_prompt_template(req_json)
            # 渲染左侧列表
            self.all_models = review_prompt_list(self.model_list)
            QMessageBox.warning(self, "错误", f"✅ 导入模版成功")
            return True
    else:
        QMessageBox.warning(self, "错误", f"❌ 未获取到文件地址")
        return False

"""提示词校验"""
def prompt_check(self, prompt, msg):
    # 系统提示词
    if prompt is None:
        QMessageBox.warning(self, "错误", f"❌ 未获取到{msg}提示词模版")
        return False
    else:
        if len(prompt.toPlainText()) <= 0:
            QMessageBox.warning(self, "错误", f"❌ {msg}提示词规则为空")
            return False
    return True


def save_prompt_conf(self):
    """保存模版"""
    """模版ID"""
    if self.prompt_id is None:
        QMessageBox.warning(self, "错误", f"❌ 未选择提示词模版")
        return False
    """角色分析"""
    # 系统提示词
    if not prompt_check(self, self.role_system_prompt, "角色分析系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.role_user_prompt, "角色分析用户"):
        return False
    """关系分析"""
    # 系统提示词
    if not prompt_check(self, self.relation_system_prompt, "关系分析系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.relation_user_prompt, "关系分析用户"):
        return False
    """流程控制"""
    # 系统提示词
    if not prompt_check(self, self.process_system_prompt, "流程控制系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.process_user_prompt, "流程控制用户"):
        return False
    """改写-场景分析"""
    # 系统提示词
    if not prompt_check(self, self.scene_system_prompt, "改写-场景分析系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.scene_user_prompt, "改写-场景分析用户"):
        return False
    # 场景规则 循环获取
    if len(self.scene_prompt_list) <= 0:
        QMessageBox.warning(self, "错误", f"❌ 改写-场景提示词模版为空")
        return False
    scene = []
    for index in range(self.scene_prompt_list.count()):
        # 获取到item并循环处理
        item = self.scene_prompt_list.item(index)

        # item不可以为空
        if item:
            # 通过 QListWidget 的 itemWidget() 方法，取出绑定到该 item 上的真实 QWidget
            custom_widget = self.scene_prompt_list.itemWidget(item)

            # 容器不为空
            if custom_widget:
                # 场景名称
                scene_name = custom_widget.findChild(QLineEdit, "scene_name")
                if scene_name is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景名称对象获取失败")
                    return False
                else:
                    if len(scene_name.text()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景名称为空")
                        return False
                # 识别点
                identify_text = custom_widget.findChild(QPlainTextEdit, "identify_text")
                if identify_text is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景识别规则对象获取失败")
                    return False
                else:
                    if len(identify_text.toPlainText()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景识别规则为空")
                        return False

                # 改写规则
                rules_text = custom_widget.findChild(QPlainTextEdit, "rules_text")
                if rules_text is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景改写规则对象获取失败")
                    return False
                else:
                    if len(rules_text.toPlainText()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景改写规则为空")
                        return False
                # json组装
                scene.append({
                    "scene_name": scene_name.text(),
                    "scene_identify": identify_text.toPlainText(),
                    "scene_rules": rules_text.toPlainText()
                })
    """改写-脉络改写"""
    # 系统提示词
    if not prompt_check(self, self.framework_system_prompt, "改写-脉络改写系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.framework_user_prompt, "改写-脉络改写用户"):
        return False
    """番外-场景分析"""
    # 系统提示词
    if not prompt_check(self, self.extra_scene_system_prompt, "番外-场景分析系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.extra_scene_user_prompt, "番外-场景分析用户"):
        return False
    # 场景规则 循环获取
    if len(self.extra_scene_prompt_list) <= 0:
        QMessageBox.warning(self, "错误", f"❌ 番外-场景提示词模版为空")
        return False
    extra_scene = []
    for index in range(self.extra_scene_prompt_list.count()):
        # 获取到item并循环处理
        item = self.extra_scene_prompt_list.item(index)

        # item不可以为空
        if item:
            # 通过 QListWidget 的 itemWidget() 方法，取出绑定到该 item 上的真实 QWidget
            custom_widget = self.extra_scene_prompt_list.itemWidget(item)

            # 容器不为空
            if custom_widget:
                # 场景名称
                scene_name = custom_widget.findChild(QLineEdit, "scene_name")
                if scene_name is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景名称对象获取失败")
                    return False
                else:
                    if len(scene_name.text()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景名称为空")
                        return False
                # 识别点
                identify_text = custom_widget.findChild(QPlainTextEdit, "identify_text")
                if identify_text is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景识别规则对象获取失败")
                    return False
                else:
                    if len(identify_text.toPlainText()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景识别规则为空")
                        return False

                # 改写规则
                rules_text = custom_widget.findChild(QPlainTextEdit, "rules_text")
                if rules_text is None:
                    QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景改写规则对象获取失败")
                    return False
                else:
                    if len(rules_text.toPlainText()) <= 0:
                        QMessageBox.warning(self, "错误", f"❌ 序号：{index + 1} ,改写-场景改写规则为空")
                        return False
                # json组装
                extra_scene.append({
                    "scene_name": scene_name.text(),
                    "scene_identify": identify_text.toPlainText(),
                    "scene_rules": rules_text.toPlainText()
                })
    """番外-脉络生成"""
    # 系统提示词
    if not prompt_check(self, self.extra_framework_system_prompt, "番外-脉络生成系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.extra_framework_user_prompt, "番外-脉络生成用户"):
        return False
    """结果润色"""
    # 系统提示词
    if not prompt_check(self, self.polish_system_prompt, "关系分析系统"):
        return False
    # 用户提示词
    if not prompt_check(self, self.polish_user_prompt, "关系分析用户"):
        return False

    # 请求组装
    req_json = {
        "id": self.prompt_id,
        "role_system": self.role_system_prompt.toPlainText(),
        "role_user": self.role_user_prompt.toPlainText(),
        "relation_system": self.relation_system_prompt.toPlainText(),
        "relation_user": self.relation_user_prompt.toPlainText(),
        "process_system": self.process_system_prompt.toPlainText(),
        "process_user": self.process_user_prompt.toPlainText(),
        "scene_system": self.scene_system_prompt.toPlainText(),
        "scene_user": self.scene_user_prompt.toPlainText(),
        "scene":scene,
        "framework_system": self.framework_system_prompt.toPlainText(),
        "framework_user": self.framework_user_prompt.toPlainText(),
        "extra_scene_system": self.extra_scene_system_prompt.toPlainText(),
        "extra_scene_user": self.extra_scene_user_prompt.toPlainText(),
        "extra_scene": extra_scene,
        "extra_framework_system": self.extra_framework_system_prompt.toPlainText(),
        "extra_framework_user": self.extra_framework_user_prompt.toPlainText(),
        "polish_system": self.polish_system_prompt.toPlainText(),
        "polish_user": self.polish_user_prompt.toPlainText()
    }
    # 新增
    save_prompt_info(req_json)
    QMessageBox.warning(self, "错误", f"✅ 提示词模版保存成功")
    return True

"""提示词校验"""
def export_prompt_check(self, prompt_id, point_type, prompt_type, title, export_json, key):
    prompt = query_prompt_template(prompt_id, point_type, prompt_type)
    if not prompt:
        QMessageBox.warning(self, "错误", f"❌ {title}提示词信息为空")
        return False
    if len(prompt[0]['context']) <= 0:
        QMessageBox.warning(self, "错误", f"❌ {title}提示词规则为空")
        return False
    export_json[key] = prompt[0]['context']
    return True

"""导出模版"""
def export_prompt(self):
    if self.prompt_id is None:
        QMessageBox.warning(self, "错误", f"❌ 提示词模版ID获取失败")
        return False
    model = query_prompt_info_by_id(self.prompt_id)
    if len(model) <= 0:
        QMessageBox.warning(self, "错误", f"❌ 提示词模版信息获取失败")
        return False
    # 组装
    export_json = {'prompt_name': model[0]['name']}
    """角色分析"""
    if not export_prompt_check(self, model[0]['id'], 1, 1, "角色分析", export_json, 'role_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 1, 2, "角色分析", export_json, 'role_user'):
        return False
    """关系分析"""
    if not export_prompt_check(self, model[0]['id'], 2, 1, "关系分析", export_json, 'relation_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 2, 2, "关系分析", export_json, 'relation_user'):
        return False
    """流程控制"""
    if not export_prompt_check(self, model[0]['id'], 6, 1, "流程控制", export_json, 'process_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 6, 2, "流程控制", export_json, 'process_user'):
        return False
    """改写-场景分析"""
    if not export_prompt_check(self, model[0]['id'], 3, 1, "改写-场景分析", export_json, 'scene_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 3, 2, "改写-场景分析", export_json, 'scene_user'):
        return False
    # 场景规则查询
    all_scene_prompt = query_prompt_template(self.prompt_id, 3, 3)
    if len(all_scene_prompt) <= 0:
        QMessageBox.warning(self, "错误", f"❌ 改写-场景提示词规则为空")
        return False
    # 场景提示词组装
    scene_data = []
    for scene in all_scene_prompt:
        scene_data.append({
            "scene_name": scene['scene_name'],
            "scene_identify": scene['scene_identify'],
            "scene_rules": scene['context']
        })
    export_json['scene'] = scene_data
    """改写-脉络改写"""
    if not export_prompt_check(self, model[0]['id'], 4, 1, "改写-脉络改写", export_json, 'framework_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 4, 2, "改写-脉络改写", export_json, 'framework_user'):
        return False
    """番外-场景分析"""
    if not export_prompt_check(self, model[0]['id'], 7, 1, "番外-场景分析", export_json, 'extra_scene_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 7, 2, "番外-场景分析", export_json, 'extra_scene_user'):
        return False
    # 场景规则查询
    all_extra_scene_prompt = query_prompt_template(self.prompt_id, 7, 3)
    if len(all_extra_scene_prompt) <= 0:
        QMessageBox.warning(self, "错误", f"❌ 番外-场景提示词规则为空")
        return False
    # 场景提示词组装
    extra_scene_data = []
    for scene in all_extra_scene_prompt:
        extra_scene_data.append({
            "scene_name": scene['scene_name'],
            "scene_identify": scene['scene_identify'],
            "scene_rules": scene['context']
        })
    export_json['extra_scene'] = extra_scene_data
    """番外-脉络生成"""
    if not export_prompt_check(self, model[0]['id'], 8, 1, "番外-脉络生成", export_json, 'extra_framework_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 8, 2, "番外-脉络生成", export_json, 'extra_framework_user'):
        return False
    """结果润色"""
    if not export_prompt_check(self, model[0]['id'], 5, 1, "结果润色", export_json, 'polish_system'):
        return False
    if not export_prompt_check(self, model[0]['id'], 5, 2, "结果润色", export_json, 'polish_user'):
        return False
    # 弹出文件夹选择对话框，让用户选择保存位置
    folder_path = QFileDialog.getExistingDirectory(self, "请选择导出文件夹")
    # 4. 检查用户是否选择了文件夹（防止用户直接点击取消）
    if folder_path:
        # 拼接完整的文件路径
        file_path = os.path.join(folder_path, f"{model[0]['name']}.json")

        # 5. 将数据写入 JSON 文件
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                # indent=4 用于格式化输出，ensure_ascii=False 用于正确保存中文
                std_json.dump(export_json, file, indent=4, ensure_ascii=False)
            QMessageBox.warning(self, "错误", f"✅ 文件导出成功")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"❌ 导出失败")
            print(f"导出失败: {e}")
            return False
    return True


"""提示词窗口"""
def prompt_open_windows(self):
    # 中心部件
    central_widget = QWidget()

    # 垂直布局
    self.model_win_layout = QVBoxLayout(central_widget)
    self.model_win_layout.setContentsMargins(20, 20, 20, 20)
    self.model_win_layout.setSpacing(5)
    # 默认值定义
    self.prompt_id = None

    # 页面渲染
    review_page(self)

    return central_widget

def show_insert_dialog(self):
    dialog = InsertModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        review_prompt_list(self.model_list)

"""页面渲染"""
def review_page(self):
    # 顶部标题栏
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 文案
    title_label = QLabel("提示词配置")
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(title_label)

    # 弹到另一端
    header_layout.addStretch()

    # 新模型按钮
    insert_model_btn = QPushButton("+ 新建模版")
    # 按钮大小
    insert_model_btn.setFixedSize(120, 40)
    # 按钮样式
    insert_model_btn.setStyleSheet(button_style_sheet())
    # 按钮触发函数
    insert_model_btn.clicked.connect(lambda: show_insert_dialog(self))
    header_layout.addWidget(insert_model_btn)

    # 新增导入按钮
    import_model_btn = QPushButton("⏫导入模版")
    # 按钮大小
    import_model_btn.setFixedSize(120, 40)
    # 按钮样式
    import_model_btn.setStyleSheet(button_style_sheet())
    # 按钮触发函数
    import_model_btn.clicked.connect(lambda: import_prompt(self))
    header_layout.addWidget(import_model_btn)

    # 加入主架构
    self.model_win_layout.addLayout(header_layout)

    # 插入水平分割线
    hqf = QFrame()
    hqf.setFrameShape(QFrame.Shape.HLine)
    hqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_win_layout.addWidget(hqf)

    # 下部分内容
    self.model_lower_layout = QHBoxLayout()
    self.model_lower_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    # 左侧列表创建
    self.model_list = QListWidget()
    self.model_list.setContentsMargins(10, 10, 10, 10)
    # 设置大小
    self.model_list.setFixedWidth(200)
    self.model_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.model_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # 渲染列表
    self.all_models = review_prompt_list(self.model_list)
    self.model_list.itemClicked.connect(lambda item: on_item_clicked(self, item))
    # 设置prompt_id
    if self.all_models and len(self.all_models) > 0:
        model = self.all_models[0]
        self.prompt_id = model['id']
    # 配置不为空
    if self.model_list.count() > 0:
        self.model_list.setCurrentRow(0)
    self.model_lower_layout.addWidget(self.model_list)

    # 垂直分割线
    vqf = QFrame()
    vqf.setFrameShape(QFrame.Shape.VLine)
    vqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_lower_layout.addWidget(vqf)

    # 配置页面
    self.conf_page = QVBoxLayout()
    self.conf_page.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    # 菜单栏
    conf_page_row1 = QHBoxLayout()
    conf_page_row1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 第一列
    self.conf_page_model_name = QLabel("-")
    self.conf_page_model_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.conf_page_model_name.setStyleSheet(title_style_sheet())
    conf_page_row1.addWidget(self.conf_page_model_name)
    # 弹开
    conf_page_row1.addStretch()
    # 导出模版
    conf_page_row1_col2 = QPushButton("⏬导出模版")
    conf_page_row1_col2.setStyleSheet(button_style_sheet())
    conf_page_row1_col2.setFixedSize(100, 30)
    conf_page_row1_col2.clicked.connect(lambda : export_prompt(self))
    conf_page_row1.addWidget(conf_page_row1_col2)
    # 编辑
    conf_page_row1_col3 = QPushButton("🖊保存")
    conf_page_row1_col3.setStyleSheet(button_style_sheet())
    conf_page_row1_col3.setFixedSize(80, 30)
    conf_page_row1_col3.clicked.connect(lambda : save_prompt_conf(self))
    conf_page_row1.addWidget(conf_page_row1_col3)
    # 删除
    conf_page_row1_col4 = QPushButton("🗑️删除")
    conf_page_row1_col4.setStyleSheet(button_style_sheet())
    conf_page_row1_col4.setFixedSize(80, 30)
    conf_page_row1_col4.clicked.connect(lambda : delete_prompt(self))
    conf_page_row1.addWidget(conf_page_row1_col4)
    self.conf_page.addLayout(conf_page_row1)
    # 插入分割线
    conf_page_fream1 = QFrame()
    conf_page_fream1.setFrameShape(QFrame.Shape.HLine)
    conf_page_fream1.setFrameShadow(QFrame.Shadow.Sunken)
    self.conf_page.addWidget(conf_page_fream1)

    # 创建滚动区域
    scroll_area = QScrollArea(self)
    # 【关键】允许内容自适应宽度
    scroll_area.setWidgetResizable(True)
    # 隐藏水平滚动条
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # 创建内容容器
    prompt_widget = QWidget()
    scroll_area.setWidget(prompt_widget)

    # 创建水平内部布局
    prompt_inner_layout = QVBoxLayout(prompt_widget)
    prompt_inner_layout.setSpacing(10)

    """角色分析"""
    # 系统提示词
    self.role_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.role_system_prompt, "角色分析系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.role_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.role_user_prompt, "角色分析用户提示词（主要为改写规则）", prompt_inner_layout, 400)

    """关系分析"""
    # 系统提示词
    self.relation_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.relation_system_prompt, "关系分析系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.relation_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.relation_user_prompt, "关系分析用户提示词（主要为改写规则）", prompt_inner_layout, 400)

    """流程控制"""
    # 系统提示词
    self.process_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.process_system_prompt, "流程控制系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.process_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.process_user_prompt, "流程控制用户提示词（主要为改写规则）", prompt_inner_layout, 400)

    """改写-场景分析"""
    # 系统提示词
    self.scene_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.scene_system_prompt, "改写-场景分析系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.scene_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.scene_user_prompt, "改写-场景分析用户提示词（主要为改写规则）", prompt_inner_layout, 400)
    # 场景提示词顶部
    scene_prompt_top = QHBoxLayout()
    scene_prompt_top.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 场景提示词内容
    scene_prompt_title = QLabel("改写-场景提示词")
    scene_prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    scene_prompt_title.setStyleSheet(title_style_sheet())
    scene_prompt_top.addWidget(scene_prompt_title)
    # 弹开
    scene_prompt_top.addStretch()
    # 增加场景规则
    insert_scene_prompt_btn = QPushButton("+ 新增场景规则")
    insert_scene_prompt_btn.setFixedSize(120, 30)
    insert_scene_prompt_btn.setStyleSheet(button_style_sheet())
    scene_prompt_top.addWidget(insert_scene_prompt_btn)
    prompt_inner_layout.addLayout(scene_prompt_top)

    # 场景提示词列表
    self.scene_prompt_list = QListWidget()
    self.scene_prompt_list.setContentsMargins(10, 10, 10, 10)
    # 设置大小
    self.scene_prompt_list.setFixedHeight(500)
    self.scene_prompt_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.scene_prompt_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    insert_scene_prompt_btn.clicked.connect(lambda : create_scene_prompt_text(self.scene_prompt_list))
    # 渲染列表
    review_scene_prompt_list(self.scene_prompt_list, self.prompt_id, 3, 3)
    prompt_inner_layout.addWidget(self.scene_prompt_list)

    """改写-脉络改写"""
    # 系统提示词
    self.framework_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.framework_system_prompt, "改写-脉络改写系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.framework_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.framework_user_prompt, "改写-脉络改写用户提示词（主要为改写规则）", prompt_inner_layout, 400)

    """番外-场景规则"""
    # 系统提示词
    self.extra_scene_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.extra_scene_system_prompt, "番外-场景分析系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.extra_scene_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.extra_scene_user_prompt, "番外-场景分析用户提示词（主要为改写规则）", prompt_inner_layout, 400)
    # 场景提示词顶部
    extra_scene_prompt_top = QHBoxLayout()
    extra_scene_prompt_top.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 场景提示词内容
    extra_scene_prompt_title = QLabel("番外-场景提示词")
    extra_scene_prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    extra_scene_prompt_title.setStyleSheet(title_style_sheet())
    extra_scene_prompt_top.addWidget(extra_scene_prompt_title)
    # 弹开
    extra_scene_prompt_top.addStretch()
    # 增加场景规则
    extra_insert_scene_prompt_btn = QPushButton("+ 新增场景规则")
    extra_insert_scene_prompt_btn.setFixedSize(120, 30)
    extra_insert_scene_prompt_btn.setStyleSheet(button_style_sheet())
    extra_scene_prompt_top.addWidget(extra_insert_scene_prompt_btn)
    prompt_inner_layout.addLayout(extra_scene_prompt_top)

    # 场景提示词列表
    self.extra_scene_prompt_list = QListWidget()
    self.extra_scene_prompt_list.setContentsMargins(10, 10, 10, 10)
    # 设置大小
    self.extra_scene_prompt_list.setFixedHeight(500)
    self.extra_scene_prompt_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.extra_scene_prompt_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    extra_insert_scene_prompt_btn.clicked.connect(lambda : create_scene_prompt_text(self.extra_scene_prompt_list))
    # 渲染列表
    review_scene_prompt_list(self.extra_scene_prompt_list, self.prompt_id, 7, 3)
    prompt_inner_layout.addWidget(self.extra_scene_prompt_list)

    """番外-脉络生成"""
    # 系统提示词
    self.extra_framework_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.extra_framework_system_prompt, "番外-脉络生成系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.extra_framework_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.extra_framework_user_prompt, "番外-脉络生成用户提示词（主要为改写规则）", prompt_inner_layout, 400)


    """结果润色"""
    # 系统提示词
    self.polish_system_prompt = QPlainTextEdit()
    prompt_text_slide(self.polish_system_prompt, "结果润色系统提示词（最好1000字以内，过长会导致遗忘设定）", prompt_inner_layout, 400)
    # 用户提示词
    self.polish_user_prompt = QPlainTextEdit()
    prompt_text_slide(self.polish_user_prompt, "结果润色用户提示词（主要为改写规则）", prompt_inner_layout, 400)

    self.conf_page.addWidget(scroll_area)

    # 渲染默认页面
    if self.all_models:
        prompt_page_info(self, self.all_models[0])

    # 尾部插入配置页面
    self.model_lower_layout.addLayout(self.conf_page)
    # 尾部插入
    self.model_win_layout.addLayout(self.model_lower_layout)

"""系统提示词滑动窗口"""
def prompt_text_slide(plain, title, layout, height):
    label = QLabel(f"{title},已输入：0 字符")
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    label.setStyleSheet(title_style_sheet())
    layout.addWidget(label)
    # 系统提示词框
    plain.setStyleSheet(line_edit_style_sheet())
    plain.setFixedHeight(height)
    plain.textChanged.connect(lambda : system_prompt_count(title, label, plain))
    layout.addWidget(plain)
    # 分割线
    fream = QFrame()
    fream.setFrameShape(QFrame.Shape.HLine)
    fream.setFrameShadow(QFrame.Shadow.Sunken)
    layout.addWidget(fream)

"""增加场景规则"""
def create_scene_prompt_text(scene_prompt_list):
    # 新创卡片
    model_item = QListWidgetItem()
    # 设置高度（宽度由列表控制）
    model_item.setSizeHint(QSize(1200, 200))
    scene_prompt_list.insertItem(0, model_item)

    # ===== 关键：创建一个居中容器 =====
    container = QWidget()
    container.setFixedSize(1200, 200)

    # 容器内部使用水平布局，让卡片居中
    container_layout = QHBoxLayout(container)
    container_layout.setContentsMargins(10, 10, 10, 10)
    container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 创建卡片
    model_frame = QFrame()
    model_frame.setFixedSize(1190, 200)
    model_frame.setStyleSheet("""
                QFrame {
                    background-color: #2D3436;
                    border-radius: 12px;
                    border: 1px solid #3D4447;
                }
                QFrame:hover {
                    border: 1px solid #4A90D9;
                    background-color: #353D3F;
                }
            """)

    # 卡片内部布局
    frame_layout = QHBoxLayout(model_frame)
    frame_layout.setContentsMargins(10, 5, 10, 5)
    frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    ## 左部分
    frame_left_you = QVBoxLayout()
    frame_left_you.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    frame_layout.addLayout(frame_left_you)
    ## 左部分-第一行
    frame_left_row1_layout = QHBoxLayout()
    frame_left_row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    frame_left_you.addLayout(frame_left_row1_layout)
    ### 场景名称
    scene_name_title = QLabel("场景名称：")
    scene_name_title.setFixedSize(80, 30)
    scene_name_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    scene_name_title.setStyleSheet(title_style_sheet(color='white'))
    frame_left_row1_layout.addWidget(scene_name_title)
    ### 场景名称修改
    scene_name = QLineEdit()
    scene_name.setObjectName("scene_name")
    scene_name.setFixedSize(300, 30)
    scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
    scene_name.setStyleSheet(line_edit_style_sheet(15))
    frame_left_row1_layout.addWidget(scene_name)

    ## 左部分-第二行
    frame_left_row2_layout = QHBoxLayout()
    frame_left_row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    frame_left_you.addLayout(frame_left_row2_layout)
    ### 识别框标题
    identify_title = QLabel("<br>".join("场景识别匹配规则"))
    identify_title.setFixedHeight(80)
    identify_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    identify_title.setStyleSheet(title_style_sheet(color='white'))
    frame_left_row2_layout.addWidget(identify_title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    ### 识别框
    identify_text = QPlainTextEdit()
    identify_text.setObjectName("identify_text")
    identify_text.setFixedSize(350, 140)
    identify_text.setStyleSheet(line_edit_style_sheet())
    frame_left_row2_layout.addWidget(identify_text)

    # 规则框标题
    rules_title = QLabel("<br>".join("场景改写规则"))
    rules_title.setFixedHeight(80)
    rules_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    rules_title.setStyleSheet(title_style_sheet(color='white'))
    frame_layout.addWidget(rules_title)
    # 规则框
    rules_text = QPlainTextEdit()
    rules_text.setObjectName("rules_text")
    rules_text.setFixedSize(640, 180)
    rules_text.setStyleSheet(line_edit_style_sheet())
    frame_layout.addWidget(rules_text, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    # 右部分
    frame_right_layout = QVBoxLayout()
    frame_right_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    frame_layout.addLayout(frame_right_layout)
    # 按钮
    scene_delete = QPushButton("🗑️删除")
    scene_delete.setFixedSize(80, 30)
    scene_delete.setStyleSheet(button_style_sheet())
    scene_delete.clicked.connect(lambda : remove_scene_prompt(scene_prompt_list, model_item))
    frame_right_layout.addWidget(scene_delete)
    # 序号
    sort = QLabel("序号：1")
    sort.setObjectName("sort")
    sort.setStyleSheet(title_style_sheet(color='white'))
    frame_right_layout.addWidget(sort)
    ## 弹开
    frame_right_layout.addStretch()

    # 将卡片添加到容器（居中）
    container_layout.addWidget(model_frame)

    # 将容器设置为列表项
    scene_prompt_list.setItemWidget(model_item, container)
    # 重排序
    sort_scene_rules(scene_prompt_list)

"""用户提示词计数"""
def system_prompt_count(title, prompt_title, prompt):
    # 获取文字
    text = prompt.toPlainText()
    char_count = len(text)
    prompt_title.setText(f"{title},已输入：{char_count} 字符")

"""用户提示词计数"""
def user_prompt_count(self):
    # 获取文字
    text = self.user_prompt.toPlainText()
    char_count = len(text)
    self.user_prompt_title.setText(f"用户提示词（主要为改写规则）,已输入：{char_count} 字符")


"""删除卡片"""
def remove_scene_prompt(scene_prompt_list, item):
    if item is None:
        return

    # 1. 获取该 item 在列表中的行号
    row = scene_prompt_list.row(item)

    # 2. 从列表中移除该 item（takeItem 会解除它与列表的绑定）
    taken_item = scene_prompt_list.takeItem(row)

    # 3. 【关键】手动删除 item 释放内存（takeItem 不会自动释放内存）
    if taken_item:
        del taken_item
    # 重排序
    sort_scene_rules(scene_prompt_list)


"""场景规则重排序"""
def sort_scene_rules(scene_prompt_list):
    # 重新排序
    for index in range(scene_prompt_list.count()):
        # 获取到item并循环处理
        item = scene_prompt_list.item(index)

        # item不可以为空
        if item:
            # 通过 QListWidget 的 itemWidget() 方法，取出绑定到该 item 上的真实 QWidget
            custom_widget = scene_prompt_list.itemWidget(item)

            # 容器不为空
            if custom_widget:
                # 场景名称
                sort = custom_widget.findChild(QLabel, "sort")
                if sort:
                    sort.setText(f"序号：{index + 1}")

"""场景规则渲染列表"""
def review_scene_prompt_list(model_list, prompt_id, point_type, prompt_type):
    # 场景规则查询
    all_scene_prompt = query_prompt_template(prompt_id, point_type, prompt_type)
    # 内容不为空
    if all_scene_prompt:
        for row, prompt in enumerate(all_scene_prompt):
            # 创建item占位
            model_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            model_item.setSizeHint(QSize(1200, 200))
            model_list.addItem(model_item)

            # ===== 关键：创建一个居中容器 =====
            container = QWidget()
            container.setFixedSize(1200, 200)

            # 容器内部使用水平布局，让卡片居中
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(10, 10, 10, 10)  # 上下各10px边距
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建卡片
            model_frame = QFrame()
            model_frame.setFixedSize(1190, 200)
            model_frame.setStyleSheet("""
                QFrame {
                    background-color: #2D3436;
                    border-radius: 12px;
                    border: 1px solid #3D4447;
                }
                QFrame:hover {
                    border: 1px solid #4A90D9;
                    background-color: #353D3F;
                }
            """)

            # 卡片内部布局
            frame_layout = QHBoxLayout(model_frame)
            frame_layout.setContentsMargins(10, 5, 10, 5)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            ## 左部分
            frame_left_you = QVBoxLayout()
            frame_left_you.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            frame_layout.addLayout(frame_left_you)
            ## 左部分-第一行
            frame_left_row1_layout = QHBoxLayout()
            frame_left_row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            frame_left_you.addLayout(frame_left_row1_layout)
            ### 场景名称
            scene_name_title = QLabel("场景名称：")
            scene_name_title.setFixedSize(80, 30)
            scene_name_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            scene_name_title.setStyleSheet(title_style_sheet(color='white'))
            frame_left_row1_layout.addWidget(scene_name_title)
            ### 场景名称修改
            scene_name = QLineEdit()
            scene_name.setObjectName("scene_name")
            scene_name.setText(prompt['scene_name'])
            scene_name.setFixedSize(300, 30)
            scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            scene_name.setStyleSheet(line_edit_style_sheet(15))
            frame_left_row1_layout.addWidget(scene_name)

            ## 左部分-第二行
            frame_left_row2_layout = QHBoxLayout()
            frame_left_row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            frame_left_you.addLayout(frame_left_row2_layout)
            ### 识别框标题
            identify_title = QLabel("<br>".join("场景识别匹配规则"))
            identify_title.setFixedHeight(80)
            identify_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            identify_title.setStyleSheet(title_style_sheet(color='white'))
            frame_left_row2_layout.addWidget(identify_title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            ### 识别框
            identify_text = QPlainTextEdit()
            identify_text.setObjectName("identify_text")
            identify_text.setPlainText(prompt['scene_identify'])
            identify_text.setFixedSize(350, 140)
            identify_text.setStyleSheet(line_edit_style_sheet())
            frame_left_row2_layout.addWidget(identify_text)

            # 规则框标题
            rules_title = QLabel("<br>".join("场景改写规则"))
            rules_title.setFixedHeight(80)
            rules_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            rules_title.setStyleSheet(title_style_sheet(color='white'))
            frame_layout.addWidget(rules_title)
            # 规则框
            rules_text = QPlainTextEdit()
            rules_text.setObjectName("rules_text")
            rules_text.setPlainText(prompt['context'])
            rules_text.setFixedSize(640, 180)
            rules_text.setStyleSheet(line_edit_style_sheet())
            frame_layout.addWidget(rules_text, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

            # 右部分
            frame_right_layout = QVBoxLayout()
            frame_right_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            frame_layout.addLayout(frame_right_layout)
            # 按钮
            scene_delete = QPushButton("🗑️删除")
            scene_delete.setFixedSize(80, 30)
            scene_delete.setStyleSheet(button_style_sheet())
            scene_delete.clicked.connect(lambda : remove_scene_prompt(model_list, model_item))
            frame_right_layout.addWidget(scene_delete)
            # 序号
            sort = QLabel("序号：1")
            sort.setObjectName("sort")
            sort.setStyleSheet(title_style_sheet(color='white'))
            frame_right_layout.addWidget(sort)
            ## 弹开
            frame_right_layout.addStretch()

            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)


"""更新模型列表"""
def review_prompt_list(model_list):
    # 清空item
    model_list.clear()

    # 模型配置查询
    all_model = query_all_prompt()
    # 模型配置非空
    if all_model is not None:
        for index, model in enumerate(all_model):
            # 创建item占位
            model_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            model_item.setSizeHint(QSize(200, 80))  # 高度比卡片稍高
            model_item.setData(Qt.ItemDataRole.UserRole, model)
            model_list.addItem(model_item)

            # ===== 关键：创建一个居中容器 =====
            container = QWidget()
            container.setFixedWidth(200)  # 与列表宽度一致

            # 容器内部使用水平布局，让卡片居中
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 10, 0, 10)  # 上下各10px边距
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建卡片
            model_frame = QFrame()
            model_frame.setFixedSize(180, 100)
            model_frame.setStyleSheet("""
                QFrame {
                    background-color: #2D3436;
                    border-radius: 12px;
                    border: 1px solid #3D4447;
                }
                QFrame:hover {
                    border: 1px solid #4A90D9;
                    background-color: #353D3F;
                }
            """)

            # 卡片内部布局
            frame_layout = QVBoxLayout(model_frame)
            frame_layout.setContentsMargins(10, 5, 10, 5)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            # 模型名称
            label = QLabel(model['name'])
            label.setStyleSheet("color: white;border: none; padding: 0; margin: 0; background: transparent;")
            frame_layout.addWidget(label)

            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)

    return all_model
