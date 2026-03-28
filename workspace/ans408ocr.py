import os
import re
import json
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import time
import subprocess


class PDFProcessor:
    """
    PDF处理器，用于解析PDF并按年份分类试题和解析
    """
    
    def __init__(self, api_token: str):
        """
        初始化PDF处理器
        
        Args:
            api_token: MinerU API的认证令牌
        """
        self.api_token = api_token
        self.base_url = "https://mineru.net/api/v4"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        # 创建输出目录
        self.results_dir = Path("结果文件夹")
        self.results_dir.mkdir(exist_ok=True)
    
    def extract_year_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名中提取年份
        
        Args:
            filename: 文件名
            
        Returns:
            年份字符串，如果未找到则返回None
        """
        # 匹配年份的正则表达式，如"2009年"或"2009"
        year_match = re.search(r'(?:^|\D)(19|20)\d{2}(?:年|$|\D)', filename)
        if year_match:
            year_str = year_match.group(0).replace('年', '').strip()
            # 确保提取的是完整的年份（4位数字）
            if len(year_str) >= 4 and year_str.isdigit():
                return year_str[:4]
        return None
    
    def submit_url_task(self, url: str, model_version: str = "vlm", data_id: str = '') -> Optional[str]:
        """
        提交URL解析任务
        
        Args:
            url: 文件URL
            model_version: 模型版本
            data_id: 数据ID
            
        Returns:
            任务ID，如果提交失败则返回None
        """
        task_url = f"{self.base_url}/extract/task"
        data = {
            "url": url,
            "model_version": model_version
        }
        
        if data_id:
            data["data_id"] = data_id
        
        print(f"正在提交解析任务: {url}")
        response = requests.post(task_url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            print(f"提交解析任务失败: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
        if result.get("code") != 0:
            print(f"提交解析任务失败: {result}")
            return None
            
        task_id = result["data"]["task_id"]
        print(f"解析任务已提交，任务ID: {task_id}")
        return task_id
    
    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果，如果获取失败则返回None
        """
        task_url = f"{self.base_url}/extract/task/{task_id}"
        
        max_attempts = 60  # 最多等待30分钟（60次 × 30秒）
        attempt_count = 0
        
        while attempt_count < max_attempts:
            response = requests.get(task_url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"获取任务结果失败: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            if result.get("code") != 0:
                print(f"获取任务结果失败: {result}")
                return None
                
            state = result["data"]["state"]
            print(f"任务状态: {state}")
            
            if state == "done":
                print("任务完成")
                return result["data"]
            elif state == "failed":
                print(f"任务执行失败: {result['data'].get('err_msg', 'Unknown error')}")
                return None
            elif state in ["pending", "running", "converting"]:
                attempt_count += 1
                print(f"等待解析完成... ({attempt_count}/{max_attempts})")
                time.sleep(30)  # 等待30秒后再次查询
            else:
                print(f"未知任务状态: {state}")
                return None
        
        print("等待超时，任务可能仍在处理中")
        return None
    
    def download_and_extract_result(self, zip_url: str, output_dir: Path) -> bool:
        """
        下载并解压结果文件
        
        Args:
            zip_url: ZIP文件下载URL
            output_dir: 输出目录
            
        Returns:
            是否成功
        """
        try:
            print(f"正在下载解析结果: {zip_url}")
            response = requests.get(zip_url)
            
            if response.status_code != 200:
                print(f"下载解析结果失败: {response.status_code}")
                return False
                
            zip_path = output_dir / "temp_result.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
                
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
                
            # 删除临时ZIP文件
            os.remove(zip_path)
            print(f"解析结果已保存到: {output_dir}")
            return True
        except Exception as e:
            print(f"下载或解压结果失败: {str(e)}")
            return False

    def post_process_results(self, year_dir: Path) -> bool:
        """
        对OCR结果进行后处理，生成解析文件

        Args:
            year_dir: 年份目录

        Returns:
            是否成功处理
        """
        try:
            print(f"开始对 {year_dir} 年份的结果进行后处理...")
            
            # 检查是否有full.md文件
            full_md_path = year_dir / "full.md"
            if not full_md_path.exists():
                print(f"未找到 {full_md_path}，跳过后处理")
                return False

            # 读取full.md内容
            with open(full_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取题目并生成解析
            questions = self._extract_questions(content)
            if not questions:
                print(f"在 {full_md_path} 中未找到有效题目")
                return False

            print(f"找到 {len(questions)} 道题目，准备生成解析...")

            # 生成带有解析的文件
            parsed_content = self._generate_parsed_content(questions, year_dir.name)
            parsed_file_path = year_dir / "full_ans.md"
            with open(parsed_file_path, 'w', encoding='utf-8') as f:
                f.write(parsed_content)

            print(f"解析文件已生成: {parsed_file_path}")
            return True

        except Exception as e:
            print(f"后处理过程中出现错误: {str(e)}")
            return False

    def _extract_questions(self, content: str) -> List[Dict]:
        """
        从OCR结果中提取题目

        Args:
            content: OCR结果内容

        Returns:
            题目列表
        """
        questions = []
        # 匹配 1. 2. 3. 等题号开头的行
        pattern = r'(\d{1,3}[\.、:)]\s.*?)(?=\n\s*\d{1,3}[\.、:)]\s|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            clean_match = match.strip()
            if clean_match and len(clean_match) > 10:  # 确保题目有一定长度
                # 简单判断题目类型
                q_type = "[单选题]" if re.search(r'[A-D][\.、\)]', clean_match) else "[问答题]"
                # 修复：安全地获取题号，避免None值访问group()
                number_match = re.match(r'(\d{1,3})', clean_match)
                question_number = number_match.group(1) if number_match else ''
                question_obj = {
                    'number': question_number,
                    'content': clean_match.strip(),
                    'type': q_type
                }
                questions.append(question_obj)

        return questions

    def _generate_parsed_content(self, questions: List[Dict], year: str) -> str:
        """
        生成带解析的内容

        Args:
            questions: 题目列表
            year: 年份

        Returns:
            带解析的内容
        """
        content_lines = [f"# {year}年全国硕士研究生入学统一考试计算机科学与技术学科联考计算机学科专业基础综合试题解析\n"]
        content_lines.append("# 题目及解析\n")

        for idx, q in enumerate(questions, 1):
            content_lines.append(f"\n## 第{q['number']}题\n")
            content_lines.append(q['content'])
            content_lines.append("\n### [参考答案]\n待补充\n")
            content_lines.append("### [答案解析]\n待补充\n")

        return "\n".join(content_lines)

    def process_local_pdf(self, local_pdf_path: str, model_version: str = "vlm") -> bool:
        """
        处理本地PDF文件，使用批量上传的方式
        
        Args:
            local_pdf_path: 本地PDF文件路径
            model_version: 模型版本
            
        Returns:
            是否成功处理
        """
        print(f"开始处理本地PDF: {local_pdf_path}")
        
        # 从文件名提取年份
        file_name = os.path.basename(local_pdf_path)
        year = self.extract_year_from_filename(file_name)
        
        if not year:
            print(f"无法从文件名中提取年份: {file_name}")
            return False
            
        print(f"从文件名提取到年份: {year}")
        
        # 使用批量上传接口
        batch_url = f"{self.base_url}/file-urls/batch"
        data = {
            "files": [{"name": file_name, "data_id": year}],
            "model_version": model_version
        }
        
        print("正在申请上传URL...")
        response = requests.post(batch_url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            print(f"申请上传URL失败: {response.status_code} - {response.text}")
            return False
            
        result = response.json()
        if result.get("code") != 0:
            print(f"申请上传URL失败: {result}")
            return False
            
        batch_id = result["data"]["batch_id"]
        upload_urls = result["data"]["file_urls"]
        
        # 上传文件
        print(f"正在上传文件 {file_name}...")
        with open(local_pdf_path, 'rb') as f:
            upload_response = requests.put(upload_urls[0], data=f)
            
        if upload_response.status_code != 200:
            print(f"文件上传失败: {upload_response.status_code} - {upload_response.text}")
            return False
            
        print(f"文件 {file_name} 上传成功")
        
        # 创建按年份分类的目录
        year_dir = self.results_dir / year
        year_dir.mkdir(exist_ok=True)
        
        # 等待处理完成
        print("文件已上传，等待系统自动处理...")
        time.sleep(30)  # 给系统一些时间来处理上传的文件
        
        # 获取批量处理结果
        batch_result = self.get_batch_result(batch_id)
        
        if batch_result:
            print(f"批量处理结果: {batch_result}")
            
            # 后处理：生成解析文件
            self.post_process_results(year_dir)
            return True
        else:
            print("无法获取批量处理结果")
            return False

    def get_batch_result(self, batch_id: str) -> Optional[Dict]:
        """
        获取批量任务结果
        
        Args:
            batch_id: 批量任务ID
            
        Returns:
            任务结果，如果获取失败则返回None
        """
        batch_result_url = f"{self.base_url}/extract-results/batch/{batch_id}"
        
        max_attempts = 30  # 最多等待15分钟（30次 × 30秒）
        attempt_count = 0
        
        while attempt_count < max_attempts:
            response = requests.get(batch_result_url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"获取批量任务结果失败: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            if result.get("code") != 0:
                print(f"获取批量任务结果失败: {result}")
                return None
                
            extract_results = result["data"]["extract_result"]
            all_done = True
            
            for item in extract_results:
                state = item["state"]
                print(f"文件 {item['file_name']} 状态: {state}")
                
                if state == "done":
                    if item.get("full_zip_url"):
                        # 下载结果到对应年份目录
                        file_name = item["file_name"]
                        year = self.extract_year_from_filename(file_name)
                        
                        if year:
                            year_dir = self.results_dir / year
                            self.download_and_extract_result(item["full_zip_url"], year_dir)
                            
                elif state in ["pending", "running", "converting", "waiting-file"]:
                    all_done = False
                elif state == "failed":
                    print(f"文件 {item['file_name']} 解析失败: {item.get('err_msg', 'Unknown error')}")
                    
            if all_done:
                print("所有文件处理完成")
                return result["data"]
            
            attempt_count += 1
            print(f"等待批量处理完成... ({attempt_count}/{max_attempts})")
            time.sleep(30)  # 等待30秒后再次查询
        
        print("等待超时，批量任务可能仍在处理中")
        return None
    
    def process_multiple_pdfs(self, pdf_list: List[str], model_version: str = "vlm"):
        """
        批量处理多个PDF文件
        
        Args:
            pdf_list: PDF文件路径列表
            model_version: 模型版本
        """
        for pdf_path in pdf_list:
            if os.path.isfile(pdf_path):
                print(f"\n处理文件: {pdf_path}")
                success = self.process_local_pdf(pdf_path, model_version)
                if success:
                    print(f"成功处理文件: {pdf_path}")
                else:
                    print(f"处理文件失败: {pdf_path}")
            else:
                print(f"文件不存在: {pdf_path}")


def find_all_pdfs(directory: str) -> List[str]:
    """
    递归查找目录中所有PDF文件
    
    Args:
        directory: 要搜索的目录
        
    Returns:
        PDF文件路径列表
    """
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    return pdf_files


def main():
    """
    主函数，演示如何使用PDF处理器
    """
    # 从配置文件加载API令牌
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        api_token = config.get("api_token", "")
    else:
        api_token = input("请输入MinerU API令牌: ")
    
    if not api_token or api_token == "[your_token_here]":
        print("API令牌未设置，请在config.json中设置api_token")
        return
    
    processor = PDFProcessor(api_token)
    
    # 递归查找当前目录及所有子目录下的PDF文件
    pdf_files = find_all_pdfs('.')
    
    # 过滤出包含年份的PDF文件
    pdf_with_years = []
    for pdf_path in pdf_files:
        if processor.extract_year_from_filename(os.path.basename(pdf_path)):
            pdf_with_years.append(pdf_path)
    
    if not pdf_with_years:
        print("未找到包含年份的PDF文件")
        # 尝试列出所有PDF文件供参考
        if pdf_files:
            print(f"当前目录及其子目录的PDF文件: {pdf_files}")
        else:
            print("当前目录及其子目录下没有PDF文件")
        return
    
    print(f"找到包含年份的PDF文件: {len(pdf_with_years)} 个")
    for pdf in pdf_with_years:
        print(f"  - {pdf}")
    
    # 处理所有找到的PDF文件
    processor.process_multiple_pdfs(pdf_with_years)
    
    print("\n所有PDF处理完成！结果已按年份分类保存到'结果文件夹'目录中。")
    print("注意：如需进一步处理题目解析，请运行 convert_to_questions.py 文件。")


if __name__ == "__main__":
    main()