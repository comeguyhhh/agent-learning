from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 第一步：定义我们的工具函数（计算器）
def calculate(a, b, operator):
    """
    执行两个数的加减乘除运算
    参数：
        a: 第一个数
        b: 第二个数
        operator: 运算符，只能是+、-、*、/
    返回：
        计算结果
    """
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return a / b
    else:
        return "不支持的运算符"

# 第二步：把函数描述成大模型能理解的JSON格式
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行两个数的加减乘除运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数"
                    },
                    "operator": {
                        "type": "string",
                        "description": "运算符，只能是+、-、*、/",
                        "enum": ["+", "-", "*", "/"]
                    }
                },
                "required": ["a", "b", "operator"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "你是一个聪明的AI助手。当用户问你数学问题时，不要自己计算，一定要调用calculate工具来计算。"}
]

def chat_with_ai(user_message):
    messages.append({"role": "user", "content": user_message})
    
    # 第三步：调用API时传入tools参数
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # 第四步：判断大模型是否想要调用函数
    if response_message.tool_calls:
        # 遍历所有要调用的函数
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # 第五步：执行对应的函数
            if function_name == "calculate":
                result = calculate(
                    a=function_args["a"],
                    b=function_args["b"],
                    operator=function_args["operator"]
                )
            
            # 第六步：把函数执行结果返回给大模型
            messages.append(response_message)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result)
                }
            )
        
        # 第七步：再次调用API，让大模型根据函数结果生成最终回复
        second_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        final_response = second_response.choices[0].message.content
        messages.append({"role": "assistant", "content": final_response})
        return final_response
    else:
        # 如果不需要调用函数，直接返回大模型的回复
        messages.append(response_message)
        return response_message.content

if __name__ == "__main__":
    print("🤖 计算器AI Agent已启动！输入'退出'结束对话。")
    print("你可以问我任何数学问题，我会用计算器帮你精确计算！")
    
    while True:
        user_input = input("\n你：")
        
        if user_input == "退出":
            print("🤖 再见！祝你学习愉快！")
            break
        
        ai_response = chat_with_ai(user_input)
        print(f"🤖 AI：{ai_response}")