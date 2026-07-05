import requests
import os
from datetime import datetime

def sign_in():
    """执行签到"""
    url = "https://mcsp-api.midea.com/api/cms_api/activity-center-im-service/im-svr/im/game/page/sign?apikey=b6db9d5cf2d449538d3a0dd5d77b2e35"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "appId": "ee07f27990db48109efcccd322d3a873",
        "appsecret": "2646746f07bb46199aff49002e6dce81",
        "miniAppVersion": "3.0.323",
        "ucAccessToken": os.environ.get("UC_ACCESS_TOKEN", ""),
        "userKey": os.environ.get("USER_KEY", ""),
        "Referer": "https://servicewechat.com/wx49a622805968d156/558/page-frame.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    data = {
        "restParams": {
            "gameId": "28",
            "actvId": "401670810827462661",
            "rootCode": "DJ",
            "appCode": "DJ_WX"
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        result = response.json()
        return result
    except Exception as e:
        return {"error": str(e)}

def send_notification(title, content):
    """发送Server酱通知"""
    send_key = os.environ.get("SERVER_CHAN_KEY")
    if not send_key:
        print("未配置SERVER_CHAN_KEY，跳过通知")
        return
    
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    try:
        requests.post(url, data={"title": title, "desp": content}, timeout=10)
    except Exception as e:
        print(f"通知发送失败: {e}")

def main():
    # 检查Token
    uc_token = os.environ.get("UC_ACCESS_TOKEN")
    user_key = os.environ.get("USER_KEY")
    
    if not uc_token or not user_key:
        print("❌ 错误: 未配置 UC_ACCESS_TOKEN 或 USER_KEY")
        print("请在 GitHub Secrets 中添加这两个变量")
        return
    
    print(f"========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========")
    print(f"UC_ACCESS_TOKEN: {uc_token[:20]}...")
    
    # 执行签到
    print("执行签到...")
    result = sign_in()
    
    if "error" in result:
        print(f"❌ 请求失败: {result['error']}")
        send_notification("美的签到失败", f"请求异常: {result['error']}")
        return
    
    print(f"响应: {result}")
    
    code = result.get("code")
    if code == "000000":
        data = result.get("data", {})
        daily_reward = data.get("dailyRewardInfo")
        
        if data.get("result") == False:
            msg = "今日已签到"
            print(f"📝 {msg}")
            send_notification("美的签到完成", msg)
        elif daily_reward:
            points = daily_reward.get("points", "0")
            msg = f"签到成功！获得 {points} 积分"
            print(f"✅ {msg}")
            send_notification(f"美的签到成功 +{points}积分", msg)
        else:
            msg = "签到成功"
            print(f"✅ {msg}")
            send_notification("美的签到完成", msg)
    else:
        msg = result.get("msg", "签到失败")
        print(f"❌ {msg}")
        send_notification("美的签到失败", f"错误码: {code}\n信息: {msg}")

if __name__ == "__main__":
    main()
