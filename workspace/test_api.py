import os
import json
import requests
from typing import Dict, Optional


class QwenAPIClient:
    """
    通义千问API客户端，兼容OpenAI接口
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL
            token: 认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json',
        }
        
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def chat_completion(self, 
                       messages: list, 
                       model: str = "qwen", 
                       stream: bool = False, 
                       conversation_id: str = None) -> Dict:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            stream: 是否流式返回
            conversation_id: 对话ID
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return {}
    
    def image_generation(self, prompt: str, model: str = "wanxiang") -> Dict:
        """
        图像生成接口
        
        Args:
            prompt: 提示文本
            model: 模型名称
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/v1/images/generations"
        
        payload = {
            "model": model,
            "prompt": prompt
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return {}
    
    def document_interpretation(self, file_url: str, question: str, model: str = "qwen") -> Dict:
        """
        文档解读接口
        
        Args:
            file_url: 文件URL
            question: 问题
            model: 模型名称
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": file_url
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return {}
    
    def image_interpretation(self, image_url: str, question: str, model: str = "qwen") -> Dict:
        """
        图像解读接口
        
        Args:
            image_url: 图像URL
            question: 问题
            model: 模型名称
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return {}
    
    def check_token(self, token: str) -> Dict:
        """
        检查token是否存活
        
        Args:
            token: 要检查的token
        
        Returns:
            API响应结果
        """
        url = f"{self.base_url}/token/check"
        
        payload = {
            "token": token
        }
        
        # 临时使用检查的token
        temp_headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, headers=temp_headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            return {}


def load_config(config_path: str = "config.json") -> dict:
    """
    从配置文件加载API参数
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典
    """
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"配置文件 {config_path} 不存在，使用默认值")
        return {}


def main():
    """
    主函数，演示各种API调用
    """
    # 尝试从配置文件加载设置
    config = load_config()
    
    # 优先使用环境变量，其次使用配置文件，最后使用默认值
    api_base_url = os.getenv("QWEN_API_BASE", 
                             config.get("api_base_url", "http://localhost:8000"))
    api_token = os.getenv("QWEN_API_TOKEN", 
                          config.get("api_token", ""))
    default_model = config.get("default_model", "qwen")
    default_image_model = config.get("default_image_model", "wanxiang")
    
    client = QwenAPIClient(base_url=api_base_url, token=api_token)
    
    print("=== 通义千问API测试 ===\n")
    
    # 测试聊天完成
    print("1. 测试聊天完成:")
    try:
        messages = [
            {"role": "user", "content": "你好，你是谁？"}
        ]
        response = client.chat_completion(messages, model=default_model)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试图像生成
    print("2. 测试图像生成:")
    try:
        response = client.image_generation("一只可爱的猫", model=default_image_model)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试文档解读
    print("3. 测试文档解读:")
    try:
        # 使用示例文档URL
        doc_url = "https://mj101-1317487292.cos.ap-shanghai.myqcloud.com/ai/test.pdf"
        question = "文档里说了什么？"
        response = client.document_interpretation(doc_url, question, model=default_model)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试图像解读
    print("4. 测试图像解读:")
    try:
        # 使用示例图像URL
        img_url = "https://img.alicdn.com/imgextra/i1/O1CN01CC9kic1ig1r4sAY5d_!!6000000004441-2-tps-880-210.png"
        question = "图像描述了什么？"
        response = client.image_interpretation(img_url, question, model=default_model)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试token检查（仅当设置了token时）
    if api_token and api_token != "[your_token_here]":
        print("5. 测试Token检查:")
        try:
            response = client.check_token(api_token)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"错误: {e}")

    print("\n所有测试已完成！")


if __name__ == "__main__":
    main()