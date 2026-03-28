import os
import json
import re
from typing import Dict, List, Tuple
import requests
from datetime import datetime
import time  # 导入time模块用于添加延迟

# ==================== 配置区 ====================
BASE_PATH = "./结果文件夹"                    # 存放各年JSON的根目录

# API_URL = "http://localhost:11434/v1/chat/completions"  # Ollama API地址
# HEADERS = {
#         "Content-Type": "application/json"
#         }
# MODEL_NAME = "qwen3:0.6b"  # Ollama模型名称


API_URL = "http://localhost:8000/v1/chat/completions"   # 您的LLM API地址
HEADERS = {
        "Authorization": "[token_here]",
        "Content-Type": "application/json"
        }
MODEL_NAME = "Qwen3"  # 原来的模型名

YEARS = range(2009, 2025)                     # 可自行调整

# 教材章节关键词映射（精准匹配408数据结构内容）
CHAPTER_MAP = {
    1: ("绪论", ["时间复杂度", "空间复杂度", "抽象数据类型", "算法分析"]),
    2: ("线性表", ["顺序表", "链表", "单链表", "双链表", "循环链表"]),
    3: ("栈和队列", ["栈", "队列", "循环队列", "链栈", "链队列"]),
    4: ("树与二叉树", ["二叉树", "遍历", "线索二叉树", "哈夫曼树", "森林"]),
    5: ("图", ["邻接矩阵", "邻接表", "最短路径", "拓扑排序", "最小生成树"]),
    6: ("查找", ["顺序查找", "折半查找", "B树", "B+树", "哈希"]),
    7: ("排序", ["冒泡", "插入", "选择", "快速", "归并", "堆排序"])
}

def load_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_chapter(content: str) -> int:
    """根据LLM判断返回章节编号（1-7）"""
    chapter_classification_prompt = f"""
请根据以下题目内容判断它属于数据结构教材《数据结构（C语言版 第3版）》严蔚敏、李冬梅、吴伟民中的哪个章节：

教材章节分类：
1. 绪论 - 涉及时间复杂度、空间复杂度、抽象数据类型、算法分析等基础概念
2. 线性表 - 涉及顺序表、链表、单链表、双链表、循环链表等
3. 栈和队列 - 涉及栈、队列、循环队列、链栈、链队列等
4. 树与二叉树 - 涉及二叉树、遍历、线索二叉树、哈夫曼树、森林等
5. 图 - 涉及邻接矩阵、邻接表、最短路径、拓扑排序、最小生成树等
6. 查找 - 涉及顺序查找、折半查找、B树、B+树、哈希等
7. 排序 - 涉及冒泡、插入、选择、快速、归并、堆排序等

请分析以下题目内容：
{content}

请直接回复章节编号(1-7)，不要有其他内容。
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"正在调用LLM进行章节分类...")
            resp = requests.post(API_URL, headers=HEADERS, json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": chapter_classification_prompt}],
                "temperature": 0.1
            }, timeout=30)
            resp.raise_for_status()
            result = resp.json()['choices'][0]['message']['content'].strip()
            
            # 尝试将结果转换为整数
            try:
                chapter_num = int(result)
                if 1 <= chapter_num <= 7:
                    print(f"LLM判断章节为: 第{chapter_num}章")
                    time.sleep(4)  # 添加4秒延迟
                    return chapter_num
                else:
                    print(f"LLM返回的章节号不在有效范围内(1-7): {chapter_num}，使用默认章节1")
                    return 1
            except ValueError:
                print(f"LLM返回的内容无法转换为整数: {result}，使用默认章节1")
                return 1
                
        except Exception as e:
            print(f"LLM章节分类失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # 最后一次尝试仍然失败
                print("LLM章节分类最终失败，返回默认章节1")
                return 1
    
    return 1  # 默认第1章

def validate_and_classify_question(text_chunk: str) -> Tuple[bool, int]:
    """使用LLM同时判断题目有效性和所属章节"""
    prompt = f"""
请同时完成两项任务：

1. 判断以下文本块是否为一道考察数据结构的题目
   如果是题目，回复"VALID"，如果不是，回复"INVALID"

2. 根据以下题目内容判断它属于数据结构教材《数据结构（C语言版 第3版）》严蔚敏、李冬梅、吴伟民中的哪个章节：
   1. 绪论 - 涉及时间复杂度、空间复杂度、抽象数据类型、算法分析等基础概念
   2. 线性表 - 涉及顺序表、链表、单链表、双链表、循环链表等
   3. 栈和队列 - 涉及栈、队列、循环队列、链栈、链队列等
   4. 树与二叉树 - 涉及二叉树、遍历、线索二叉树、哈希树、森林等
   5. 图 - 涉及邻接矩阵、邻接表、最短路径、拓扑排序、最小生成树等
   6. 查找 - 涉及顺序查找、折半查找、B树、B+树、哈希等
   7. 排序 - 涉及冒泡、插入、选择、快速、归并、堆排序等

