# Simple-Twitch-Bot-With-Interface

## Configure BOT

### Create BOT

At start you need to create bot here https://dev.twitch.tv/console/apps/create

1. Insert prefered BOT name
1. Insert url as http://localhost if you dont know what is it
1. Chose ChatBot category


### Get CLIENT_ID and SECRET_TOKEN

After creating bot you can get **CLIENT_ID** and **SECRET_TOKEN** by follow this [link](https://dev.twitch.tv/console/apps) and press **Manage** after your created bot
![example](https://docs.aws.amazon.com/lumberyard/latest/userguide/images/chatplay/twitch-manage-app.png)

### Get IRC_TOKEN

To get **IRC_TOKEN** go [here](https://twitchapps.com/tmi/)

### Get ACCESS_TOKEN
To get **ACCESS_TOKEN** follow this link<br>
`https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<client_id>&redirect_uri=http://localhost&scope=clips:edit user:edit:follows`<br><br>
With replacing `<client-id>` with your **CLIENT_ID**, you will see such thing in your browser line `http://localhost/#access_token=<access_token>&scope=clips%3Aedit+user%3Aedit%3Afollows&token_type=bearer` copy `<access_token>` and this is it!

### Configure other statments

* **INITIAL_CHANELS** Insert cannel name you want bot work with
* **SOUND_LOCATION** Location where your sounds locaed
* **MESSAGE_SOUND_NAME** Name of the sound that will be palyed while someone wrote to chat(must be in **SOUND_LOCATION**)
* **MESSAGE_SOUND_BLACKLIST** Channel names which will not cause a sound(**BOT_NICK** will be added automaticaly)
* **MUSIC_MESSAGE_TIMEOUT** Timeout between alert messages in chat
* **MUSIC_MESSAGE_TEXT** Text of alert message
* **MUSIC_COMMANDS** commands that will cause alert message
* **FOLLOW_COMMANDS** commands that will cause follow to follow
* **CLIP_COMMANDS** commands that will cause follow to follow
* **MESSAGE_SOUND** Enable sound while someone write to chat
* **MUSIC_MESSAGE** Enable automatic alert message(you need to write `!start` to chat)
