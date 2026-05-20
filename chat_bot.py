# 导入所需的库
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载.env文件中的环境变量
load_dotenv()

# 初始化DeepSeek客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 定义聊天函数
def chat_with_ai(user_message):
    # 调用DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个友好的AI助手，正在帮助用户学习AI Agent开发。"},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )
    
    # 返回AI的回复
    return response.choices[0].message.content

# 主程序
if __name__ == "__main__":
    print("🤖 AI聊天助手已启动！输入'退出'结束对话。")
    
    while True:
        # 获取用户输入
        user_input = input("\n你：")
        
        # 如果用户输入"退出"，结束程序
        if user_input == "退出":
            print("🤖 再见！祝你学习愉快！")
            break
        
        # 调用聊天函数，获取AI回复
        ai_response = chat_with_ai(user_input)
        
        # 打印AI回复
        print(f"🤖 AI：{ai_response}")