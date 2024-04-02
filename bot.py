from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '7056429683:AAEwZ3TjCJ_DgJ2zGmAwFS3ukeek65rj3c4'
ADMIN_CHAT_ID = '-1002143772467'


user_message_ids = {}

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Задайте свой вопрос и администраторы на него ответят.')


def forward_to_admin(update: Update, context: CallbackContext):
    # Пересылаем сообщение от пользователя администраторам
    message = context.bot.forward_message(chat_id=ADMIN_CHAT_ID,
                                          from_chat_id=update.message.chat_id,
                                          message_id=update.message.message_id)
    
    user_message_ids[str(message.message_id)] = update.message.from_user.id
    # Отправляем сообщение с ID в административный чат
    context.bot.send_message(chat_id=ADMIN_CHAT_ID,
                             text=f"Ответьте на это сообщение, чтобы направить ответ пользователю:\n"
                                  f"Пересланное сообщение ID: {message.message_id}")



def forward(update: Update, context: CallbackContext):
    args = context.args
    if len(args) >= 2:
        message_id = args[0]
        text = ' '.join(args[1:])
        # Проверяем, что ID сообщения сохранен в словаре
        if message_id in user_message_ids:
            # Получаем ID пользователя и отправляем ему сообщение
            user_id = user_message_ids[message_id]
            context.bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.MARKDOWN)
            update.message.reply_text(f'Сообщение отправлено пользователю с ID {user_id}.')
        else:
            update.message.reply_text('ID сообщения не найден. Возможно, вы ввели неверный ID.')
    else:
        update.message.reply_text('Используйте команду в формате: /forward <ID сообщения> <текст>')


dispatcher.add_handler(CommandHandler('start', forward_to_admin))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_admin))
dispatcher.add_handler(CommandHandler('forward', forward, pass_args=True))

updater.start_polling()
updater.idle()