文本内容：
{text_chunk}

请按以下格式回复：
状态: [VALID或INVALID]
章节: [1-7的数字]

例如：
状态: VALID
章节: 4
"""
    
    print(f"使用LLM验证题目有效性并分类: {text_chunk[:50]}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"向LLM发送验证和分类请求 (尝试 {attempt + 1}/{max_retries})...")
            resp = requests.post(API_URL, headers=HEADERS, json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, timeout=30)
            resp.raise_for_status()
            result = resp.json()['choices'][0]['message']['content'].strip()
            print(f"LLM返回结果: {result}")
            
            # 解析返回结果
            lines = result.split('\n')
            status = None
            chapter = 1  # 默认第一章
            
            for line in lines:
                if line.startswith('状态:'):
                    status = 'VALID' in line
                elif line.startswith('章节:'):
                    try:
                        chapter = int(line.split(':')[1].strip())
                        if chapter < 1 or chapter > 7:
                            chapter = 1  # 限制在1-7范围内
                    except:
                        chapter = 1  # 解析失败时默认为第一章
            
            if status is not None:
                print(f"解析结果 - 有效: {status}, 章节: {chapter}")
                return status, chapter
            else:
                print("未能从LLM响应中解析出有效状态，使用默认值")
                return False, 1
                
        except Exception as e:
            print(f"LLM验证和分类时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # 最后一次尝试仍然失败
                print("LLM验证和分类最终失败")
                return False, 1
        time.sleep(4)  # 添加4秒延迟
                
    return False, 1  # 默认返回值


def extract_questions_from_md(md_content: str, year: int) -> List[Dict]:
    """从MD文件内容中提取题目"""
    questions = []
    
    # 直接按题号分割，不再按题型分块（因为有些MD文件可能格式不一致）
    # 匹配 1. 2. 3. 等题号开头的行
    pattern = r'(\d{1,3}[\.、:)]\s.*?)(?=\n\s*\d{1,3}[\.、:)]\s|\Z)'
    matches = re.findall(pattern, md_content, re.DOTALL)
    
    for match in matches:
        clean_match = match.strip()
        if clean_match:
            # 使用LLM同时判断有效性并分类章节
            print(f"开始判断题目有效性并分类.")
            is_valid, chapter = validate_and_classify_question(clean_match)
            
            if is_valid:
                q_type = "[单选题]" if re.search(r'[A-D][\.、\)]', clean_match) else "[问答题]"
                question_obj = {
                    'year': year,
                    'chapter': chapter,
                    'type': q_type,
                    'content': clean_match.strip(),
                    'images': []
                }
                questions.append(question_obj)
                print(f"题目已添加到列表，归属第{chapter}章")
            else:
                print(f"题目被判定为无效，跳过: {clean_match[:60]}...")
    
    return questions


def is_valid_question(text_chunk: str) -> bool:
    """使用LLM判断文本块是否为有效题目"""
    prompt = f"""
请判断以下文本块是否为一道考察数据结构的题目
如果是题目，回复"YES"，如果不是，回复"NO"。

文本内容：
{text_chunk}

请只回复"YES"或"NO"
"""
    
    print(f"使用LLM验证题目有效性")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"向LLM发送验证请求 (尝试 {attempt + 1}/{max_retries})...")
            resp = requests.post(API_URL, headers=HEADERS, json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, timeout=30)
            resp.raise_for_status()
            result = resp.json()['choices'][0]['message']['content'].strip()
            print(f"LLM返回结果: {result}")
            print("TRUE")
            return result.upper() == "YES"
        except Exception as e:
            print(f"LLM验证题目有效性时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # 最后一次尝试仍然失败
                print("LLM验证题目有效性最终失败，使用后备逻辑判断")
                # 如果LLM调用失败，使用后备逻辑判断
                # 基本判断：包含题号且有一定长度
                has_number_prefix = bool(re.match(r'^\d+[\.、]', text_chunk))
                length_check = len(text_chunk) > 10
                print(f"后备判断 - 包含题号: {has_number_prefix}, 长度>10: {length_check}")
                return has_number_prefix and length_check
                
    # 默认返回值
    return False


def call_llm_for_full_answer(question: Dict) -> Tuple[str, str]:
    """调用LLM生成真实答案 + 详细解析（核心改进）"""
    print(f"正在处理题目: {question['content']}\n\n")
    
    prompt = f"""
