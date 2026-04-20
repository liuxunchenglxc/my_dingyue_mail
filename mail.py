import sys
import argparse
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import random

import gzip
import io

def get_subscribe_url(auth_token):
    url = "https://feiniaoyun.xyz/api/v1/user/getSubscribe"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://feiniaoyun.xyz/",
        "authorization": auth_token,
        "Content-Language": "zh-CN",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.getcode()
            resp_headers = response.info()
            encoding = resp_headers.get('Content-Encoding')
            print(f"[*] 响应状态码: {status_code}")
            print(f"[*] 响应编码格式: {encoding}")
            
            raw_data = response.read()
            print(f"[*] 读取到的原始字节数: {len(raw_data)}")
            
            # 处理解压缩逻辑
            content = ""
            if encoding == 'gzip':
                try:
                    content = gzip.decompress(raw_data).decode('utf-8')
                    print("[+] Gzip 解压成功")
                except Exception as ge:
                    print(f"[-] Gzip 解压失败: {ge}")
            elif encoding == 'deflate':
                try:
                    content = zlib.decompress(raw_data).decode('utf-8')
                    print("[+] Deflate 解压成功")
                except Exception as de:
                    print(f"[-] Deflate 解压失败: {de}")
            else:
                content = raw_data.decode('utf-8', errors='ignore')
                print("[!] 未检测到已知压缩格式，尝试直接解码")

            # 4. 解析 JSON
            res_data = json.loads(content)
            sub_url = res_data.get("data", {}).get("subscribe_url")
            return sub_url, True
            
    except Exception as e:
        if hasattr(e, 'read'):
            try:
                err_body = e.read().decode()
                return f"HTTP错误喵: {e.code} - {err_body}", False
            except:
                pass
        return f"请求异常喵: {str(e)}", False

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
