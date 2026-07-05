import requests
import json
import time
import os
from datetime import datetime

class MideaSign:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://mideaai.midea.com"
        self.headers = {
            "User-Agent": "Midea/8.4.0 (iPhone; iOS 15.0; Scale/3.0)",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "zh-Hans-CN;q=1",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
    def login(self, username, password):
        """登录获取token"""
        login_url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password,
            "loginType": "mobile"
        }
        
        try:
            response = self.session.post(login_url, json=data, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    token = result.get("data", {}).get("token")
                    if token:
                        self.headers["Authorization"] = f"Bearer {token}"
                        return True
                print(f"登录失败: {result.get('msg', '未知错误')}")
                return False
            else:
                print(f"登录请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False
    
    def get_user_info(self):
        """获取用户信息"""
        url = f"{self.base_url}/api/user/info"
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data", {})
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def sign_in(self):
        """执行签到"""
        sign_url = f"{self.base_url}/api/sign/in"
        
        try:
            response = self.session.post(sign_url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    data = result.get("data", {})
                    return {
                        "success": True,
                        "points": data.get("points", 0),
                        "message": "签到成功"
                    }
                elif "已签到" in result.get("msg", ""):
                    return {
                        "success": True,
                        "points": 0,
                        "message": "今日已签到"
                    }
                else:
                    return {
                        "success": False,
                        "points": 0,
                        "message": result.get("msg", "签到失败")
                    }
            return {
                "success": False,
                "points": 0,
                "message": f"请求失败: {response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "points": 0,
                "message": f"签到异常: {e}"
            }
    
    def get_sign_status(self):
        """获取签到状态"""
        url = f"{self.base_url}/api/sign/status"
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data", {})
            return None
        except Exception as e:
            print(f"获取签到状态失败: {e}")
            return None

class ServerChan:
    def __init__(self, send_key):
        self.send_key = send_key
        self.url = "https://sctapi.ftqq.com/{send_key}.send"
    
    def send(self, title, content=""):
        """发送通知"""
        if not self.send_key:
            print("Server酱未配置，跳过通知")
            return False
        
        url = self.url.format(send_key=self.send_key)
        data = {
            "title": title,
            "desp": content
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("通知发送成功")
                    return True
                else:
                    print(f"通知发送失败: {result.get('msg', '未知错误')}")
            else:
                print(f"通知请求失败: {response.status_code}")
            return False
        except Exception as e:
            print(f"发送通知异常: {e}")
            return False

def main():
    # 从环境变量获取配置
    username = os.environ.get("MIDEA_USERNAME")
    password = os.environ.get("MIDEA_PASSWORD")
    send_key = os.environ.get("SERVER_CHAN_KEY")
    
    if not username or not password:
        print("错误: 请设置环境变量 MIDEA_USERNAME 和 MIDEA_PASSWORD")
        return
    
    # 创建签到实例
    sign = MideaSign()
    server = ServerChan(send_key)
    
    # 记录日志
    log_lines = []
    log_lines.append(f"========== 签到执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========")
    
    # 登录
    print("正在登录...")
    if not sign.login(username, password):
        log_lines.append("❌ 登录失败，请检查用户名和密码")
        server.send("美的签到失败", "\n".join(log_lines))
        return
    
    log_lines.append("✅ 登录成功")
    
    # 获取用户信息
    user_info = sign.get_user_info()
    if user_info:
        nickname = user_info.get("nickname", "用户")
        level = user_info.get("level", "0")
        log_lines.append(f"👤 用户: {nickname}")
        log_lines.append(f"📊 等级: {level}")
    
    # 获取签到状态
    status = sign.get_sign_status()
    if status:
        days = status.get("consecutiveDays", 0)
        log_lines.append(f"📅 已连续签到: {days}天")
    
    # 执行签到
    print("正在签到...")
    result = sign.sign_in()
    
    if result["success"]:
        points = result["points"]
        msg = result["message"]
        log_lines.append(f"✅ {msg}")
        if points > 0:
            log_lines.append(f"💎 获得 {points} 积分")
        log_lines.append(f"📝 状态: {msg}")
    else:
        log_lines.append(f"❌ {result['message']}")
    
    # 构建通知内容
    content = "\n".join(log_lines)
    print(content)
    
    # 发送通知
    if result["success"]:
        title = "美的签到成功" if result["points"] > 0 else "美的签到完成"
    else:
        title = "美的签到失败"
    
    server.send(title, content)

if __name__ == "__main__":
    main()
