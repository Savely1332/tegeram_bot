from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram.ext import CommandHandler, ConversationHandler
from key import TOKEN
from openpyxl import load_workbook
from connect_to_database import stickers, replies, insert_sticker, insert_user, in_database


WAIT_NAME, WAIT_SEX, WAIT_GRADE = range(3)


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
    text_handler = MessageHandler(Filters.text, ask_grade)
    sticker_handler = MessageHandler(Filters.sticker, new_sticker)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", meet)],  # точка старта
        states={
            WAIT_NAME: [MessageHandler(Filters.all, ask_sex)],
            WAIT_SEX: [MessageHandler(Filters.all, ask_grade)],
            WAIT_GRADE: [MessageHandler(Filters.all, greet)],


        },  # Конечное состояние автомата
        fallbacks=[],  #

    )

    dispatcher.add_handler(murad_handler)
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(text_handler)
    dispatcher.add_handler(sticker_handler)
    dispatcher.add_handler(conv_handler)

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


def meet(update: Update, context: CallbackContext):
    """
    имя
    пол
    класс
    id юзера
    
    """
    user_id = update.message.from_user.id
    if in_database(user_id):
        update.message.reply_text(
            f'Добро пожаловать, {update.message.from_user.first_name}\n',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    return ask_name(update, context)


def ask_name(update: Update, context: CallbackContext):
    """
    имя?
    TODO проверить имя пользователя в телеге
    """
    update.message.reply_text(
        "Вас нет в базе\n"
        "Войдите в базу!\n"
        "Введите свое имя",
        reply_markup=ReplyKeyboardRemove()
    )

    return WAIT_NAME

def ask_sex(update: Update, context: CallbackContext):
    """
    пол?
    """
    name = update.message.text
    if not name_is_valid(name):
        update.message.reply_text(
            "э"
        )
        return WAIT_NAME
    context.user_data["name"] = name
    buttons = [
        ["М", "Ж"]
    ]
    keys = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )
    reply_text = f"Введите свой пол"
    update.message.reply_text(
        reply_text,
        reply_markup=keys
    )

    return WAIT_SEX

def ask_grade(update: Update, context: CallbackContext):
    """
    класс?
    """
    sex = update.message.text
    if not sex_is_valid(sex):
        update.message.reply_text(
            "э"
        )
        return WAIT_SEX
    context.user_data["sex"] = sex
    buttons = [
        ["1-8", "9-11"]
    ]
    keys = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )
    reply_text = f"Введите свой класс"
    update.message.reply_text(
        reply_text,
        reply_markup=keys
    )

    return WAIT_GRADE

def greet(update: Update, context: CallbackContext):
    """
    записывает в БД
        user_id(сообщение)
        name(контекст)
        sex((контекст)
        grade(из пред. сооб.)
    """
    grade = update.message.text
    name = context.user_data["name"]
    sex = context.user_data["sex"]
    user_id = update.message.from_user.id

    insert_user(user_id, name, sex, grade)
    update.message.reply_text(
        f'Новая запись в БД\n'
        f'{user_id=}\n'
        f'{name=}\n'
        f'{sex=}\n'
        f'{grade=}',
        reply_markup = ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def name_is_valid(name: str) -> bool:
    return name.isalpha() and name[0].isupper() and name[1:].islower()

def sex_is_valid(sex: str) -> bool:
    return True

def grede_is_valid(grade: str) -> bool:
    return True



if __name__ == '__main__':
    main()

