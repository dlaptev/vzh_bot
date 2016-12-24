Vzhuh Meme Generator for Telegram
===================================
**TL;DR.** This is a simplistic [Telegram](https://telegram.org/) bot example. The demo is at http://telegram.me/vzh_bot. It takes the text sent to it, and sends back an image of a magic cat saying this text. To be hosted on Google App Engine.

![Output example](https://img-fotki.yandex.ru/get/195771/10605357.9/0_92008_94ebff6a_orig.png)

### What it actually does
* Sets up two urls to handle requests (both are set in ```main_vzhuh.py```):
    * ```/vzhuh/img``` - takes the text passed as GET parameter, and returns an image. You can use it directly at, e.g. ```/vzhuh/img?t=and the bot is ready```.
    * ```/vzhuh/webhook``` - parses POST requests from Telegram and forms a POST json response with an url to the image and some boilerplate info.
* Handles either direct messages, or chat messages starting with ```/vz```.
    * Replies with text instructions through [```sendMessage```](https://core.telegram.org/bots/api#sendmessage) method if the text after ```/vz``` is empty.
    * If the text is provided, the bot replies with an image url through [```sendPhoto```](https://core.telegram.org/bots/api#sendphoto) method.
* The algorithm to fit the text into the rectangular area is in ```main_vzhuh.py/vzhuh_formatter```.

### Google App Engine (GAE)
The bot is hosted on [GAE](https://cloud.google.com/appengine/) (a part of Google Cloud Platform). There are multiple advantages of GAE:
* *Easy set-up.* Or rather: a bit strange, but well-documented set-up.
* *Free quotas.* Generous enough for a small, non-viral bot.
* *Free SSL/TLS encryption.* For webhook bots, you need a server that can handle TLS1.0+ HTTPS-traffic signed with a trusted and verified certificate.

### How to set it up
1. Register on Google Cloud Platform, create a new App Engine project with ```<app_engine_project_id>```.
2. Test and deploy the application following [these steps](https://cloud.google.com/appengine/docs/python/quickstart).
``` gcloud app deploy app.yaml --project <app_engine_project_id> ```
3. Create a bot with the help of the [BotFather](https://core.telegram.org/bots#6-botfather), note down your ```<telegram_bot_authorization_token>```.
4. [Set up a webhook](https://core.telegram.org/bots/api#setwebhook) with the curl request:
```
curl -v -k -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache"  -d '{
"url":"https://<app_engine_project_id>.appspot.com/vzhuh/webhook",
}' "https://api.telegram.org/bot<telegram_bot_authorization_token>/setWebhook"
```
5. Send a message to your bot in Telegram, check that it replies. Add the bot to a chat with your friends. Have fun.

##### Debugging tips:
* You can always look up GAE logs, they are quite detailed by already, but they also show whatever you just ```print``` from your code.
* To test the server response for different messages, you can use requests sent with ```curl```:
```
curl -v -k -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache"  -d '{
"update_id":10000,
"message":{
  "date":1441645532,
  "chat":{
     "last_name":"Test Lastname",
     "id":1111111,
     "type": "private",
     "first_name":"Test Firstname",
     "username":"Testusername"
  },
  "message_id":1365,
  "from":{
     "last_name":"Test Lastname",
     "id":1111111,
     "first_name":"Test Firstname",
     "username":"Testusername"
  },
  "text":"/vz and the bot is ready"
}
}' "http://localhost:8080/vzhuh/webhook"
```
