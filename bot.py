import rcon
import socket
import json
import os
from aiogram import Bot, types, executor, Dispatcher
from kb import createkb
from db import adduser, removeuseradmin, removeuser, getusers, getuseridvianick


# config
TOKEN = ""
banned_ids = []
admin_ids = []
serverip = ""
rconport = 25565
rcon_password = ""


#texts
info = ''
link_to_modpack = ''

bot = Bot(token=TOKEN)
bot.parse_mode = 'markdown'
dp = Dispatcher(bot)


def sock_comm(comm):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((serverip, rconport))
    result = rcon.login(sock, rcon_password)
    output = rcon.command(sock, comm)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    return output


async def send_admins(message):
    for admin in admin_ids:
        await bot.send_message(admin, message)


@dp.message_handler(commands=['online'])
async def online(message: types.Message):
    if message.from_user.id not in banned_ids:
        await message.reply(sock_comm("list"))
        await send_admins(f"#id{message.from_user.id}: \n\n```{message.text}```")
    else:
        await message.answer("ти в бані")
        await send_admins(f"#id{message.from_user.id} спробував виконати команду /online, але він в бані.")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.reply('команди бота:\n/whitelistadd --- добавить нік в вайтліст\n/whitelistremove --- прибрать нік із вайтліста\n/online --- вивести список задротів на сервері\n/info --- інфа про сервак\n/modpack --- отримати модпак')
    await send_admins(f"#id{message.from_user.id}: \n\n```{message.text}```")


@dp.message_handler(commands=['info', 'start'])
async def info(message: types.Message):
    await message.answer(info)
    await send_admins(f"#id{message.from_user.id}: \n\n```{message.text}```")


@dp.message_handler(commands=['whitelistadd'])
async def whitelistadd(message: types.Message):
    if message.from_user.id in banned_ids:
        await message.answer("ти в бані")
        await send_admins(f"#id{message.from_user.id} спробував додать нік в вайтліст, але юзер в бані.")
    else:
        if message.get_args() == "":
            await message.answer("invalid command syntax, /whitelistadd your_nick")
            await send_admins(f"#id{message.from_user.id} спробував додати нік на вайтліст, але не ввів нік.")
        else:
            if adduser(message.from_user.id, message.get_args()):
                await message.answer("user added to waitlist for admin approval")
                for admin in admin_ids:
                    await bot.send_message(admin, f"#id{message.from_user.id} відправив {message.get_args()} на очікування одобрення.", reply_markup=createkb(f"approve_add_{message.get_args()}", f"decline_add_{message.get_args()}"))
            else:
                await message.answer("user already in waitlist or you are the owner of this nick")
                await send_admins(f"#id{message.from_user.id} спробував додати нік на вайтліст, але він вже є в вейтлісті.")


@dp.message_handler(commands=['whitelistremove'])
async def whitelistadd(message: types.Message):
    if message.from_user.id in banned_ids:
        await message.answer("ти в бані")
        await send_admins(f"#id{message.from_user.id} спробував видалить нік з вайтліста, але юзер в бані.")
    else:
        if message.get_args() == "":
            await message.answer("invalid command syntax, /whitelistadd your_nick")
            await send_admins(f"#id{message.from_user.id} спробував видалити нік з вайтліста , але не ввів нік.")
        else:
            if removeuser(message.from_user.id, message.get_args()):
                await message.answer("user added to waitlist for admin approval")
                for admin in admin_ids:
                    await bot.send_message(admin, f"#id{message.from_user.id} відправив {message.get_args()} на очікування видалення.", reply_markup=createkb(f"approve_remove_{message.get_args()}", f"decline_remove_{message.get_args()}"))
            else:
                await message.answer("user already in waitlist or you are the owner of this nick")
                await send_admins(f"#id{message.from_user.id} спробував видалити нік з вайтліста, але такий нік вже є в вейтлісті.")


