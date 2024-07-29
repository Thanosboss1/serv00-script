import os
import json
import subprocess
import requests

def send_telegram_message(token, chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": '{"inline_keyboard":[[{"text":"问题反馈❓","url":"https://t.me/yxjsjl"}]]}'
    }

    response = requests.post(telegram_url, json=telegram_payload)
    print(f"Telegram 请求状态码：{response.status_code}")
    print(f"Telegram 请求返回内容：{response.text}")

    if response.status_code != 200:
        print("发送 Telegram 消息失败")
    else:
        print("发送 Telegram 消息成功")

# 从环境变量中获取密钥
accounts_json = os.getenv('ACCOUNTS_JSON')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 检查并解析 JSON 字符串
try:
    servers = json.loads(accounts_json)
except json.JSONDecodeError:
    error_message = "ACCOUNTS_JSON 参数格式错误"
    print(error_message)
    send_telegram_message(telegram_token, telegram_chat_id, error_message)
    exit(1)

# 初始化计数器和失败列表
success_count = 0
failure_count = 0
failure_details = []

# 默认恢复命令
default_restore_command = "~/.npm-global/bin/pm2 resurrect"

# 遍历服务器列表并执行恢复操作
for server in servers:
    host = server['host']
    port = server['port']
    username = server['username']
    password = server['password']
    cron_command = server.get('cron', default_restore_command)

    print(f"连接到 {host}...")

    # 执行恢复命令（这里假设使用 SSH 连接和密码认证）
    restore_command = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {username}@{host} '{cron_command}'"
    try:
        output = subprocess.check_output(restore_command, shell=True, stderr=subprocess.STDOUT)
        success_count += 1
    except subprocess.CalledProcessError as e:
        failure_count += 1
        failure_details.append(host)

# 构建汇总消息
summary_message = (
    f"serv00-vless 恢复操作结果：\n\n"
    f"成功恢复的服务器数量：{success_count}\n"
    f"无法恢复的服务器数量：{failure_count}\n"
)

if failure_count > 0:
    summary_message += f"无法恢复的服务器ID：\n" + "\n".join(failure_details)

# 发送汇总消息到 Telegram
send_telegram_message(telegram_token, telegram_chat_id, summary_message)
