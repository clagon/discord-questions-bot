import requests
import os

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

STATE = {
	"ask": {
		"type": "rich",
		"title": f"__質問__",
		"color": 0x00ffff,
		"fields": [
			{
				"name": "回答を送信するには..",
				"value":"このメッセージを長押し(右クリック)して\n`アプリ->answer`を選択してください。"
			}
		]
		},
	"answer": {
		"type": "rich",
		"title": f"__回答__",
		"color": 0xff00ff,
		"fields": []
		},
	}
headers = {
		"Authorization": f"Bot {DISCORD_BOT_TOKEN}"
	}
def send_embed(mode: int, message: str,  channel_id: str, reply_id: str=None) -> int:
	url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

	if mode not in STATE.keys():
		return 1
	payload = dict()
	payload["allowed_mentions"] = {"replied_user": False}
	if reply_id is not None:
		payload["message_reference"] = {"message_id": reply_id}
	payload["embeds"] = []
	payload["embeds"].append(STATE[mode])
	payload["embeds"][0]["description"] = f"**{message}**"
	if mode == "answer":
		ref = get_message(channel_id, reply_id)
		if ref:
			payload["embeds"][0]["fields"].append({
				"name": "質問",
				"value": f'```{ref.json()["embeds"][0]["description"][2:1000]}```'
			})
		payload["embeds"][0]["fields"].append(
			{
				"name": "",
				"value": f"[質問のリンク](https://discord.com/channels/{GUILD_ID}/{channel_id}/{reply_id})"
			}
		)

	r = requests.post(url, headers=headers, json=payload)
	return r.status_code

def get_message(channel_id: str, message_id: str) -> dict:
	url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}"
	r = requests.get(url, headers=headers)
	return r

