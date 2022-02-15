from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater , MessageHandler , Filters , CallbackContext
from key import  TOKEN
from openpyxl import load_workbook
from stickers import stickers


bd = load_workbook('database.xlsx')


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher

    echo_handler = MessageHandler(Filters.all, do_echo)
    hello_handler = MessageHandler(Filters.text('Привет'), say_hello)
    murad_handler = MessageHandler(Filters.text('Мурад'), say_ahay)
    keyboard_handler = MessageHandler(Filters.text("Клавиатура"), keyboard)

    dispatcher.add_handler(murad_handler)
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()
    print('Бот_старт - из комплете!')
    updater.idle()

def do_echo(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    id = update.message.chat_id
    text = update.message.text if update.message.text else "текста нет"
    sticker = update.message.sticker
    if sticker:
        sticker_id = sticker.file_id
        update.message.reply_sticker(sticker_id)
    update.message.reply_text(text=f'Твой id: {id}\n'
                                   f'Твой текст: {text}\n'
                                   f'Твой стикер: {sticker}')

def say_hello(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    sticker_id = stickers['Привет']
    update.message.reply_sticker(sticker_id)
    update.message.reply_text(text=f'Шалом, {name}!\n'
                                   f'Приятно познакомиться с живым человеком!\n'
                                   f'Я - бот!')

def say_ahay(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(text=f'Ахай!')

def keyboard(update: Update, context: CallbackContext):
    buttons = [
        ['1','2','3'],
        ['привет','пока']
    ]
    keys = ReplyKeyboardMarkup(
        buttons
    )

    update.message.reply_text(
        text='Смотри! У тебя появилась клавиатура',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            # one_time_keyboard=True

        )
    )

if __name__ == '__main__':
    main()