你要整理408全国硕士研究生入学统一考试中《数据结构》的命题与阅卷，必须严格按照教材《数据结构（C语言版 第3版）》严蔚敏、李冬梅、吴伟民的知识点作答。

请将以下题目整理成题库导入格式（仅输出以下内容，不要加任何说明）：

[单选题] 或 [问答题]（根据题目类型）
题干（原样保留，单独一行）

[参考答案]
（单选题只写单个大写字母，如A；问答题写完整答案）

[答案解析]
（必须包含：
1. 详细推理/计算每一步中间结果
2. 关键代码思路或伪代码
3. 时间复杂度与空间复杂度分析
4. 教材对应章节知识点
5. 若有图，文字描述图的关键结构）

题目如下：
{question['content']}

请严格按以上格式输出，不要省略任何部分。解析长度控制在3000字符以内，但必须详细易懂。
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(API_URL, headers=HEADERS, json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }, timeout=60)
            resp.raise_for_status()
            result = resp.json()['choices'][0]['message']['content'].strip()
            
            print("LLM响应成功获取 \n\n")
            print(f"LLM返回结果预览: {result} \n\n\n ")  # 显示返回结果的前200个字符
            
            # 提取答案和解析
            answer_match = re.search(r'\[参考答案\](.*?)(?=\[答案解析\]|\Z)', result, re.DOTALL)
            parse_match = re.search(r'\[答案解析\](.*)', result, re.DOTALL)
            
            extracted_answer = answer_match.group(1).strip() if answer_match else "待人工核对【LLM ERROR】"
            extracted_parse = parse_match.group(1).strip() if parse_match else "待人工核对【LLM ERROR】"
            
            print(f"提取到的答案: {extracted_answer}")
            print(f"解析内容长度: {len(extracted_parse)} 字符")
            time.sleep(4)  # 添加4秒延迟
            
            return extracted_answer, extracted_parse
        except Exception as e:
            print(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # 最后一次尝试仍然失败
                print("LLM调用最终失败")
                return "待人工核对", "待人工核对【LLM ERROR】"

    # 添加明确的返回语句，确保在所有路径都有返回值
    return "待人工核对", "待人工核对【LLM ERROR】"


def save_chapter_files(all_questions: List[Dict], year: int):
    """按章节保存（每章一个文件）"""
    print(f"开始按章节分类 {year} 年的 {len(all_questions)} 道题目...")
    
    chapters = {i: [] for i in range(1, 8)}
    for q in all_questions:
        chapters[q['chapter']].append(q)
    
    total_processed = 0
    for ch, qs in chapters.items():
        if not qs:
            continue
        ch_name = [name for num, (name, _) in CHAPTER_MAP.items() if num == ch][0]
        content = [f"# {year}年 数据结构 第{ch}章 {ch_name}\n\n"]
        
        prev_type = None
        for q in qs:
            if q['type'] != prev_type:
                content.append(q['type'])
                prev_type = q['type']
            
            content.append(q['content'])
            
            # 配图处理
            if q.get('images'):
                content.append(f"[配图：第{q['images'][0].get('page', '?')}页原图]（已保存高清图片）")
            
            print(f"正在处理第 {ch} 章的题目 ({total_processed + 1}/{len(all_questions)})...")
            ans, parse = call_llm_for_full_answer(q)
            content.append(f"[参考答案]{ans}")
            content.append(f"[答案解析]{parse}")
            content.append("\n")
            
            total_processed += 1
        
        output_dir = os.path.join(BASE_PATH, str(year), "题库_按章")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{year}_第{ch}章_{ch_name}.md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        print(f"✓ 已生成：{file_path}（{len(qs)}题）")

def main():
    print(f"[{datetime.now()}] 开始处理近10年408数据结构题库...")
    
    for year in YEARS:
        year_path = os.path.join(BASE_PATH, str(year))
        if not os.path.exists(year_path):
            print(f"  跳过 {year} 年，目录不存在: {year_path}")
            continue
            
        print(f"\n正在处理 {year} 年...")
        all_q = []
        
        for file in os.listdir(year_path):
            if file.endswith('.md') and 'full' in file:  # 只处理MD文件，特别是full.md
                print(f"  正在加载文件: {file}")
                with open(os.path.join(year_path, file), 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # 从MD内容中提取题目
                qs = extract_questions_from_md(md_content, year)
                all_q.extend(qs)
                print(f"  已从 {file} 中提取 {len(qs)} 道题目")
        
        if all_q:
            print(f"  {year} 年共提取到 {len(all_q)} 道题目")
            save_chapter_files(all_q, year)
        else:
            print(f"  未找到{year}年题目")
    
    print(f"\n[{datetime.now()}] 全部处理完成！")

if __name__ == "__main__":
    main()