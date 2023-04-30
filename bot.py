import rcon
import socket
from aiogram import Bot, types, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from kb import createkb
from db import *


# config
TOKEN = ""
banned_ids = []
admin_ids = []
serverip = ""
rconport = 25575
rcon_password = ""


# texts
starttext = "Welcome to our Minecraft server!\nTo join the server, you need to get approved by the admins.\nSend /help to get bot commands.\n\nThis bot is [Open Source](https://github.com/5050prop/minecraft-wl-tgbot)."
infotext = ""


class adduserform(StatesGroup):
    nick = State()


class removeuserform(StatesGroup):
    nick = State()


storage = MemoryStorage()


bot = Bot(token=TOKEN)
bot.parse_mode = "markdown"
dp = Dispatcher(bot, storage=storage)


def sock_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((serverip, rconport))
    result = rcon.login(sock, rcon_password)
    output = rcon.command(sock, command)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    return output


async def send_admins(message):
    for admin in admin_ids:
        await bot.send_message(admin, message)


@dp.message_handler(commands=["online"])
async def online(message: types.Message):
    if message.from_user.id not in banned_ids:
        await message.reply(sock_comm("list"))
        await send_admins(f"#id{message.from_user.id}:\n\n```{message.text}```")
    else:
        await message.answer("**We are really sorry, but you are banned.**")
        await send_admins(
            f"#id{message.from_user.id}\n\n/online\n\nThe user is banned."
        )


@dp.message_handler(commands=["start"])
async def info(message: types.Message):
    await message.answer(starttext)
    await send_admins(f"#id{message.from_user.id}:\n\n```{message.text}```")


@dp.message_handler(commands=["info"])
async def info(message: types.Message):
    await message.answer(infotext)
    await send_admins(f"#id{message.from_user.id}:\n\n```{message.text}```")


@dp.message_handler(commands=["whitelistadd"])
async def whitelistadd1(message: types.Message):
    if message.from_user.id in banned_ids:
        await message.answer("**We are really sorry, but you are banned.**")
        await send_admins(
            f"#id{message.from_user.id}\n\n/whitelistadd\n\nThe user is banned."
        )
    else:
        await message.answer("Enter your Minecraft nickname:")
        await adduserform.nick.set()
        await send_admins(f"#id{message.from_user.id}:\n\n```{message.text}```")


@dp.message_handler(state=adduserform.nick)
async def whitelistadd2(message: types.Message, state: FSMContext):
    if adduser(message.from_user.id, message.text):
        await message.answer(
            "Your nickname got added to the waitlist for admin approval."
        )
        for admin in admin_ids:
            await bot.send_message(
                admin,
                f"#id{message.from_user.id} wants to add {message.text} to whitelist.",
                reply_markup=createkb(
                    f"approve_add_{message.text}", f"decline_add_{message.text}"
                ),
            )
            await state.finish()
    else:
        await message.answer("User is already in waitlist. Cancelling.")
        await state.finish()


@dp.message_handler(commands=["whitelistremove"])
async def whitelistremove1(message: types.Message):
    if message.from_user.id in banned_ids:
        await message.answer("**We are really sorry, but you are banned.**")
        await send_admins(
            f"#id{message.from_user.id}\n\n/whitelistremove\n\nThe user is banned."
        )
    else:
        await message.answer("Enter your Minecraft nickname:")
        await removeuserform.nick.set()
        await send_admins(f"#id{message.from_user.id}:\n\n```{message.text}```")


@dp.message_handler(state=removeuserform.nick)
async def whitelistremove2(message: types.Message, state: FSMContext):
    if removeuser(message.from_user.id, message.text):
        await message.answer(
            "Your nickname got added to the waitlist for admin approval."
        )
        for admin in admin_ids:
            await bot.send_message(
                admin,
                f"#id{message.from_user.id} want to remove {message.text} from whitelist.",
                reply_markup=createkb(
                    f"approve_remove_{message.text}", f"decline_remove_{message.text}"
                ),
            )
            await state.finish()
    else:
        await message.answer("User is already in waitlist. Cancelling.")
        await state.finish()


# admin buttons
@dp.callback_query_handler()
async def callback_query_handler(callback_query: types.CallbackQuery):
    if callback_query.data.startswith("approve_add_"):
        nick = callback_query.data.split("_")[2]
        sock_comm(f"whitelist add {nick}")
        await bot.send_message(callback_query.from_user.id, f"Approved {nick}")
        await bot.send_message(
            getuseridvianick(nick),
            f"Your request to add {nick} to the whitelist has been approved.",
        )
        await callback_query.answer("Approved")
        removeuseradmin(nick)

    if callback_query.data.startswith("decline_add_"):
        nick = callback_query.data.split("_")[2]
        await bot.send_message(callback_query.from_user.id, f"Declined {nick}")
        await bot.send_message(
            getuseridvianick(nick),
            f"Sorry, but your request to add {nick} to the whitelist was declined.",
        )
        await callback_query.answer("Declined")
        removeuseradmin(nick)

    if callback_query.data.startswith("approve_remove_"):
        nick = callback_query.data.split("_")[2]
        sock_comm(f"whitelist remove {nick}")
        await bot.send_message(callback_query.from_user.id, f"Approved {nick}")
        await bot.send_message(
            getuseridvianick(nick),
            f"Your request to remove {nick} from the whitelist has been approved.",
        )
        await callback_query.answer("Approved")
        removeuseradmin(nick)

    if callback_query.data.startswith("decline_remove_"):
        nick = callback_query.data.split("_")[2]
        await bot.send_message(callback_query.from_user.id, f"Declined {nick}")
        await bot.send_message(
            getuseridvianick(nick),
            f"Sorry, but your request to remove {nick} from whitelist has been declined.",
        )
        await callback_query.answer("Declined")
        removeuseradmin(nick)


@dp.message_handler(commands=["getdb"])
async def getdb(message: types.Message):
    for admin in admin_ids:
        if message.from_user.id == admin:
            await bot.send_message(admin, str(getusers()))
        else:
            await message.answer("Sorry, you got to be an admin to run that command.")


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(
        "/whitelistadd - propose admins to add a nickname to the whitelist\n/whitelistremove - propose admins to remove a nickname from the whitelist\n/help - this message\n/info - info about the server\n/online - get list and count of current players"
    )


@dp.message_handler(commands=["listpendings"])
async def listpendings(message: types.Message):
    if message.from_user.id in admin_ids:
        db = getusers()
        if len(db) == 0:
            await message.answer("No pending requests.")
        else:
            for user in db:
                if user[2] == 0:
                    await message.reply(
                        f"#id{user[0]} wants to add {user[1]} to the whitelist.",
                        reply_markup=createkb(
                            f"approve_add_{user[1]}", f"decline_add_{user[1]}"
                        ),
                    )
                elif user[2] == 1:
                    await message.reply(
                        f"#id{user[0]} wants to remove {user[1]} from the whitelist.",
                        reply_markup=createkb(
                            f"approve_remove_{user[1]}", f"decline_remove_{user[1]}"
                        ),
                    )
    else:
        await message.answer("Sorry, you got to be an admin to run that command.")


@dp.message_handler()
async def leavefromgroups(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        await message.answer("I can't be there. Leaving.")
        await message.chat.leave()
    if message.chat.type == "channel":
        # We have to leave quietly, not to shit-post into a channel.
        await message.chat.leave()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
