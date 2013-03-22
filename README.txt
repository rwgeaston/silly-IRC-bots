Look at config_example.py and copy it to config.py. Crucially you need to change the owner.

Look at botmap_config_example.py in the bots/ folder. This tells the bot_runner which nickname refers to which bot module. When you create new bot modules, add them here so the bot_runner can find them.

Look at speech_example. This is a template for creating new bots. All bots currently need two functions: 1) what_to_say and 2) authorised_to_shup.

1) When receiving either a public or private message, this function tells the bot how to respond. It can make this decision based on:

source: the person who said the message
text: what they said
nickname: the nickname of the bot (useful so they can reply to their own name, without hardcoding it into the module)
private: True if the message was a PM, False for public.

you return an array of strings. The strings will be sent by private message if and only if the incoming message was private.

2) if a bot is spamming, you can send it the command "nickname: shup". This function decides who can use the shup function. Returns True or False. Implement a whitelist or perhaps do:
if source == config.owner:
    return True
else:
    return False