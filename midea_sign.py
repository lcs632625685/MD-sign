import requests
import os
import json
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

        return {
            "success": False,
            "message": result.get("msg", "获取失败")
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"请求异常: {e}"
        }


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
        return {
            "error": str(e)
        }


def send_notification(title, content):
    """发送 PushPlus 通知"""
    pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
    pushplus_topic = os.environ.get("PUSHPLUS_TOPIC")

    if not pushplus_token:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过通知")
        return

    url = "https://www.pushplus.plus/send"

    data = {
        "token": pushplus_token,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    if pushplus_topic:
        data["topic"] = pushplus_topic

    try:
        response = requests.post(url, json=data, timeout=15)
        print(f"✅ PushPlus 推送请求已发送，状态码: {response.status_code}")

        try:
            result = response.json()
            print(f"🔍 PushPlus 返回: {json.dumps(result, ensure_ascii=False)}")

            if result.get("code") == 200:
                print("✅ PushPlus 推送成功")
            else:
                print(f"❌ PushPlus 推送失败: {result.get('msg', '未知错误')}")
        except Exception:
            print(f"🔍 PushPlus 原始返回: {response.text}")

    except Exception as e:
        print(f"❌ PushPlus 通知发送失败: {e}")


def main():
    uc_token = os.environ.get("UC_ACCESS_TOKEN")
    user_key = os.environ.get("USER_KEY")

    print(f"DEBUG: PUSHPLUS_TOKEN = {os.environ.get('PUSHPLUS_TOKEN')[:10] + '...' if os.environ.get('PUSHPLUS_TOKEN') else 'None'}")
    print(f"DEBUG: PUSHPLUS_TOPIC = {os.environ.get('PUSHPLUS_TOPIC') if os.environ.get('PUSHPLUS_TOPIC') else 'None'}")

    if not uc_token or not user_key:
        print("❌ 错误: 未配置 UC_ACCESS_TOKEN 或 USER_KEY")
        print("请在 GitHub Secrets 中添加这两个变量")

        send_notification(
            "美的签到失败",
            "❌ 未配置 `UC_ACCESS_TOKEN` 或 `USER_KEY`，请检查 GitHub Secrets。"
        )
        return

    print(f"========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========")
    print(f"UC_ACCESS_TOKEN: {uc_token[:20]}...")

    # 获取签到前积分
    print("\n📊 获取当前积分...")
    before_info = get_user_info()

    if before_info.get("success"):
        before_points = before_info.get("points", 0)
        nickname = before_info.get("nickname", "")
        level = before_info.get("level", "")
        mfans_level = before_info.get("mfans_level", "")

        print(f"当前积分: {before_points}")
        print(f"昵称: {nickname}")
        print(f"等级: {level}")
        print(f"美粉等级: {mfans_level}")
    else:
        before_points = 0
        nickname = ""
        level = ""
        mfans_level = ""

        print(f"⚠️ 获取积分失败: {before_info.get('message', '')}")

    # 执行签到
    print("\n✅ 执行签到...")
    result = sign_in()

    if "error" in result:
        print(f"❌ 请求失败: {result['error']}")

        send_notification(
            "美的签到失败",
            f"## 美的签到失败\n\n"
            f"❌ 请求异常：{result['error']}"
        )
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

        base_info = (
            f"## 美的家居签到结果\n\n"
            f"昵称：{nickname if nickname else '未获取'}\n\n"
            f"等级：{level if level else '未获取'}\n\n"
            f"美粉等级：{mfans_level if mfans_level else '未获取'}\n\n"
            f"签到前积分：{before_points}\n\n"
            f"当前积分：{after_points}\n\n"
        )

        if data.get("result") is False:
            msg = (
                f"{base_info}"
                f"签到状态：今日已签到\n\n"
                f"积分变化：{points_change}"
            )

            print(f"📝 今日已签到\n当前积分: {after_points}")
            send_notification("美的签到完成", msg)

        elif daily_reward:
            reward_points = int(daily_reward.get("points", "0"))

            msg = (
                f"{base_info}"
                f"签到状态：签到成功\n\n"
                f"签到奖励：+{reward_points} 积分\n\n"
                f"实际积分变化：+{points_change}"
            )

            print(f"✅ 签到成功！获得 {reward_points} 积分")
            print(f"当前积分: {after_points}")
            print(f"今日获得: +{points_change}")

            send_notification(f"美的签到成功 +{reward_points}积分", msg)

        else:
            msg = (
                f"{base_info}"
                f"签到状态：签到成功\n\n"
                f"积分变化：+{points_change}"
            )

            print(f"✅ 签到成功\n当前积分: {after_points}")
            send_notification("美的签到完成", msg)

    else:
        msg = result.get("msg", "签到失败")

        print(f"❌ {msg}")

        send_notification(
            "美的签到失败",
            f"## 美的家居签到失败\n\n"
            f"错误码：{code}\n\n"
            f"错误信息：{msg}"
        )


if __name__ == "__main__":
    main()
