import sys
import argparse
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random

def get_subscribe_url(auth_token):
    url = "https://feiniaoyun.xyz"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "authorization": auth_token,
        "Referer": "https://feiniaoyun.xyz",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            return res_data.get("data", {}).get("subscribe_url"), True
    except Exception as e:
        print(f"API请求异常: {e}")
        return f"{e}", False

def send_email(sub_url, status, args):
    prefix = random.choice(["呜喵！", "主人主人！", "喵呜~", "报告主人！"])
    suffix = random.choice(["要好好使用喵~", "这是人家的努力成果喵！", "喵喵喵~"])

    if status:
        subject_text = f"主人的飞鸟云订阅更新成功了喵！"
        body_content = (
            f"{prefix}\n\n"
            f"人家已经帮主人把飞鸟云的订阅链接取回来啦喵！\n"
            f"链接就在下面，请主人查收喵：\n\n"
            f"{sub_url}\n\n"
            f"{suffix}"
        )
    else:
        subject_text = f"呜呜...飞鸟云订阅更新出错了喵..."
        body_content = (
            f"对不起主人喵...人家没能拿到链接...\n"
            f"报错信息是这个喵：\n{sub_url}\n"
            f"主人快去检查一下设置喵！"
        )
  
    from_str = f'"{args.from_name}" <{args.user}>'

    msg = MIMEText(body_content, 'plain', 'utf-8')
    msg['From'] = from_str
    msg['To'] = args.to_user
    msg['Subject'] = Header(subject_text, 'utf-8')

    try:
        with smtplib.SMTP(args.addr, int(args.port)) as server:
            server.login(args.user, args.passwd)
            server.sendmail(args.user, [args.to_user], msg.as_string())
        print("[+] 邮件通知已成功发送。")
    except Exception as e:
        print(f"[-] 邮件发送失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="飞鸟云订阅获取脚本")
    parser.add_argument("--token", required=True, help="Auth Token")
    parser.add_argument("--user", required=True, help="SMTP 用户邮箱")
    parser.add_argument("--passwd", required=True, help="SMTP 授权码")
    parser.add_argument("--addr", default="smtp.163.com", help="SMTP 服务器地址")
    parser.add_argument("--port", default="25", help="SMTP 端口")
    parser.add_argument("--from-name", default="Github Action", help="发件人显示名称")
    parser.add_argument("--to-user", required=True, help="收件人邮箱")
    
    args = parser.parse_args()

    url, status = get_subscribe_url(args.token)
    send_email(url, status, args)
