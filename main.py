from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from verify import generate_verification_img
import asyncio
import time

bot = Bot(token='5599510861:AAGOhwcsyw_nHgQxKQnYziozC1zlCPPfF4Q')
dp = Dispatcher(bot)


def create_welcome_text(user_name, user_id, topic):
    user_name_link = f'<a href="tg://user?id={user_id}">{user_name}</a>'
    text = f'Привет {user_name_link}! Выбери номер фото, на котором "{topic}", чтобы войти в чат. У тебя 1 минута.'

    return text


async def kick_member(message, chat_id, user_id):
    await message.bot.ban_chat_member(chat_id, user_id)
    await message.bot.unban_chat_member(chat_id, user_id)


async def give_time_to_solve(chat_id, user_id, message, sequence, time_to_solve):
    await asyncio.sleep(time_to_solve)

    if new_members_solutions:
        for member in new_members_solutions:
            if user_id == member[0] and sequence == member[1]:
                await kick_member(message, chat_id, user_id)
                await bot.delete_message(chat_id, member[3])
                new_members_solutions.remove(member)


# ===============================================================================================================

sequence = 0
new_members_solutions = []

inline_keyboard = InlineKeyboardMarkup()
num_btns = [
    InlineKeyboardButton(text=index + 1, callback_data=index)
    for index in range(6)
]
inline_keyboard.row(*num_btns)


@dp.message_handler(content_types=['new_chat_members'])
async def send_verification_test(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id

    await bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + 300)

    verification_img, topic, correct_img_index = generate_verification_img()

    verification_img.save('verification_img.jpg')
    verification_photo = open('verification_img.jpg', 'rb')

    test = await bot.send_photo(
        chat_id,
        verification_photo,
        caption=create_welcome_text(user_name, user_id, topic),
        parse_mode="HTML",
        reply_markup=inline_keyboard
    )

    global sequence
    test_id = test.message_id

    new_members_solutions.append((user_id, sequence, correct_img_index, test_id))

    await give_time_to_solve(chat_id, user_id, message, sequence, 60)

    sequence += 1


@dp.message_handler(content_types=['left_chat_member'])
async def left_member(message: types.Message):
    user_id = message.from_user.id

    for member in new_members_solutions:
        if user_id == member[0]:
            new_members_solutions.remove(member)


@dp.callback_query_handler()
async def exam_new_member(callback: types.CallbackQuery):
    if new_members_solutions:
        user_id = callback.from_user.id
        user_name = callback.from_user.first_name
        chat_id = callback.message.chat.id
        message_id = callback.message.message_id

        for member in new_members_solutions:
            if user_id == member[0] and message_id == member[3]:
                if callback.data == str(member[2]):
                    await callback.answer(f'Добро пожаловать {user_name}!')
                    await bot.delete_message(chat_id, member[3])
                    await bot.promote_chat_member(chat_id, user_id)
                    new_members_solutions.remove(member)
                else:
                    await callback.answer('Неправильный ответ!')
                    await kick_member(callback, chat_id, user_id)
                    await bot.delete_message(chat_id, member[3])
                    new_members_solutions.remove(member)
            else:
                await callback.answer('Этот тест не для тебя')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
