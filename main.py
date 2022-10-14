import telebot
from random import choice, randint


with open("api-key") as f:
    token = f.read().strip()
bot = telebot.TeleBot(token, parse_mode=None)

words = None
user_to_word = None
user_to_tries = None

help_message = """
Hi, there!
I'm a bot to play in "Bulls and Cows" game.
You can use the following commands:
/rules — to learn the rules of "Bulls and Cows"
/play — to start the game with me
Have fun!
"""

help_message_while_playing = """
You are in the game now.
You can use the following commands:
/hint — to get a hint for hidden word
/stop — to stop the game
"""

rules_message = """
The rules of "Bulls and Cows" are as follows:
At first I think of an isogram word (no letter in the word appears twice) and announce the number of letters in the word.
Then you try to figure out that word by guessing isogram words containing the same number of letters.
I respond with the number of Cows & Bulls for each guessed word. "Cow" means a letter in the wrong position and "Bull" means a letter in the right position.
And this process continue until the word is guessed.
Send me /play to start the game!
"""


def initialize():
    global bot, words, user_to_word, user_to_tries
    user_to_word = {}
    user_to_tries = {}

    with open("words") as f:
        words = f.read().strip().split()


@bot.message_handler(commands=['start', 'help'])
def start_help_commands(message):
    if message.chat.id in user_to_word:
        reply = help_message_while_playing
    else:
        reply = help_message
    bot.reply_to(message, reply)


@bot.message_handler(commands=['rules'])
def rules_command(message):
    bot.reply_to(message, rules_message)


@bot.message_handler(commands=['play'])
def play_command(message):
    global user_to_word, user_to_tries
    chat_id = message.chat.id
    if chat_id in user_to_word:
        bot.reply_to(message, "You're already playing the game!")
    else:
        user_to_tries[chat_id] = 0
        word = choice(words)
        user_to_word[chat_id] = word
        bot.reply_to(message, f"You started the game!\nI guessed a *{len(word)}*-letter word\nTo try to guess it, send me *{len(word)}*-letter word", parse_mode="Markdown")


@bot.message_handler(commands=['stop'])
def stop_game_command(message):
    global user_to_word, user_to_tries
    chat_id = message.chat.id
    if chat_id not in user_to_word:
        bot.reply_to(message, "You can't stop the game, because you aren't playing now:(\nSend me /help command and I'll tell you what I can!")
    else:
        tries = user_to_tries[chat_id]
        del user_to_tries[chat_id]
        word = user_to_word[chat_id]
        del user_to_word[chat_id]
        bot.reply_to(message, f"You've finished the game after *{tries}* tries:(\nThe hidden word was *{word}*", parse_mode="Markdown")


@bot.message_handler(commands=['hint'])
def stop_game_command(message):
    global user_to_word, user_to_tries
    chat_id = message.chat.id
    if chat_id not in user_to_word:
        bot.reply_to(message, "You can't get the hint, because you aren't playing now:(\nSend me /help command and I'll tell you what I can!")
    else:
        word = user_to_word[chat_id]
        ps = randint(0, len(word) - 1)
        suff = "th"
        if ps == 0:
            suff = "st"
        elif ps == 1:
            suff = "nd"
        elif ps == 2:
            suff = "rd"
        bot.reply_to(message, f"The *{ps + 1}*-{suff} letter of the guessed word is *{word[ps]}*\nContinue guessing!", parse_mode="Markdown")


def check_correctness_of_the_guess(word, length):
    if length != len(word):
        return f"I guessed a *{length}*-letter word, you should send me *{length}*-letter word for guessing"
    for letter in word:
        if ord(letter) < ord('a') or ord(letter) > ord('z'):
            return "Guessing word should contain only English letters from *a* to *z*"
    if len(set(word)) != len(word):
        return "Guessing word should be isogram (no letter in the word appears twice)!"


def get_cows_and_bulls(word1, word2):
    bulls = 0
    for i in range(len(word1)):
        if word1[i] == word2[i]:
            bulls += 1
    cows = len(set(word1) & set(word2)) - bulls
    return (cows, bulls)


@bot.message_handler(func=lambda message: True)
def guess_handler(message):
    global user_to_word, user_to_tries
    chat_id = message.chat.id
    text = message.text
    if chat_id not in user_to_word:
        bot.reply_to(message, "I can't understand you:(\nIf you try to guess a word, you're not playing now!")
    else:
        rs = check_correctness_of_the_guess(text, len(user_to_word[chat_id]))
        if rs is not None:
            bot.reply_to(message, rs, parse_mode="Markdown")
            return
        user_to_tries[chat_id] += 1
        if text == user_to_word[chat_id]:
            bot.reply_to(message, f"Congratulations!\nYou guessed the word *{text}* in *{user_to_tries[chat_id]}* tries!\nTo continue playing send me /play", parse_mode="Markdown")
            del user_to_word[chat_id]
            del user_to_tries[chat_id]
            return
        rs = get_cows_and_bulls(user_to_word[chat_id], text)
        bot.reply_to(message, f"In word *{text}* there're *{rs[0]}* cows and *{rs[1]}* bulls\nContinue guessing!", parse_mode="Markdown")


if __name__ == "__main__":
    initialize()
    bot.infinity_polling()