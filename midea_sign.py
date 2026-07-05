import requests
import os
from datetime import datetime

def get_user_info():
    """获取用户信息（包含当前积分）"""
    url = "https://mcsp.midea.com/api/mcsp_cms/mcsp-cmshop-bff-app/user/getMemberInfo"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "apikey": "b6db9d5cf2d449538d3a0dd5d77b2e35",
        "appId": "ee07f27990db48109efcccd322d3a873",
        "appsecret": "2646746f07bb46199aff49002e6dce81",
        "miniAppVersion": "3.0.323",
        "ucAccessToken": os.environ.get("UC_ACCESS_TOKEN", ""),
        "userKey": os.environ.get("USER_KEY", ""),
        "Referer": "https://servicewechat.com/wx49a622805968d156/558/page-frame.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    data = {
        "headParams": {
            "language": "CN",
            "originSystem": "cms-app-mini",
            "timeZone": "8",
            "userType": "C",
            "tenantCode": "",
            "userKey": os.environ.get("USER_KEY", ""),
            "sign": "e02ac436de344f729498263395de1dba17832414471810de1177c77524a7f965a36cf09d21345",
            "timestamp": "1783241447181",
            "miniAppVersion": "3.0.323",
            "transactionId": "14471810.834292307382517"
        },
        "restParams": {
            "brand": 1,
            "userId": "",
            "mobile": "",
            "openId": "oXZrx5EavI_VsHpzvue-Ub_BUGzU",
            "_timeStamp": 1783241447161
        },
        "pagination": {}
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        result = response.json()
        if result.get("code") == "000000":
            data = result.get("data", {})
            return {
                "success": True,
                "points": int(data.get("vipPoint", "0")),
                "level": data.get("levelName", ""),
                "nickname": data.get("userCustomize", {}).get("nickName", ""),
                "mfans_level": data.get("mfansLevelName", "")
            }
        return {"success": False, "message": result.get("msg", "获取失败")}
    except Exception as e:
        return {"success": False, "message": f"请求异常: {e}"}

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
    
    # 获取签到前积分
    print("\n📊 获取当前积分...")
    before_info = get_user_info()
    
    if before_info.get("success"):
        before_points = before_info.get("points", 0)
        print(f"当前积分: {before_points}")
        print(f"昵称: {before_info.get('nickname', '')}")
        print(f"等级: {before_info.get('level', '')}")
        print(f"美粉等级: {before_info.get('mfans_level', '')}")
    else:
        before_points = 0
        print(f"⚠️ 获取积分失败: {before_info.get('message', '')}")
    
    # 执行签到
    print("\n✅ 执行签到...")
    result = sign_in()
    
    if "error" in result:
        print(f"❌ 请求失败: {result['error']}")
        send_notification("美的签到失败", f"请求异常: {result['error']}")
        return
    
    print(f"响应码: {result.get('code')}")
    
    code = result.get("code")
    if code == "000000":
        data = result.get("data", {})
        daily_reward = data.get("dailyRewardInfo")
        
        # 获取签到后积分
        print("\n📊 获取最新积分...")
        after_info = get_user_info()
        after_points = after_info.get("points", before_points) if after_info.get("success") else before_points
        
        points_change = after_points - before_points
        
        if data.get("result") == False:
            msg = f"今日已签到\n当前积分: {after_points}"
            print(f"📝 {msg}")
            send_notification("美的签到完成", msg)
        elif daily_reward:
            reward_points = int(daily_reward.get("points", "0"))
            msg = f"签到成功！获得 {reward_points} 积分\n当前积分: {after_points}\n今日获得: +{points_change}"
            print(f"✅ {msg}")
            send_notification(f"美的签到成功 +{reward_points}积分", msg)
        else:
            msg = f"签到成功\n当前积分: {after_points}"
            print(f"✅ {msg}")
            send_notification("美的签到完成", msg)
    else:
        msg = result.get("msg", "签到失败")
        print(f"❌ {msg}")
        send_notification("美的签到失败", f"错误码: {code}\n信息: {msg}")

if __name__ == "__main__":
    main()
