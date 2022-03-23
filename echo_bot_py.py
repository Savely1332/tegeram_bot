from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from key import TOKEN
from openpyxl import load_workbook
from connect_to_database import stickers, replies, insert_sticker


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
    text_handler = MessageHandler(Filters.text, say_smth)
    sticker_handler = MessageHandler(Filters.sticker, new_sticker)

    dispatcher.add_handler(murad_handler)
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(text_handler)
    dispatcher.add_handler(sticker_handler)

    updater.start_polling()
    print('Бот_старт - из комплете!')
    updater.idle()

def say_smth(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    text = update.message.text
    for keyword in stickers:
        if keyword in text:
            update.message.reply_sticker(stickers[keyword])
            update.message.reply_text(replies[keyword].format(name))
            break
    else:
        do_echo(update, context)

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

def new_sticker(update: Update, context: CallbackContext):
    sticker_id = update.message.sticker.file_id
    for keyword in stickers:
        if sticker_id == stickers[keyword]:
            update.message.reply_text('У меня тоже такой есть!')
            update.message.reply_sticker(sticker_id)
            break
    else:
        context.user_data['new_sticker'] = sticker_id
        update.message.reply_text('Скажи мне ключевое слово для этого стикера, и я его запомню')


def new_keyword(update: Update, context: CallbackContext):
    if 'new_sticker' not in context.user_data:
        say_smth(update, context)
    else:
        keyword = update.message.text
        sticker_id = context.user_data['new_sticker']
        insert_sticker(keyword, sticker_id)
        context.user_data.clear()

def meet(update: Update, context: CallbackContext)
    """
    имя
    пол
    класс
    id юзера
    
    """
    user_id = update.message.from_user.id
    if in_database(user_id):
        pass # выход из диолога
    ask_name(update, context)

def ask_name(update: Update, context: CallbackContext)
    update.message.reply_text(
        "Вас нет в базе\n"
        "Войдите в базу!\n"
        "ВВведите свое имя"
    )

if __name__ == '__main__':
    main()