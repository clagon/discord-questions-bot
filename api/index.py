from flask import Flask, abort, jsonify, request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
import os
from utils import send_embed

from static import COMMAND_IDs

app = Flask(__name__)
PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")


@app.route("/api/interactions", methods=["POST"])
def interactions():
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    message = timestamp.encode() + request.data
    try:
        verify_key.verify(message, bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, "Incorrect Signature")

    content = request.json

    data = content.get("data", {})

    # ping
    if content["type"] == 1:
        return jsonify({
            "type": 1
        })

    if data.get("id"):
        id = data["id"]
        if id == COMMAND_IDs["ask"]:
            return jsonify(
                {
                    "type": 9,
                    "data": {
                        "custom_id": "askmodal",
                        "title": "質問をする",
                        "components": [
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 4,
                                        "custom_id": "asktext",
                                        "style": 2,
                                        "label": "質問をする",
                                        "placeholder": "質問を入力",
                                        "min_length": 1,
                                    }
                                ]
                            }
                        ]
                    }
                }
            )

        elif id == COMMAND_IDs["answer"]:
            embeds = tuple(data["resolved"]["messages"].values())[0]["embeds"]
            embeds = embeds if len(embeds) != 0 else [{"color": 0}]
            isquestion = embeds[0]["color"] == 65535
            if not isquestion:
                return jsonify({
                    "type": 4,
                    "data": {
                        "content": "error: not a question",
                        "flags": 64,
                    }
                })

            else:
                message = embeds[0]["description"][2:-2]
                return jsonify(
                    {
                        "type": 9,
                        "data": {
                            "custom_id": "answermodal",
                            "title": "回答する",
                            "components": [
                                {
                                    "type": 1,
                                    "components": [
                                        {
                                            "type": 4,
                                            "custom_id": "answertext",
                                            "style": 2,
                                            "label": "質問に回答する",
                                            "placeholder": f"回答を入力\n質問: {message[:70]}...",
                                            "min_length": 1,
                                        }
                                    ]
                                },
                                {
                                    "type": 1,
                                    "components": [
                                        {
                                            "type": 4,
                                            "custom_id": "idtext",
                                            "style": 1,
                                            "label": "変更しないでください",
                                            "min_length": 1,
                                            "value": tuple(data["resolved"]["messages"].values())[0]['id']
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                )

    elif data.get("components"):
        id = data["custom_id"]
        if id == "askmodal":
            text = data["components"][0]["components"][0]["value"]
            send_embed("ask", text, CHANNEL_ID,)
            return jsonify({
                "type": 4,
                "data": {
                    "content": f"質問を送信しました\n{text}",
                    "flags": 64,
                }
            })
        elif id == "answermodal":
            text = data["components"][0]["components"][0]["value"]
            reply_id = data["components"][1]["components"][0]["value"]
            send_embed("answer", text, CHANNEL_ID, reply_id)
            return jsonify({
                "type": 4,
                "data": {
                    "content": f"回答を送信しました\n{text}",
                    "flags": 64,
                }
            })

    else:
        return jsonify({
            "type": 4,
            "data": {
                "content": "unknown command"
            }
        })


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
