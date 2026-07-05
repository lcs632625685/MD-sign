import requests
import os
import json
from datetime import datetime

class MideaSign:
    def __init__(self):
        self.base_url = "https://mcsp-api.midea.com"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "appId": "ee07f27990db48109efcccd322d3a873",
            "appsecret": "2646746f07bb46199aff49002e6dce81",
            "miniAppVersion": "3.0.323",
            "ucAccessToken": os.environ.get("UC_ACCESS_TOKEN", "5f7bff39c2f7f9717c10abd65ad7db365d4673d7581b69e54a038cbfa91e4b9c"),
            "userKey": os.environ.get("USER_KEY", "5f7bff39c2f7f9717c10abd65ad7db365d4673d7581b69e54a038cbfa91e4b9c"),
            "Referer": "https://servicewechat.com/wx49a622805968d156/558/page-frame.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 MicroMessenger/7.0.20.1781(0x6700143B)"
        }

    def sign_in(self):
        """执行签到"""
        url = f"{self.base_url}/api/cms_api/activity-center-im-service/im-svr/im/game/page/sign?apikey=b6db9d5cf2d449538d3a0dd5d77b2e35"
        data = {
            "restParams": {
                "gameId": "28",
                "actvId": "401670810827462661",
                "rootCode": "DJ",
                "appCode": "DJ_WX"
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            result = response.json()
            
            if result.get("code") == "000000":
                data = result.get("data", {})
                daily_reward = data.get("dailyRewardInfo")
                
                # 如果签到过了，dailyRewardInfo 为 null
                if data.get("result") == False:
                    return {
                        "success": True,
                        "points": 0,
                        "message": "今日已签到",
                        "raw": result
                    }
                
                # 签到成功，获取积分
                if daily_reward:
                    points = daily_reward.get("points", "0")
                    return {
                        "success": True,
                        "points": int(points),
                        "message": "签到成功",
                        "raw": result
                    }
                else:
                    return {
                        "success": True,
                        "points": 0,
                        "message": "签到成功，但未获得积分",
                        "raw": result
                    }
            else:
                return {
                    "success": False,
                    "message": result.get("msg", "签到失败"),
                    "raw": result
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求异常: {e}",
                "raw": None
            }

    def get_sign_status(self):
        """获取签到状态"""
        url = f"{self.base_url}/api/cms_api/activity-center-im-service/im-svr/cmimp/activity/initData?apikey=b6db9d5cf2d449538d3a0dd5d77b2e35"
        data = {
            "restParams": {
                "actvId": "401670810827462661",
                "rootCode": "DJ",
                "appCode": "DJ_WX",
                "userType": 1,
                "openId": "oXZrx5EavI_VsHpzvue-Ub_BUGzU",
                "templateId": "2",
                "channelId": "401670810907154451",
                "wasLogin": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            result = response.json()
            if result.get("code") == "000000":
                data = result.get("data", [])
                if data and len(data) > 0:
                    sign_data = data[0]
                    return {
                        "success": True,
                        "total_score": sign_data.get("totalScore", 0),
                        "signed_days": sign_data.get("signedDays", "0"),
                        "raw": result
                    }
            return {"success": False, "message": "获取状态失败"}
        except Exception as e:
            return {"success": False, "message": f"获取状态异常: {e}"}

class ServerChan:
    def __init__(self, send_key):
        self.send_key = send_key
        self.url = "https://sctapi.ftqq.com/{send_key}.send"
    
    def send(self, title, content=""):
        if not self.send_key:
            print("Server酱未配置，跳过通知")
            return False
        
        url = self.url.format(send_key=self.send_key)
        data = {"title": title, "desp": content}
        
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("通知发送成功")
                    return True
            return False
        except Exception as e:
            print(f"发送通知异常: {e}")
            return False

def main():
    print(f"========== 签到执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========")
    
    # 从环境变量获取配置
    uc_token = os.environ.get("UC_ACCESS_TOKEN", "5f7bff39c2f7f9717c10abd65ad7db365d4673d7581b69e54a038cbfa91e4b9c")
    user_key = os.environ.get("USER_KEY", "5f7bff39c2f7f9717c10abd65ad7db365d4673d7581b69e54a038cbfa91e4b9c")
    send_key = os.environ.get("SERVER_CHAN_KEY")
    
    sign = MideaSign()
    server = ServerChan(send_key)
    
    log_lines = []
    
    # 获取签到状态
    print("获取签到状态...")
    status = sign.get_sign_status()
    if status["success"]:
        log_lines.append(f"📊 当前积分: {status['total_score']}")
        log_lines.append(f"📅 已签到天数: {status['signed_days']}")
        print(f"当前积分: {status['total_score']}")
        print(f"已签到天数: {status['signed_days']}")
    
    # 执行签到
    print("\n执行签到...")
    result = sign.sign_in()
    
    if result["success"]:
        if result["points"] > 0:
            log_lines.append(f"✅ 签到成功！获得 {result['points']} 积分")
            print(f"签到成功！获得 {result['points']} 积分")
            title = f"美的签到成功 +{result['points']}积分"
        else:
            log_lines.append(f"📝 {result['message']}")
            print(f"{result['message']}")
            title = "美的签到完成"
    else:
        log_lines.append(f"❌ {result['message']}")
        print(f"签到失败: {result['message']}")
        title = "美的签到失败"
    
    # 发送通知
    content = "\n".join(log_lines)
    server.send(title, content)

if __name__ == "__main__":
    main()