#@dp.message_handler(commands=['modpack'])
#async def modpack(message: types.Message):
#    await message.answer(link_to_modpack)
#    await send_admins(f"#id{message.from_user.id}: \n\n```{message.text}```")


# admin buttons
@dp.callback_query_handler(lambda c: c.data.startswith('decline_add_'))
async def approve(callback_query: types.CallbackQuery):
    for admin in admin_ids:
        if callback_query.from_user.id == admin:
            await bot.answer_callback_query(callback_query.id)
            if getuseridvianick(callback_query.data[12:]):
                await bot.send_message(admin, f"#id{callback_query.from_user.id} відхилив {callback_query.data[12:]}")
                await bot.send_message(getuseridvianick(callback_query.data[12:]), f"ваш запит на додавання {callback_query.data[12:]} в вайтліст було відхилено")
                removeuseradmin(callback_query.data[12:])
            else:
                await bot.send_message(admin, f"#id{callback_query.from_user.id} спробував відхилити {callback_query.data[12:]}, але такого юзера нема в базі")


@dp.callback_query_handler(lambda c: c.data.startswith('approve_add_'))
async def approve(callback_query: types.CallbackQuery):
    for admin in admin_ids:
        if callback_query.from_user.id == admin:
            await bot.answer_callback_query(callback_query.id)
            if getuseridvianick(callback_query.data[12:]):
                await bot.send_message(admin, f"#id{callback_query.from_user.id} підтвердив {callback_query.data[12:]}")
                await bot.send_message(getuseridvianick(callback_query.data[12:]), f"ваш запит на додавання {callback_query.data[12:]} в вайтліст було підтверджено")
                removeuseradmin(callback_query.data[12:])
                sock_comm(f"whitelist add {callback_query.data[12:]}")
                sock_comm(f"whitelist reload")
            else:
                await bot.send_message(admin, f"#id{callback_query.from_user.id} спробував підтвердити {callback_query.data[12:]}, але такого юзера нема в базі")


@dp.callback_query_handler(lambda c: c.data.startswith('decline_remove_'))
async def approve(callback_query: types.CallbackQuery):
    for admin in admin_ids:
        if callback_query.from_user.id == admin:
            await bot.answer_callback_query(callback_query.id)
            if getuseridvianick(callback_query.data[15:]):
                await bot.send_message(admin, f"#id{callback_query.from_user.id} відхилив {callback_query.data[15:]}")
                await bot.send_message(getuseridvianick(callback_query.data[15:]), f"ваш запит на видалення {callback_query.data[15:]} з вайтліста було відхилено")
                removeuseradmin(callback_query.data[15:])
            else:
                await bot.send_message(admin, f"#id{callback_query.from_user.id} спробував відхилити {callback_query.data[15:]}, але такого юзера нема в базі")


@dp.callback_query_handler(lambda c: c.data.startswith('approve_remove_'))
async def approve(callback_query: types.CallbackQuery):
    for admin in admin_ids:
        if callback_query.from_user.id == admin:
            await bot.answer_callback_query(callback_query.id)
            if getuseridvianick(callback_query.data[15:]):
                await bot.send_message(admin, f"#id{callback_query.from_user.id} підтвердив видалення {callback_query.data[15:]} з вайтліста")
                await bot.send_message(getuseridvianick(callback_query.data[15:]), f"ваш запит на видалення {callback_query.data[15:]} з вайтліста було підтверджено")
                removeuseradmin(callback_query.data[15:])
                sock_comm(f"whitelist remove {callback_query.data[15:]}")
                sock_comm(f"whitelist reload")
            else:
                await bot.send_message(admin, f"#id{callback_query.from_user.id} спробував підтвердити {callback_query.data[15:]}, але такого юзера нема в базі")


@dp.message_handler(commands=['getdb'])
async def getdb(message: types.Message):
    for admin in admin_ids:
        if message.from_user.id == admin:
            await bot.send_message(admin, str(getusers()))
        else:
            pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)