from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 关键改动1：创建一个全局的对话历史列表
messages = [
    {"role": "system", "content": "你是一个友好的AI助手，正在帮助用户学习AI Agent开发。"}
]

def chat_with_ai(user_message):
    # 关键改动2：把用户的新消息添加到对话历史中
    messages.append({"role": "user", "content": user_message})
    
    # 调用API时传入完整的对话历史
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7
    )
    
    ai_response = response.choices[0].message.content
    
    # 关键改动3：把AI的回复也添加到对话历史中
    messages.append({"role": "assistant", "content": ai_response})
    
    return ai_response

if __name__ == "__main__":
    print("🤖 多轮对话AI助手已启动！输入'退出'结束对话。")
    
    while True:
        user_input = input("\n你：")
        
        if user_input == "退出":
            print("🤖 再见！祝你学习愉快！")
            break
        
        ai_response = chat_with_ai(user_input)
        print(f"🤖 AI：{ai_response}")