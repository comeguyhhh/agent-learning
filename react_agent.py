from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from duckduckgo_search import DDGS

# 加载环境变量
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# ===================== 1. 定义工具函数 =====================
def web_search(query):
    """搜索互联网信息"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        
        result_text = ""
        for i, res in enumerate(results):
            result_text += f"【结果{i+1}】标题：{res['title']}\n内容：{res['body']}\n\n"
        
        return result_text.strip()
    except Exception as e:
        return f"搜索失败：{str(e)}"

# ===================== 2. 工具描述 =====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "搜索互联网上的实时信息，适合查询新闻、天气、数据、常识等未知内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，越精准越好"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ===================== 3. 系统提示词（ReAct核心指令） =====================
system_prompt = """
你是一个聪明的ReAct智能助手。你可以调用搜索工具来获取互联网上的信息。

请严格按照以下流程解决问题：
1. 先思考当前已知的信息和下一步需要做什么
2. 如果需要获取信息，就调用搜索工具
3. 收到工具返回的结果后，继续思考
4. 当信息足够时，给出最终答案

回答时请清晰区分思考过程和最终答案。
"""

# 对话历史
messages = [
    {"role": "system", "content": system_prompt}
]

# ===================== 4. ReAct核心逻辑 =====================
def react_chat(user_message, max_steps=5):
    """
    ReAct模式聊天，支持多轮工具调用
    max_steps: 最大调用工具次数，防止无限循环
    """
    # 把用户问题加入对话
    messages.append({"role": "user", "content": user_message})
    
    for step in range(max_steps):
        print(f"\n--- 第 {step+1} 步思考中 ---")
        
        # 调用大模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # 判断：大模型要不要调用工具？
        if response_message.tool_calls:
            # 把大模型的思考加入对话历史
            messages.append(response_message)
            
            # 遍历所有要调用的工具
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"💡 决定调用工具：{function_name}")
                print(f"🔍 搜索关键词：{function_args['query']}")
                
                # 执行工具
                if function_name == "web_search":
                    observation = web_search(function_args["query"])
                
                print(f"📋 搜索结果：\n{observation[:200]}...") # 只打印前200字
                
                # 把工具返回的结果加入对话历史
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": observation
                    }
                )
        else:
            # 不需要调用工具了，给出最终答案
            final_answer = response_message.content
            messages.append({"role": "assistant", "content": final_answer})
            return final_answer
    
    # 超过最大步数，强制返回
    return "抱歉，我尝试了多次仍然无法解决你的问题，请换一种问法试试。"

# ===================== 5. 主程序 =====================
if __name__ == "__main__":
    print("🤖 ReAct搜索智能助手已启动！")
    print("我可以自主搜索互联网信息来回答你的问题，输入'退出'结束。\n")
    
    while True:
        user_input = input("你：")
        
        if user_input == "退出":
            print("🤖 再见！")
            break
        
        answer = react_chat(user_input)
        print(f"\n✅ 最终答案：\n{answer}\n")
        print("="*50)