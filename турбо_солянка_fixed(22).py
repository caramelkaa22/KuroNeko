__version__=(0, 1, 5)
# meta developer: enicaaa (pure reflex)
# -----------------------Immports---------------
from .. import loader, utils
from ..inline.types import InlineCall

from typing import Union, Optional
import re
import os
import html
import asyncio
from asyncio.exceptions import TimeoutError
from datetime import datetime, timedelta
import logging
import json as Json
from random import choice, randrange
import pytz

from telethon.tl.types import (
    Message,
    User,
    MessageEntityPhone,
    MessageEntityMentionName,
    MessageEntityTextUrl,
    MessageEntityMention,
    Channel,
)

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

MEP = MessageEntityPhone
MEMN = MessageEntityMentionName
METU = MessageEntityTextUrl
MENT = MessageEntityMention
logger = logging.getLogger('saltwort')
re._MAXCAСHE = 3000

# ---------------------------Module--------------------


@loader.tds
class Saltwort(loader.Module):
    """
В разработке \n\n            Если ты совершил ошибку,\n            которую можно исправить,\n            то это была не ошибка\n                    © Кто-то из великих"""

    # Чат бота Biowars, откуда реально приходят уведомления о заражении
    BIOWAR_CHAT_IDS = {-5043529249, 8644732229, -1004413327164}
    # Кулдаун между заражениями (часы)
    INFECT_COOLDOWN_HOURS = 6

    strings = {
        "name": "Saltwort",
        "link_id": "tg://openmessage?user_id=",
        "link_username": "https://t.me/",

        "сommands": {
#            "z": "[args] [reply] ",
            "id": "[arg/reply] -",
            "ids": "[args] [reply] - Чекает айди по реплаю",
            "dov": "Показывает информацию по доверке",
#            'zz': 'Заражает по списку',
            'nik': '[id] [имя] - запись человека',
            'pref': '[id] [префикс] - записывает префикс дова',
            'import': '[реплай на список или JSON] - импорт жертв',
            'timer': '[add N текст / del id / list] - циклотаймер: шлёт текст раз в N (30=мин, 2ч, 1д)',
            'искл': '[add id / del id / list] - исключения для АвтоБио (кого не трогать)',
            'export': '- экспорт зарлиста в JSON (формат обмена, schema_version 1)'
        },
        # Зарлист
        'zar.search':
            "🟢 <b>Жертва:</b> \n      {} \n"
            "🟠 <b>Приносит:</b>\n      <i>+{} био-опыта</i>\n"
            "🟣 <b>Заражен до:</b> \n      <i>{}</i> \n",
#            '📅 <b>Заражение до:</b> {} ',

        'zar.save':
            "🟢 <b>Я сохранил </b>\n      <code>{}</code>\n"
            "🟠 <b>Био-опыт:</b>\n      <s>{}</s> +{}  \n"
            "🟣 <b>Заражение до:</b>\n      {} ",

        'z.nf': '⭕ <b>Жертва \n      <code>{}</code>\n      не найдена</b>',

        'edit_nik': '<b>Юзер <code>@{0}</code> сохранен как</b> <a href = "tg://openmessage?user_id={0}">{1}</a>',
        'edit_pref': '<b>Префикс <code>{}</code> сохранен для <code>@{}</code></b>',
# Руководство по модулю
        "bio.commands": "🔳<b> Доступные команды:</b> \n\n"
        "{1} \n"
        "<b>Руководство по модулю.</b> \n"
        "<code>{0}солянка инфо</code> - <b>информация о вас</b> \n"
        "<code>{0}солянка навыки</code> - <b>помощь по лабе</b>\n"
        "<code>{0}солянка зарлист</code> - <b>помощь по зарлисту</b>\n\n"
        '«---------------ᕙ(⇀‸↼‶)ᕗ---------------»',
        
# Информация о вас
        'bio.info':
            '🔳 <b>Информация::</b> \n\n'
            '🟢<b>Жертв в зарлисте:</b>\n      <i>{}</i> \n'
            '🟠 <b>Суммарный опыт:</b>\n      <i>{}</i>\n'
            '🟣 <b>В доверке:</b>\n      <i>{}</i>\n\n'
            '«---------------٩(๑❛ᴗ❛๑)۶---------------»',

# Помощь по зарлисту
        "bio.zar": "🔳 <b>Помощь по зарлисту</b>\n\n"
            "🟤 <b>Проверка списка</b>\n"
            "[ник] з <i>Чек жертвы</i>\n"
            "[ник] зз [био] [нов] <i>Чек списка (нов — только новые жертвы)</i>\n\n"
            "🟤 <b>Заражение</b>\n"
            "[ник] еб [бей] <i>Заразить жертву</i>\n"
            "[ник] еб 1-4...7-30 <i>Выборочно из списка</i>\n"
            "[ник] еб 1-30 <i>Заражение по списку</i>\n\n"
            "🟤 <b>Вывод зарлиста</b>\n"
            "[ник] жертвы (топ жертвы)\n\n"
            "🔴 <i>Сохранение в зарлист - недоступно</i>\n\n"
            '«---------------(◡‿◡✿)---------------»',
            
#Управление лабораторией через доверку help Навыки       
        "bio.skill": "🔳 <b>Уровни доступа через доверку</b>\n\n"
           "🟢  <b>1 уровень - Зарлист</b>\n"
           "  <b>Покупка вакцины:</b>\n"
           "  🔸[ник] вак/хил\n"
           "  <b>Просмотр жертв в зарлисте:</b>\n"
           "  🔸[ник] жертвы/топ жертвы\n"
           "      <b>Проверка списка и жертв:</b>\n"
           "  🔸[ник] сб <i> служба безопасности</i>\n"
           "  🔸[ник] калкулятор навыков\n"
           "  🔸[ник] зз/био [нов] <i> список / только новые</i>\n"
           "  🔸[ник] з <i>проверка жертвы</i>\n"
           "  <b>Заражение:</b>\n"
           "  🔸[ник] еб/бей 1-5 7 9... <i>выборочно </i>\n"
           "  🔸[ник] еб/бей  <i>одну жертву</i>\n"
           "  <b>Просмотр лаборатории:</b>\n"
           "  🔸[ник] мл <i>краткая лаба</i>\n\n"
           "🟢  <b>2 уровень- Лаборатория</b>\n"
           "  🔸[ник] фл <i>полная лаба</i>\n"
           "  🔸<b>Установка имени лабы:</b>\n"
           "  🔸[ник] +лаб [название]       <i>установить</i>\n"
           "  🔸[ник] -лаб <i>удалить</i>\n"
           "  <b>Установка патогена:</b>\n"
           "  🔸[ник] пат [название] <i>установка</i>\n"
           "  🔸[ник] -пат <i>удаление</i>\n"
           "  <b>Уведомления:</b>\n"
           "  🔸[ник] уведы <i>уведомления</i>\n"
           "  <b>Улучшение навыков:</b>\n"
           "  🔸[ник] +навык [1-5] <i>стоимость прокачки</i>\n"
           "  🔸[ник] ++навык [1-5] <i>прокачка</i>\n"
           "  <i>навыки: заразность, иммунитет, патоген, летальность, безопасность</i>\n"
           "  🔸[ник] чек навык [...9] <i>       стоимость (старый вид)</i>\n"
           "  🔸[ник] навык [1...9] <i>прокачка (старый вид)</i>\n\n"  
           "«---------------¯\_(ツ)_/¯---------------»",

#Все что относится к доверке
        "dov": "<b>🔳 Информация по доверке</b> \n\n"
        "🟠 <b>Список доверенных пользователей:</b> \n"
        "  🔸 <code>{0}dov dovs</code> - Общий список\n"
        "  🔸 <code>{0}dov dovs chat</code> - В чате\n"
        "  🔸 <code>{0}dov prefs</code> - Общий список\n"
        "  🔸 <code>{0}dov prefs chat</code> - В чате\n\n"
        "🟠 <b>Удалить/добавить саппорта:</b>\n"
        '  🔸 <code>{0}dov set</code> [айди/реплай]\n\n'
        "🟠 <b>Повысить/понизить уровень</b>\n"
        "  🔸 <code>{0}dov set</code> [айди/реплай] 1 или 2\n"
        "  🔸 <code>{0}dov nik</code> [ник]  <i>Установить ник</i> \n"
        "     🟡 Ваш ник: <code>{1}</code> \n\n"
        "🟠 <b>Включение/Выключение доверки</b>\n"
        "      {2} <code>{0}dov st</code> "
        "      Статус: <i>{3}</i> \n\n"
        "«--------------ᕦ(ò_óˇ)ᕤ--------------»",

#Команды доверки
        'dov.users': '🟡 <b>В доверке:</b> \n' 
        '{}',
        "dov.users.chat": '🟠 Доверки в чате: \n' 
        '{}',
        "dov.prefs": '🟡 <b>Ваши доверки:</b> \n'
        '{}',
        "dov.prefs.chat": '🟠 <b> Доверившие пользователи в чате: </b>\n' 
        '{}',
        "dov.rem": "🔴  <b>Пользователь</b>\n      @{} \n      <b>Удален из списка</b>\n",
        "dov.add":
            "🟢 <b>Юзер</b> @{} \n      <b>Добавлен в список</b>\n     "
            " <b>Уровень доверки:</b> {}",
        'dov.edit_level':
            '♻️ <b>Уровень доверки</b>\n      для <code>@{}</code>\n      <b>изменен'
               ' <s>{}</s> 👉 {}</b>',
        "nick.rename": "♻️ <b>Изменён ник \n</b>" 
            '️ <b><s>{0}</s> 👉 <b>{1}</b>',
        "dov.status.True": "🟢 <i>Доверка\n      включена</i>",
        "dov.status.False": "🔴 <i>Доверка\n      выключена</i>",

# Ошибки
        "no.reply": "⭕ Отсуствует\n      реплай",
        "no.args": "⭕ Отсуствуют\n      аргументы",
        "no.args_and_reply": "⭕ Отсуствуют\n      реплай и\n      аргументы",
        "args_error": '⭕ Аргументы\n      введены\n      неверно',
        "len_error": "⭕ <b>Превышено\n       количество\n      символов. \n      Лимит 8</b>",
        "hueta": "⭕ Тут что-то не так?",

#Рандом при чек зарлиста
        "messages.biotop": [
            '🟢 Займись делом\n',
            '🟢 Интересный биотоп\n',
            '🟢 Скучный биотоп\n'
        ],
        'messages.misc': [
            "🤡 На манеже все те же\n",
            "🤢 Зря ты сюда заглянул\n",
            "🫤 Думаешь будет фарм?\n",
        ],
        "get_user": "🟢 <b>Пользователь: </n>\n"
        "      <a href='tg://openmessage?user_id={}'>{}</a> \n"
        "<b>🔴 <b>Юзернейм:</b>\n      @{} \n"
        "<b>🟣 <b>Айди:</b>\n      <code>@{}</code>",
        'calc_formul': {
            'zar': 2.5,
            'imun': 2.55,
            'sb': 2.1,
            'kvala': 2.6,
            'pat': 2,
            'letal': 1.95
        }


    }
# -----------------------Functions-------------------

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Вкл/Выкл доверки",
                False,
                "Статус доверки",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "Автозапись жертв",
                False,
                "Автозапись жертв(БЕТА)\nНе работает",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "отладка",
                False,
                "дебаг сообщения",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "АвтоБио",
                False,
                "Раз в минуту проверяет биотоп: если жертва не на кулдауне и "
                "выгодна (10% её опыта > текущий доход) — атакует её; если вы "
                "сами заражены — сначала пишет '.купить вакцину'. Выключено по умолчанию.",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "АвтоБио мин. прибыль",
                1,
                "Минимальный плюс опыта, при котором АвтоБио атакует жертву. "
                "Пример: 10 → заразит того, у кого прибыль +11, но не тронет +9.",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "АвтоБио макс. атак за цикл",
                5,
                "Сколько максимум жертв атаковать за один проход (раз в минуту). "
                "Защита от перегрузки юзербота/спама при большом списке выгодных.",
                validator=loader.validators.Integer(minimum=1),
            ),
        )

    async def client_ready(self, client, db):
        # Nummod + saltwort
        self.client = client
        self.db = db
        # Состояние листов (пагинация) и запусков заражений по /код
        self._page_store = {}
        self._mass_lists = {}
        self._mass_task = None
        self._mass_state = {'sent': 0, 'skipped': 0, 'total': 0}

        # NumMod
        if not self.db.get("NumMod", "numfilter"):
            # Добовление овнеров юб в список доверившихся людей
            # Айди аккаунта там тоже присуствует
            owners = list(getattr(self.client.dispatcher.security, "owner"))
            self.db.set(
                "NumMod",
                "numfilter",
                {"users": owners, "filter": None, "status": False},
            )
# infection
        if not self.db.get("NumMod", "infection"):
            self.db.set("NumMod", "infection", {})

        if not self.db.get("saltwort", "DovUsers"):
            owners = list(getattr(self.client.dispatcher.security, "owner"))
            users = {}
            for i in self.db.get("NumMod", "numfilter")["users"]:
                users[str(i)] = 1
            for i in owners:
                users[str(i)] = 4
            self.db.set("saltwort", "DovUsers", users)

        if not self.db.get('saltwort', 'FamousUsers'):
            self.db.set('saltwort', 'FamousUsers', {})
            # {id : username }
        if not self.db.get('saltwort', 'LastInfect'):
            self.db.set('saltwort', 'LastInfect', None)

        if not self.db.get('saltwort', 'InfectionBefore'):
            self.db.set('saltwort', 'InfectionBefore', {})

        if not self.db.get('saltwort', 'YourLetal'):
            self.db.get('saltwort', 'YourLetal', 1)
            # Ваш летал, будет использоватся при записи жертв в зарлист
        if not self.db.get('saltwort', 'UsersNik'):
            self.db.set('saltwort', 'UsersNik', {})
            # user_id : желаемый ник
        if not self.db.get('saltwort', 'FamousPrefs'):
            self.db.set('saltwort', 'FamousPrefs', {})
            # user_id : pref
        # При заражении ставится True
        # Статус заражения
        self.db.set("saltwort", "infStatus", False)
        # Интервал между заражениями
        self.db.set("saltwort", "infInterval", 4)

    async def send(self, text: str, message: Message) -> None:
        """Если возникает ошибка при отправке сообщения с инлайн клавиатурой,   то отправляется обычное сообщение с таким же текстом"""
        # from telethon.errors.rpcerrorlist import BotResponseTimeoutError
        try:
            await self.inline.form(
                text,
                reply_markup={
                    "text": "🔻SaltWort🔻",
                    "callback": self.inline__close,
                },
                message=message,
                disable_security=False,
            )
        except:
            await utils.answer(message, text)

    async def inline__close(self, call) -> None:
        await call.delete()

    async def return_user(self, username: str) -> int:
        if username not in self.db.get('saltwort', 'FamousUsers').values():
            await self._write_user(username=username)

        famous_users = self.db.get('saltwort', 'FamousUsers')
        for k, v in famous_users.items():
            if v == username:
                user_id = k
                return user_id

    async def save_nik(self, user_id: int, nik: str) -> None:
        users_nik = self.db.get('saltwort', 'UsersNik')
        users_nik[str(user_id)] = nik
        self.db.set('saltwort', 'UsersNik', users_nik)

    async def save_pref(self, user_id: int, nik: str) -> None:
        users_nik = self.db.get('saltwort', 'FamousPrefs')
        users_nik[str(user_id)] = nik
        self.db.set('saltwort', 'FamousPrefs', users_nik)

    async def _write_user(self, username: Optional[str] = None, user_id: Optional[int] = None) -> None:
        famous_users = self.db.get('saltwort', 'FamousUsers')
        if (username in famous_users) or (user_id in famous_users):
            return

        if username and user_id:
            famous_users[user_id] = username
        # Если есть юзер айди, вытаскиваем юзернейм и сохраняем его
        if not username:
            if user_id not in famous_users.keys():
                try:
                    user = await self.client.get_entity(user_id)
                    username = user.username if user.username else None
                    famous_users[user_id] = username
                except:
                    return None
        if not user_id:
            # Если есть юзернейм, то вытаскиваем с помощью него юзер айди
            if username not in famous_users.values():
                try:
                    user = await self.client.get_entity(username)
                    user_id = user.id
                    famous_users[user_id] = username
                except:
                    return None

# Сохраняем все
        self.db.set('saltwort', 'FamousUsers', famous_users)

    async def save_last_infect(self, user: Optional[str]) -> None:
        if user:
            user = user.replace('@', '')
            if not user.isdigit():
                if user.startswith('https://t.me/'):
                    user = user.replace('https://t.me/', '')
                user = await self.return_user(username=user)

        save = user if user else None
        self.db.set('saltwort', 'infection',
                    save)

# Нужен класс чата, а не айди чата
    async def get_members_chat(self, chat: Channel) -> Union[list, str]:
        offset_user = 0    # номер участника, с которого начинается считывание
        limit_user = 50   # максимальное число записей, передаваемых за один раз

        users = []   # список всех участников канала

        filter_user = ChannelParticipantsSearch('')
        try:
            while True:
                participants = await self.client(GetParticipantsRequest(
                    chat,
                    filter_user,
                    offset_user,
                    limit_user,
                    hash=0))
                if not participants.users:
                    break

                users.extend(participants.users)
                offset_user += len(participants.users)
            ids = [i.id for i in users]
            return ids

        except TypeError:
            return 'NotChat'

    async def _handler_link(self, link) -> Optional[str]:
        if link.startswith(self.strings("link_id")):
            return "@" + link.replace(self.strings("link_id"), "")
        elif link.startswith(self.strings("link_username")):
            return "@" + link.replace(self.strings("link_username"), "")
        else:
            return None

    async def number_convert(self, number: int) -> str:
        if number >= 1000000000:
            return f"{number / 1000000000:.1f}B"
        elif number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}k"
        else:
            return str(number)

    async def get_pref(self) -> str:
        return self.db.get("hikka.main", "command_prefix", ".")

    async def _generator_links(self, reply, args: str) -> Union[list, str]:
        list_args, lis = [], []
        for i in args.split(" "):
            if "-" in i:
                ot_do = i.split("-")
                try:
                    list_args.extend(
                        str(x) for x in range(int(ot_do[0]), int(ot_do[1]) + 1)
                    )
                except Exception:
                    return "wrong_ot-do"

            else:
                list_args.append(i)

        a = reply.text
        entity = reply.get_entities_text()
        users = []
        #validate_text = await self.validate_text(text)

        for e in entity:
            if isinstance(e[0], MENT):
                url = e[1]
                # if not url.startswith('@'):
                # continue

                users.append(url)

            elif isinstance(e[0], METU):
                url = await self._handler_link(e[0].url)
                users.append(url)

        for arg in list_args:
            lis.append(users[int(arg)-1])

        return lis

    async def _o_generator_links(self, reply: Message) -> Union[list, str]:
        lis = []
        json = Json.loads(reply.to_json())
        try:
            for i in range(len(reply.entities)):
                try:
                    link = json["entities"][i]["url"]
                    if link.startswith("tg"):
                        users = "@" + link.split("=")[1]
                        lis.append(users)
                    elif link.startswith("https://t.me"):
                        a = "@" + str(link.split("/")[3])
                        lis.append(a)
                    else:
                        return "hueta"
                except Exception:
                    blayt = reply.raw_text[
                        json["entities"][i]["offset"]: json["entities"][i]["offset"]
                        + json["entities"][i]["length"]
                    ]
                    lis.append(blayt)
            return lis
        except TypeError:
            return "hueta"

    async def get_top_zhertv(self, message: Message, num_list: int) -> None:
        import operator
        # Cортировка зарлиста
        infection = self.db.get('NumMod', 'infection')
        a = {}
        zhertvs = []
        for k, v in infection.items():
            a[k] = int(float((v[0]))) if not 'k' in v[0] else int(
                float(v[0][:-1].replace(',', '.')) * 1000)

        sort = sorted(a.items(), key=operator.itemgetter(1), reverse=True)

        sort_dict = dict(sort)

        users = list(sort_dict.keys())

        for i in range(0, len(users), 50):
            e_c = users[i: 50 + i]

            if len(e_c) < 50:
                e_c = e_c + [None for y in range(50 - len(e_c))]
            zhertvs.append(e_c)

        if num_list > len(zhertvs):
            await utils.answer(message, 'Такого номера вкладки нет')
            return
        # ------------------------------------------------
        # Генерация текста с жертвами

        infectBefore = self.db.get(
            'saltwort', 'InfectionBefore')
        niks = self.db.get('saltwort', 'UsersNik')
        all_exps = int(sum([eval(i[0].replace(",", ".").replace(
            'k', '*1000')) for i in list(infection.values())]))
        bio_exp = await self.number_convert(all_exps)
        all_exps = '{:,}'.format(all_exps).replace(',', ' ')

        sms = f'Топ ваших жертв({num_list}/{len(zhertvs)}): \n'
        count = 1

        for i in zhertvs[num_list-1]:
            if not i:
                continue
            user = infection[i]
            zar_do = infectBefore[i] if i in infectBefore.keys(
            ) else '<b>неизвестная дата</b>'
            if i[1:] in niks.keys():
                nik = niks[str(i[1:])]
                usr = f'<a href="tg://openmessage?user_id={i[1:]}">{nik}</a>'
            else:
                usr = i
            sms += f'{count}. {usr} | +{user[0]} | заражение до {zar_do} \n'
            count += 1

        sms += f'\n🟢 <b>Заражённых:</b>   <i>{len(infection)}</i>\n🔴 <b>Био-опыт:</b>   <i>{bio_exp}</i>\n'
        sms += f'🟣 <b>био-ресурс:</b>   <i>{all_exps}</i>'
        await self.send(sms, message)

    async def get_zhertv(self, message: Message, num_list: int) -> None:
        infection = self.db.get('NumMod', 'infection')
        users = list(reversed(infection.keys()))
        zhertvs = []

        for i in range(0, len(users), 50):
            e_c = users[i: 50 + i]

            if len(e_c) < 50:
                e_c = e_c + [None for y in range(50 - len(e_c))]
            zhertvs.append(e_c)

        # генерация сообщения

        if num_list > len(zhertvs):
            await utils.answer(message, 'Такого номера вкладки нет')
            return

        infectBefore = self.db.get('saltwort', 'InfectionBefore')
        niks = self.db.get('saltwort', 'UsersNik')
        all_exps = int(sum([eval(i[0].replace(",", ".").replace(
            'k', '*1000')) for i in list(infection.values())]))
        bio_exp = await self.number_convert(all_exps)
        all_exps = '{:,}'.format(all_exps).replace(',', ' ')

        sms = f'Ваши жертвы({num_list}/{len(zhertvs)}): \n'
        count = 1

        for i in zhertvs[num_list-1]:
            if not i:
                continue
            user = infection[i]
            zar_do = infectBefore[i] if i in infectBefore.keys(
            ) else '<b>неизвестная дата</b>'
            if i[1:] in niks.keys():
                nik = niks[str(i[1:])]
                usr = f'<a href="tg://openmessage?user_id={i[1:]}">{nik}</a>'
            else:
                usr = i
            sms += f'{count}. {usr} | +{user[0]} | заражение до {zar_do} \n'
            count += 1

        sms += f'\n🟢 <b>Заражённых:</b>   <i>{len(infection)}</i>\n🔴 <b>Био-опыт:</b>   <i>{bio_exp}</i>\n'
        sms += f'🟣 <b>Био-ресурс:</b>   <i>{all_exps}</i>'
        await self.send(sms, message)

    @staticmethod
    def _parse_exp(s: str) -> Optional[float]:
        """'6,4k' -> 6400.0, '877' -> 877.0, '1.8к' -> 1800.0"""
        m = re.fullmatch(r'\s*([0-9]+(?:[.,][0-9]+)?)\s*([kкKК]?)\s*', str(s))
        if not m:
            return None
        val = float(m.group(1).replace(',', '.'))
        return val * 1000 if m.group(2) else val

    async def _compute_top_labs(self, reply: Message, me: User) -> dict:
        """Разбирает 'ТОП ЛАБОРАТОРИЙ ПО БИО-ОПЫТУ' и возвращает
        {'plus': [{'profit','gain','old','uid','name','key'}, ...] (по убыванию
        профита), 'minus': N, 'unknown': N}."""
        infection = self.db.get("NumMod", "infection") or {}

        # Ссылки в порядке появления: (текст, user_id)
        ent_queue = []
        for ent, ent_text in reply.get_entities_text():
            uid = None
            if isinstance(ent, MEMN):
                uid = ent.user_id
            elif isinstance(ent, METU):
                m = re.search(r'user[_]?id=(\d+)', ent.url)
                if m:
                    uid = int(m.group(1))
            if uid is not None:
                ent_queue.append((ent_text, uid))

        line_re = re.compile(
            r'^\s*\d+\.\s*(?P<name>.+?)\s*\|\s*(?P<exp>[0-9.,]+\s*[kкKК]?)\s*опыт')

        plus, minus, unknown = [], 0, 0
        ent_i = 0
        for line in (reply.raw_text or '').splitlines():
            m = line_re.match(line)
            if not m:
                continue

            name = m.group('name').strip()
            uid = None
            if ent_i < len(ent_queue) and ent_queue[ent_i][0] and ent_queue[ent_i][0] in name:
                uid = ent_queue[ent_i][1]
                ent_i += 1

            victim_exp = self._parse_exp(m.group('exp'))
            if uid is None or victim_exp is None:
                unknown += 1
                continue
            if str(uid) == str(me.id):
                continue

            key = f'@{uid}'
            gain = int(round(victim_exp * 0.1))          # 10% опыта жертвы
            old = self._parse_exp(infection[key][0]) if key in infection else 0
            old = int(old or 0)
            profit = gain - old

            if profit > 0:
                plus.append({'profit': profit, 'gain': gain, 'old': old,
                             'uid': uid, 'name': name, 'key': key})
            else:
                minus += 1

        plus.sort(key=lambda c: c['profit'], reverse=True)
        return {'plus': plus, 'minus': minus, 'unknown': unknown}

    async def top_labs(self, reply: Message, me: User) -> str:
        """Текстовое представление _compute_top_labs для команды 'зз'."""
        data = await self._compute_top_labs(reply, me)

        if not data['plus']:
            return '🔘 Выгодных для заражения нет\n'

        infection = self.db.get("NumMod", "infection") or {}
        cooldowns = self._get_cooldowns()  # один раз на весь список, не на каждую строку
        sms = '🟢 <b>Выгодно заразить:</b>\n'
        for n, c in enumerate(data['plus'], start=1):
            hourglass = '⏳ ' if self._cooldown_left_for(c['key'], cooldowns) else ''
            state = (f"{c['old']} → {c['gain']}" if c['key'] in infection
                      else f"новый → {c['gain']}")
            sms += (f"{n}. {hourglass}<a href='tg://openmessage?user_id={c['uid']}'>"
                    f"{html.escape(c['name'])}</a> 🔸<b>[+{c['profit']}]</b> <i>({state})</i>\n")
        sms += f"\n🔻 Невыгодно: {data['minus']}"
        if data['unknown']:
            sms += f" | ❔ Без id: {data['unknown']}"
        return sms + '\n'

    async def bio(self, reply: Message, me: User, only_new: bool = False, collected: Optional[list] = None):

        first_line = (reply.raw_text or '').splitlines()[0] if reply.raw_text else ''
        if 'ТОП ЛАБОРАТОРИЙ' in first_line:
            return await self.top_labs(reply, me)

        infection = self.db.get("NumMod", "infection")
        b = reply.raw_text.splitlines()

        niks = self.db.get('BioWars', 'UsersNik')
        sms = ''
        exps = []
        # Add exp
        if chat_flag := 'Биотоп чмоней' in b.pop(0):
            b.pop(0);b.pop(-1);b.pop(-1)
            for i in b:
                try:
                    exps.append(i.split('|')[-1])
                except:
                    pass

        json = Json.loads(reply.to_json())

        if len(exps) == 0:

            entity = reply.get_entities_text()
            users = []

            for e in entity:
                if isinstance(e[0], MENT):
                    url = e[1]
                    users.append(url)
                elif isinstance(e[0], METU):
                    url = await self._handler_link(e[0].url)
                    users.append(url)
            count = 1
            cooldowns = self._get_cooldowns()  # один раз на весь список
            for i in users:
                if only_new:
                    # режим "нов": себя и уже заражённых пропускаем
                    if i in infection or str(i[1:]) == str(me.id):
                        continue
                    if collected is not None:
                        collected.append(i)
                if str(i[1:]) == str(me.id):
                    name = me.first_name
                    sms += f'{str(count)}.  <a href= "tg://openmessage?user_id={me.id}">{name}</a>\n'
                    count += 1
                    continue

                if str(i[1:]) in niks:
                    nik = niks[str(i[1:])]
                    name = f"<a href='tg://openmessage?user_id={i[1:]}'>{nik}</a>"
                else:
                    name = i

                exp = infection[i][0] if i in infection else None
                if exp:
                    hourglass = '⏳ ' if self._cooldown_left_for(i, cooldowns) else ''
                    exp = f'{hourglass}🟠 {exp}'
                else:
                    exp = '<emoji document_id=5382357040008021292>🔘</emoji> Еще не бил, бей!'
                sms += f'{count}. {name} {exp} \n'
                count += 1
            return sms

        else:
            count = 1
            cooldowns = self._get_cooldowns()  # один раз на весь список
            for i in range(0, len(b)):
                try:
                    exp = exps[i].replace(",", ".")
                    s = exp.find(' опыт')
                    exp = exp[1:s].replace(' ', '')
                    if 'k' in exp:
                        exp_count = float(exp[:-1])
                        if exp_count < 10.0:
                            exp = int(round(exp_count * 100, 0))

                        else:
                            exp_count = float(exp[:-1])
                            exp_count = int(exp_count)
                            exp = str(exp_count / 10) + 'k'

                    else:
                        exp_count = int(exp)
                        exp = exp_count // 10

                except:
                    exp = None

                link = json["entities"][i]["url"]
                bla = []
                if link.startswith('tg'):
                    for i in link.split('='):
                        bla.append(i)

                    if str(bla[1]) == str(me.id):
                        if only_new:
                            continue
                        name = me.first_name
                        sms += f'{str(count)}. 🍺 <a href= "tg://openmessage?user_id={me.id}">{name}</a> {exp}  \n'
                        count += 1
                        continue

                    user_id = bla[1]
                    if only_new:
                        if '@' + str(user_id) in infection:
                            continue
                        if collected is not None:
                            collected.append('@' + str(user_id))
                    if '@' + str(user_id) in infection:
                        if chat_flag:
                            user = infection['@' + str(user_id)]
                            usr_exp = user[0].replace(',', '.')
                            exp_count = str(exp)

                            if usr_exp[-1] == 'k':
                                usr_exp = float(usr_exp[:-1]) * 1000

                            if exp_count[-1] == 'k':
                                exp_count = float(exp_count[:-1]) * 1000

                            result = int(float(exp_count) - float(usr_exp))

                            # abc.append(str(result))

                            if result > 0:
                                if result < 1000:
                                    result = f'<emoji document_id=5397916757333654639>🔸</emoji>[+{str(result)}]'
                                else:
                                    result = f'<emoji document_id=5397916757333654639>🔸</emoji>[+{str(round(float(result) / 1, 1))}]'
                            elif result == 0:
                                result = f'[{str(result)}]'

                            else:
                                if result > -1000:
                                    result = f'<emoji document_id=5210952531676504517>🔻</emoji>[{str(result)}]'
                                else:
                                    result = f'<emoji document_id=5210952531676504517>🔻</emoji>[{str(round(float(result) / 1, 1))}]'
                            zh = f"({user[0]}) | <b>{result}</b>"
                        else:
                            hourglass = '⏳ ' if self._cooldown_left_for('@' + str(user_id), cooldowns) else ''
                            zh = f"{hourglass}🟠 (+{infection['@' + str(user_id)][0]})"
                    else:
                        if chat_flag:  # если это чат и жертвы нет в зарлисте
                            exp_count1 = str(exp)
                            if exp_count1[-1] == 'k':
                                exp_count1 = float(exp_count1[:-1]) * 1000

                            if round(float(exp_count1), 1) < 10000.0:  # +{}к
                                zh = f'| 🔘 <b>[+{round(float(exp_count1) / 1000,1)}]</b>'
                            else:  # + {}
                                zh = f'| 🔘 <b>[+{round(float(exp_count1)/ 1000,1)}]</b>'
                        else:
                            zh = ''

                    try:
                        if str(bla[1]) in niks:
                            nik = niks[str(bla[1])]
                            name = f"<a href='tg://openmessage?user_id={bla[1]}'>{nik}</a>"
                        else:
                            name = '@' + str(bla[1])

                        exp = f'| {exp}'
                        sms += f'{str(count)}. {name} {zh} {exp} \n'

                    except:
                        if str(bla[1]) in niks:
                            nik = niks[str(bla[1])]
                            name = f"<a href='tg://openmessage?user_id={bla[1]}'>{nik}</a>"
                        else:
                            name = '@' + str(bla[1])

                        exp = f'| {exp}'
                        sms += f'{str(count)}. {name} {zh} {exp} \n'
                count += 1
            return sms

    async def message_q(  # отправляет сообщение боту и возращает ответ
        self,
        text: str,
        bot_id: int = 8644732229,
        mark_read: bool = True,
        delete: bool = True,
    ) -> str:
        """Отправляет сообщение и возращает ответ"""
        async with self.client.conversation(bot_id, exclusive=False) as conv:
            try:
                msg = await conv.send_message(text)
                response = await conv.get_response()
                if mark_read:
                    await conv.mark_read()
                if delete:
                    await msg.delete()
                    await response.delete()
                return response.text
            except TimeoutError:
                return "Timeout"


# -----------------------Commands in watcher----------


    async def z_command(self, message: Message, args_raw: str, text: str, reply: Message) -> None:
        if self.db.get("saltwort", "infStatus"):
            await message.reply('⭕  <b>Заражения\n      не завершены</b>')
            return

        if not args_raw and not reply:  # .z - аргументов нет
            text = self.strings("no.args_and_reply")
            await utils.answer(message, text)
            return

        if (reply and not args_raw):
            entities = reply.get_entities_text()
            if re.search(r"👨🏻‍🔬 Была проведена операция заражения", reply.text):

                infect = await self._handler_link(entities[1][0].url)
                self.db.set("saltwort", "infStatus", True)
                await message.reply(f"заразить  {infect}")

                await self.save_last_infect(str(infect))
                self.db.set("saltwort", "infStatus", False)
                return

            elif len(entities) == 1 and len(entities[0]) == 2:
                user_id = entities[0][1]

                if not user_id.startswith('@'):
                    return

                self.db.set("saltwort", "infStatus", True)
                await message.reply(f"заразить  {user_id}",)

                await self.save_last_infect(str(user_id))
                self.db.set("saltwort", "infStatus", False)

            else:
                user_id = reply.sender_id

                self.db.set("saltwort", "infStatus", True)
                await message.reply(f"заразить  @{user_id}",)

                await self.save_last_infect(str(user_id))
                self.db.set("saltwort", "infStatus", False)

            return
        if reply and args_raw == 'о':

            ids = await self._o_generator_links(reply)

            self.db.set("saltwort", "infStatus", True)

            for i in ids:
                interval = self.db.get("saltwort", "infInterval", 2)
                await message.client.send_message(
                    message.peer_id, f"заразить  {i}", reply_to=reply
                )
                await asyncio.sleep(interval)

            else:
                await message.reply('🟢  <b>Заражения\n      окончены</b>')

            self.db.set("saltwort", "infStatus", False)
            return

        if reply and args_raw:
            users = await self._generator_links(reply, args_raw)

            if len(users) == 1:
                self.db.set("saltwort", "infStatus", True)
                await message.reply(f"заразить  {users[0]}")

                await self.save_last_infect(users[0])
                self.db.set("saltwort", "infStatus", False)
            else:
                self.db.set("saltwort", "infStatus", True)
                interval = self.db.get("saltwort", "infInterval", 4)
                for infect in users:
                    if self.db.get("saltwort", "infStatus"):
                        await message.reply(f"заразить  {infect}",)
                        await asyncio.sleep(interval)
                    else:
                        return
                else:
                    await message.reply('🟢  <b>Заражения\n      окончены</b>')

                self.db.set("saltwort", "infStatus", False)
                return

    async def id_command(self, message: Message, args: str, reply) -> None:
        if not args and not reply:
            user = await self.client.get_me()

        elif reply:
            user_id = reply.sender_id
            user = await message.client.get_entity(user_id)

        elif args.startswith("@"):
            if args[1:].isdigit():
                user_id = int(args[1:])
            else:
                user_id = args[1:]

            user = await message.client.get_entity(user_id)
        else:
            return

        username = user.username if user.username else "Отсуствует"
        await self.write_user(username, user.id)
        await self.client.send_message(
            message.chat_id,
            self.strings("get_user").format(
                user.id, user.first_name, username, user.id
            ),
            reply_to=reply,
        )

    async def ids_command(self, message: Message, args_raw: str, reply) -> None:
        if not reply:
            await utils.answer(message, self.strings("no.reply"))
            return
        ids = (
            await self._generator_links(reply, args_raw)
            if args_raw
            else await self._o_generator_links(reply)
        )
        for i in ids:
            await message.client.send_message(
                message.peer_id, f".ид {i}", reply_to=reply
            )
            await asyncio.sleep(3.5)
        else:
            await message.respond("🟢  <b>Все айди\n      прочеканы!</b>")

    async def dov_command(
        self, message: Message, args_list: list, args_raw: str, reply
    ) -> None:

        numfilter = self.db.get("NumMod", "numfilter")
        saltwort_dovs = self.db.get("saltwort", "DovUsers")
        pref = await self.get_pref()

        if not args_raw and not reply:
            status_emj = "🟢" if self.config["Вкл/Выкл доверки"] else "🔴"
            status = "Включено" if self.config["Вкл/Выкл доверки"] else "Выключено"
            nik = numfilter["filter"] if numfilter["filter"] else "Не   установлен"

            text_message = self.strings("dov").format(
                pref, nik, status_emj, status
            )
            await self.send(text_message, message)
            return

        if args_list[0].lower() == "set":
            # Если 2 аргумента то ставим первый уровень, если 3 аргументы и 3 типа инт ставим уровень указанный в нем

            level = None
            data = args_list[1:]
            logging.info(f'{data}')
            if reply:
                user_id = str(reply.sender_id)
                if data:
                    level = int(data[0]) if data[0].isdigit() else None
                if not level:
                    level = None

            elif re.fullmatch(r"@\d+", data[0]):
                user_id = data[0].replace('@', '')
                # try:
                if len(data) >= 2:
                    level = int(data[1]) if data[1].isdigit() else None
                if not level:
                    level = None
                # except Exception:
                    # await utils.answer(message, self.strings('args_error'))
                    # return
            else:
                await utils.answer(message, self.strings('args_error'))
                return
            # Я знаю что in распостраняется только на user_id

            if level and user_id in saltwort_dovs.keys():
                old_level = saltwort_dovs[user_id]
                saltwort_dovs[user_id] = level
                self.db.set("saltwort", "DovUsers", saltwort_dovs)
                await utils.answer(message, self.strings('dov.edit_level').format(user_id, old_level, level))

                return

            elif str(user_id) in saltwort_dovs.keys():
                numfilter["users"].remove(str(user_id))
                saltwort_dovs.pop(user_id)
                self.db.set("saltwort", "DovUsers", saltwort_dovs)
                await utils.answer(message, self.strings("dov.rem").format(user_id))
                return
            else:
                logging.info(
                    f'{user_id} - {level}')
                level = level if level else 1
                numfilter["users"].append(user_id)
                saltwort_dovs[user_id] = level
                text_message = self.strings("dov.add").format(user_id, level)
                self.db.set("saltwort", "DovUsers", saltwort_dovs)

                await utils.answer(message, text_message)
                return

        elif args_list[0].lower() == "nik":
            if args_list[1]:
                if len(args_list[1]) > 8 or len(args_list) >= 3:
                    await utils.answer(message, self.strings("len_error"))
                    return

                old_nik = numfilter["filter"] if numfilter["filter"] else "Отсуствует"
                nik = args_list[1]
                numfilter['filter'] = nik
                self.db.set("NumMod", "numfilter", numfilter)
                await utils.answer(message,
                                   self.strings("nick.rename").format(
                                       old_nik, nik)
                                   )

            else:
                await utils.aswer('Какой ник будем ставить?')
                return

        elif args_list[0].lower() == "dovs":
            niks = self.db.get('saltwort', 'UsersNik')

            dovs_users = ''

            if len(args_list) > 1 and args_list[1].lower() == 'chat':
                r = await self.get_members_chat(message.chat)
                if r == 'NotChat':
                    await utils.answer(message, 'Это не чат')
                    return
                else:
                    users = r
                i = 1
                for user in users:
                    if str(user) in saltwort_dovs.keys():
                        level = saltwort_dovs[str(user)]

                        level = '2ур <b>Имба</b>' if level == 2 else f'{level} ур'

                        if str(user) in niks.keys():
                            nik = niks[str(user)]
                            usr = f'<a href="tg://openmessage?user_id={user}">{nik}</a>'
                        else:
                            usr = f'<code>@{user}</code>'

                        dovs_users += f'<b>{i})</b> {usr} - {level} \n'
                        i += 1
                dovs_users = dovs_users if dovs_users else 'В этом чате никого нет'

                await self.send(self.strings('dov.users.chat').format(dovs_users), message)
                return
            for i, (user_id, level) in enumerate(saltwort_dovs.items(), start=1):

                level = '2ур <b>Имба</b>' if level == 2 else f'{level} ур'

                if str(user_id) in niks.keys():
                    nik = niks[str(user_id)]
                    usr = f'<a href="tg://openmessage?user_id={user_id[1:]}">{nik}</a>'
                else:
                    usr = f'<code>@{user_id}</code>'

                dovs_users += f'<b>{i})</b> {usr} - {level} \n'
            await self.send(self.strings('dov.users').format(dovs_users), message)
            return

        elif args_list[0].lower() == "prefs":
            prefs_users = self.db.get('saltwort', 'FamousPrefs')
            niks = self.db.get('saltwort', 'UsersNik')
            prefs = ''
            if len(args_list) > 1 and args_list[1].lower() == 'chat':
                r = await self.get_members_chat(message.chat)
                if r == 'NotChat':
                    await utils.answer(message, 'Это не чат')
                    return
                else:
                    users = r
                i = 1
                for user in users:
                    if str(user) in prefs_users.keys():
                        pref = prefs_users[str(user)]

                        if str(user) in niks.keys():
                            nik = niks[str(user)]
                            usr = f'<a href="tg://openmessage?user_id={user}">{nik}</a>'
                        else:
                            usr = f'<code>@{user}</code>'

                        prefs += f'<b>{i})</b> {usr} | {pref} \n'
                        i += 1
                prefs = prefs if prefs else 'В этом чате никого нет'

                await self.send(self.strings('dov.prefs.chat').format(prefs), message)
                return

            for i, (user_id, pref) in enumerate(prefs_users.items(), start=1):
                if str(user_id) in niks.keys():
                    nik = niks[str(user_id)]
                    usr = f'<a href="tg://openmessage?user_id={user_id[1:]}">{nik}</a>'
                else:
                    usr = f'<code>@{user_id}</code>'
                prefs += f'<b>{i})</b> {usr} | {pref} \n'

            prefs = prefs if prefs else 'Тут никого нет'

            await self.send(self.strings('dov.prefs').format(prefs), message)
            return

        elif args_list[0].lower() == "st":
            status = self.config["Вкл/Выкл доверки"]
            if status:
                self.config["Вкл/Выкл доверки"] = False
                await utils.answer(message, self.strings("dov.status.False"))
            else:
                self.config["Вкл/Выкл доверки"] = True
                await utils.answer(message, self.strings("dov.status.True"))

    # >>> VICTIMS-IO BEGIN
    MSK = pytz.timezone("Europe/Moscow")
    PAGE_SIZE = 50        # жертв на один лист
    MASS_INTERVAL = 90    # 1.5 минуты между заражениями по /код

    @staticmethod
    def _iso_utc(dt: datetime) -> str:
        return dt.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def _parse_iso(s) -> Optional[datetime]:
        if not s or not isinstance(s, str):
            return None
        for fmt in ('%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z'):
            try:
                return datetime.strptime(s.strip(), fmt).astimezone(pytz.utc)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_date(s):
        """'17.10.2026' -> date | None"""
        try:
            d, m, y = (int(x) for x in str(s).split('.'))
            return datetime(y + 2000 if y < 100 else y, m, d).date()
        except Exception:
            return None

    def _build_export(self, owner_id: int):
        """Собирает зарлист в формате обмена (schema_version 1).
        Возвращает (payload, число пропущенных записей без числового id)."""
        infection = self.db.get("NumMod", "infection") or {}
        before = self.db.get('saltwort', 'InfectionBefore') or {}
        now_utc = datetime.now(pytz.utc)
        now_msk = now_utc.astimezone(self.MSK)

        keys = sorted((k for k in infection if re.fullmatch(r'@\d+', k)),
                      key=lambda k: int(k[1:]))
        skipped = len(infection) - len(keys)

        victims = []
        for key in keys:
            entry = infection[key]
            val = self._parse_exp(entry[0]) if entry else None
            daily = int(round(val)) if val is not None else 1

            # Дата окончания хранится как ДД.ММ.ГГГГ без времени — считаем,
            # что заражение действует до конца этого дня по Москве
            expires = None
            d = self._parse_date(before.get(key))
            if d:
                expires = self.MSK.localize(
                    datetime(d.year, d.month, d.day, 23, 59, 59)).astimezone(pytz.utc)

            # Дата заражения хранится как ДД.ММ без года — год подбираем так,
            # чтобы она не оказалась позже окончания (или позже "сейчас")
            infected = None
            try:
                dd, mm = (int(x) for x in str(entry[1]).split('.')[:2])
                ref = expires.astimezone(self.MSK) if expires else now_msk
                cand = self.MSK.localize(datetime(ref.year, mm, dd))
                if cand > ref:
                    cand = self.MSK.localize(datetime(ref.year - 1, mm, dd))
                infected = cand.astimezone(pytz.utc)
            except Exception:
                infected = None
            if infected is None:
                infected = expires or now_utc

            if expires is None:
                duration, status = None, 'unknown_expiry'
            else:
                duration = max(0, int((expires - infected).total_seconds()))
                status = 'active' if expires > now_utc else 'expired'

            victims.append({
                'telegram_id': int(key[1:]),
                'infections': [{
                    'id': None,  # id заражения в игре модулем не хранится
                    'infected_at': self._iso_utc(infected),
                    'duration_seconds': duration,
                    'expires_at': self._iso_utc(expires) if expires else None,
                    'daily_bio_resources': daily,
                    'status': status,
                }],
            })

        payload = {
            'schema_version': 1,
            'exported_at': self._iso_utc(now_utc),
            'owner_telegram_id': owner_id,
            'unclassified_infections_count': 0,
            'victims': victims,
            'victims_count': len(victims),
            'infections_count': sum(len(v['infections']) for v in victims),
        }
        return payload, skipped

    def _merge_import(self, data: dict, me_id: int) -> dict:
        """Вливает файл формата обмена в зарлист. Более свежие записи
        (с более поздним окончанием) не перезаписываются старыми."""
        infection = self.db.get("NumMod", "infection") or {}
        before = self.db.get('saltwort', 'InfectionBefore') or {}
        stat = {'added': 0, 'updated': 0, 'kept': 0, 'invalid': 0, 'self': 0}
        floor = datetime.min.replace(tzinfo=pytz.utc)

        for v in data.get('victims', []):
            if not isinstance(v, dict):
                stat['invalid'] += 1
                continue
            tid = v.get('telegram_id')
            infs = [i for i in (v.get('infections') or []) if isinstance(i, dict)]
            if not str(tid).isdigit() or not infs:
                stat['invalid'] += 1
                continue
            if str(tid) == str(me_id):
                stat['self'] += 1
                continue

            active = [i for i in infs if i.get('status') == 'active'
                      and self._parse_iso(i.get('expires_at'))]
            if active:
                best = max(active, key=lambda i: self._parse_iso(i['expires_at']))
            else:
                best = max(infs, key=lambda i: self._parse_iso(i.get('infected_at')) or floor)

            try:
                daily = max(int(float(best.get('daily_bio_resources'))), 0)
            except (TypeError, ValueError):
                daily = 1
            inf_dt = self._parse_iso(best.get('infected_at'))
            exp_dt = self._parse_iso(best.get('expires_at'))
            short = (inf_dt or datetime.now(pytz.utc)).astimezone(self.MSK).strftime('%d.%m')
            exp_date = exp_dt.astimezone(self.MSK).date() if exp_dt else None

            key = '@' + str(tid)
            if key not in infection:
                stat['added'] += 1
            else:
                old = self._parse_date(before.get(key))
                if exp_date is None or (old is not None and exp_date <= old):
                    stat['kept'] += 1
                    continue
                stat['updated'] += 1

            infection[key] = [str(daily), short]
            if exp_date:
                before[key] = exp_date.strftime('%d.%m.%Y')

        self.db.set("NumMod", "infection", infection)
        self.db.set('saltwort', 'InfectionBefore', before)
        return stat

    async def _read_json_file(self, reply: Message):
        raw = await reply.download_media(bytes)
        return Json.loads(raw.decode('utf-8-sig'))

    @staticmethod
    def _victim_keys(data) -> list:
        """Ключи '@id' из файла: формат обмена (victims[].telegram_id)
        или старый плоский список ["@id", ...]."""
        keys = []
        if isinstance(data, dict) and isinstance(data.get('victims'), list):
            for v in data['victims']:
                if isinstance(v, dict) and str(v.get('telegram_id', '')).isdigit():
                    keys.append('@' + str(v['telegram_id']))
        elif isinstance(data, list):
            for x in data:
                sx = str(x).strip()
                if re.fullmatch(r'@?\d+', sx):
                    keys.append('@' + sx.lstrip('@'))
        return list(dict.fromkeys(keys))
    # >>> VICTIMS-IO END

    def _mass_register(self, keys: list) -> str:
        """Запоминает список под случайным 6-значным кодом для /код."""
        lists = self._mass_lists
        code = f"{randrange(10 ** 6):06d}"
        while code in lists:
            code = f"{randrange(10 ** 6):06d}"
        lists[code] = list(dict.fromkeys(keys))
        while len(lists) > 10:
            lists.pop(next(iter(lists)))
        return code

    def _mass_footer(self, keys: list) -> str:
        if not keys:
            return ''
        code = self._mass_register(keys)
        return (f"▶️ Заражать каждые 1.5 мин ({len(set(keys))} шт.): /{code}\n"
                f"⏹ Остановить: /stop")

    def _render_page(self, token: str, page: int):
        data = self._page_store.get(token)
        if not data:
            return None, None
        lines = data['lines']
        pages = max(1, (len(lines) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        page = min(max(page, 0), pages - 1)
        chunk = lines[page * self.PAGE_SIZE:(page + 1) * self.PAGE_SIZE]

        head = data['header']
        if pages > 1:
            head += f" — лист <code>{page + 1}/{pages}</code>"
        text = head + "\n" + "\n".join(chunk)
        if data['footer']:
            text += "\n\n" + data['footer']

        nav = []
        if page > 0:
            nav.append({"text": "◀️ Предыдущий лист",
                        "callback": self._page_cb, "args": (token, page - 1)})
        if page < pages - 1:
            nav.append({"text": "Следующий лист ▶️",
                        "callback": self._page_cb, "args": (token, page + 1)})
        markup = [nav] if nav else []
        markup.append([{"text": "🔻 Закрыть" if pages > 1 else "🔻SaltWort🔻",
                        "callback": self.inline__close}])
        return text, markup

    async def _page_cb(self, call: InlineCall, token: str, page: int) -> None:
        text, markup = self._render_page(token, page)
        if text is None:
            await call.answer("Список устарел — запросите заново", show_alert=True)
            return
        await call.edit(text, reply_markup=markup)

    async def send_paged(self, header: str, lines: list, footer: str, message: Message) -> None:
        """Отправляет список по 50 строк на лист с кнопками
        «Предыдущий лист / Следующий лист / Закрыть»."""
        token = f"{randrange(10 ** 8):08d}"
        self._page_store[token] = {'header': header, 'lines': lines, 'footer': footer}
        while len(self._page_store) > 30:
            self._page_store.pop(next(iter(self._page_store)))
        text, markup = self._render_page(token, 0)
        try:
            await self.inline.form(text, reply_markup=markup,
                                   message=message, disable_security=False)
        except Exception:
            await utils.answer(message, text)

    async def _send_new_list(self, message: Message, new_keys: list, total: int, hit: int) -> None:
        if not new_keys:
            await self.send(f"🔘 <b>Новых жертв нет</b> — все {hit} из {total} "
                            f"уже в зарлисте", message)
            return
        niks = self.db.get('saltwort', 'UsersNik') or {}
        lines = []
        for n, key in enumerate(new_keys, start=1):
            digits = key[1:]
            nik = niks.get(digits)
            label = html.escape(nik) if nik else key
            lines.append(f"{n}. <a href='tg://openmessage?user_id={digits}'>{label}</a>")
        header = (f"🟢 <b>Новые жертвы</b> (<code>{len(new_keys)}</code> из "
                  f"<code>{total}</code>):")
        footer = f"🟠 Уже в зарлисте (не показаны): <code>{hit}</code>\n" + self._mass_footer(new_keys)
        await self.send_paged(header, lines, footer, message)

    async def check_json_victims(self, message: Message, reply: Message, me: User) -> None:
        """(ник) зз [нов] в ответ на JSON-файл (формат обмена или старый
        список ["@id", ...]) — показывает только тех, кого ещё нет в зарлисте."""
        try:
            data = await self._read_json_file(reply)
        except Exception as e:
            await self.send(f"🔴 <b>Не смог прочитать JSON:</b> <code>{html.escape(str(e))}</code>", message)
            return

        keys = self._victim_keys(data)
        if not keys:
            await self.send("🔴 <b>Не нашёл жертв в файле</b> (нужен формат экспорта "
                            "с полем victims или список [\"@id\", ...])", message)
            return

        infection = self.db.get("NumMod", "infection") or {}
        hit = sum(1 for k in keys if k in infection)
        new_keys = [k for k in keys if k not in infection and k[1:] != str(me.id)]
        await self._send_new_list(message, new_keys, len(keys), hit)

    async def new_victims_from_text(self, message: Message, reply: Message, me: User) -> None:
        """(ник) зз нов в ответ на обычный список — только новые жертвы."""
        infection = self.db.get("NumMod", "infection") or {}
        first_line = (reply.raw_text or '').splitlines()[0] if reply.raw_text else ''
        collected = []

        if 'ТОП ЛАБОРАТОРИЙ' in first_line:
            lines = []
            data = await self._compute_top_labs(reply, me)
            for c in data['plus']:
                if c['key'] in infection:
                    continue
                collected.append(c['key'])
                lines.append(f"{len(lines) + 1}. <a href='tg://openmessage?user_id={c['uid']}'>"
                             f"{html.escape(c['name'])}</a> 🔸<b>[+{c['gain']}]</b>")
        else:
            body = await self.bio(reply, me, only_new=True, collected=collected)
            lines = [ln.rstrip() for ln in (body or '').split('\n') if ln.strip()]

        if not lines:
            await self.send("🔘 <b>Новых жертв нет</b> — все из списка уже в зарлисте", message)
            return
        header = f"🟢 <b>Новые жертвы</b> (<code>{len(lines)}</code>):"
        await self.send_paged(header, lines, self._mass_footer(collected), message)

    async def _mass_command(self, message: Message, cmd: str) -> None:
        """/123456 — запуск заражений по списку, /stop — остановка."""
        if cmd == '/stop':
            task = self._mass_task
            if task and not task.done():
                task.cancel()
                st = self._mass_state
                await utils.answer(message, f"⏹ <b>Остановлено.</b> Отправлено "
                                            f"{st['sent']} из {st['total']}")
            else:
                await utils.answer(message, "🔘 <b>Сейчас ничего не запущено</b>")
            return

        keys = self._mass_lists.get(cmd[1:])
        if keys is None:
            await utils.answer(message, "🔴 <b>Такого списка нет</b> — он устарел или "
                                        "модуль перезапускался, запросите список заново")
            return
        if self._mass_task and not self._mass_task.done():
            await utils.answer(message, "⚠️ <b>Заражения уже идут</b> — сначала /stop")
            return

        self._mass_state = {'sent': 0, 'skipped': 0, 'total': len(keys)}
        self._mass_task = asyncio.ensure_future(self._mass_infect(keys, message.chat_id))
        total_min = max(len(keys) - 1, 0) * self.MASS_INTERVAL / 60
        await utils.answer(
            message,
            f"🟢 <b>Заражения запущены</b>\n"
            f"      Жертв: <code>{len(keys)}</code>\n"
            f"      Интервал: <code>1.5 мин</code> (≈ {total_min:.0f} мин всего)\n"
            f"      Остановить: /stop"
        )

    async def _mass_infect(self, keys: list, report_chat_id: int) -> None:
        """Раз в MASS_INTERVAL секунд шлёт 'заразить <жертва>' боту.
        Кто уже в зарлисте (например, заразил АвтоБио) — пропускается."""
        attack_chat_id = next((cid for cid in self.BIOWAR_CHAT_IDS if cid > 0), None) \
            or report_chat_id
        st = self._mass_state

        def already(k):
            return k in (self.db.get("NumMod", "infection") or {})

        try:
            for key in keys:
                if already(key):
                    st['skipped'] += 1
                    continue
                if st['sent']:
                    await asyncio.sleep(self.MASS_INTERVAL)
                    if already(key):
                        st['skipped'] += 1
                        continue

                if re.fullmatch(r'@\d+', key):
                    cmd = f"заразить tg://openmessage?user_id={key[1:]}"
                else:
                    cmd = f"заразить {key}"
                await self.client.send_message(attack_chat_id, cmd)
                st['sent'] += 1

            await self.client.send_message(
                report_chat_id,
                f"✅ <b>Заражения по списку завершены:</b> отправлено "
                f"{st['sent']}, пропущено {st['skipped']}"
            )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            try:
                await self.client.send_message(
                    report_chat_id, f"🔴 <b>Заражения по списку прерваны:</b> "
                                    f"<code>{html.escape(str(e))}</code>")
            except Exception:
                pass

    async def bio_command(self, message: Message, reply: Message, me, only_new: bool = False) -> None:
        if reply.file and (reply.file.name or '').lower().endswith('.json'):
            await self.check_json_victims(message, reply, me)
            return

        if only_new:
            await self.new_victims_from_text(message, reply, me)
            return

        if reply.text.startswith('Биотоп чмоней:'):
            sms = choice(self.strings('messages.biotop')) + '\n'
        else:
            sms = choice(self.strings('messages.misc')) + '\n'

        sms += await self.bio(reply, me)

        await self.send(sms, message)

    async def nik_command(self, message: Message, args_list: list, args_raw: str) -> None:

        user_id = args_list[0].replace('@', '')
        user_nikname = ' '.join(args_list[1:])
        await self.save_nik(user_id, user_nikname)
        await utils.answer(message, self.strings('edit_nik').format(user_id, user_nikname))

    async def pref_command(self, message: Message, args_list: list) -> None:
        user_id = args_list[0].replace('@', '')
        user_pref = ' '.join(args_list[1:])
        await self.save_pref(user_id, user_pref)
        await utils.answer(message, self.strings('edit_pref').format(user_pref, user_id))

    def _get_cooldowns(self) -> dict:
        """Возвращает словарь кулдаунов {user_key: unix-время окончания},
        попутно вычищая из бд уже истёкшие записи (по прошествии кулдауна
        айди выносится из бд)."""
        cooldowns = self.db.get('saltwort', 'Cooldowns') or {}
        now = datetime.now(pytz.timezone("Europe/Moscow")).timestamp()
        changed = False
        for uid in list(cooldowns.keys()):
            if cooldowns[uid] <= now:
                del cooldowns[uid]
                changed = True
        if changed:
            self.db.set('saltwort', 'Cooldowns', cooldowns)
        return cooldowns

    def _set_cooldown(self, user_key: str) -> None:
        """Заносит user_key в бд кулдаунов с фиксированным временем
        INFECT_COOLDOWN_HOURS от текущего момента."""
        cooldowns = self._get_cooldowns()
        cooldowns[user_key] = (
            datetime.now(pytz.timezone("Europe/Moscow")).timestamp()
            + self.INFECT_COOLDOWN_HOURS * 3600
        )
        self.db.set('saltwort', 'Cooldowns', cooldowns)

    def _cooldown_left_for(self, user_key: str, cooldowns: Optional[dict] = None) -> Optional[timedelta]:
        """Оставшееся время кулдауна для конкретного user_key, либо None.
        ВАЖНО: при переборе списка из N жертв нужно один раз получить
        cooldowns = self._get_cooldowns() и передавать его сюда явно —
        иначе каждый вызов делает отдельный поход в бд (N обращений вместо 1),
        что при большом зарлисте ощутимо грузит юзербот."""
        if cooldowns is None:
            cooldowns = self._get_cooldowns()
        expiry = cooldowns.get(user_key)
        if not expiry:
            return None
        remaining = expiry - datetime.now(pytz.timezone("Europe/Moscow")).timestamp()
        return timedelta(seconds=remaining) if remaining > 0 else None

    @staticmethod
    def _format_timedelta(td: timedelta) -> str:
        total = int(td.total_seconds())
        hours, rem = divmod(total, 3600)
        minutes = rem // 60
        return f"{hours} ч {minutes} мин"

    def _am_i_infected(self) -> bool:
        """True, если по данным SelfInfectedUntil вы сейчас заражены (кто-то
        другой вас заразил, и срок ещё не истёк)."""
        expiry = self.db.get('saltwort', 'SelfInfectedUntil')
        if not expiry:
            return False
        return datetime.now(pytz.timezone("Europe/Moscow")).timestamp() < expiry

    @loader.loop(interval=60, autostart=True)
    async def autobio_loop(self):
        """Раз в минуту (если включено в конфиге "АвтоБио"): запрашивает
        биотоп командой "биотоп" и атакует ВСЕХ, кто выгоден и не в
        кулдауне; если сами заражены — сначала лечится и в этот раз не бьёт."""
        if not self.config["АвтоБио"]:
            return

        try:
            # Чат бота Biowars — единственный положительный id среди
            # разрешённых чатов (групповой id для биотопа отрицательный)
            attack_chat_id = next(
                (cid for cid in self.BIOWAR_CHAT_IDS if cid > 0), None)
            if not attack_chat_id:
                return

            if self._am_i_infected():
                await self.client.send_message(attack_chat_id, '.купить вакцину')
                # Флаг снимается только по подтверждению "Вакцина излечила
                # вас" в watcher'е — в этом цикле не бьём, попробуем в следующий
                return

            # Активно запрашиваем свежий биотоп командой "биотоп" (не
            # полагаемся на то, что бот сам когда-то что-то пришлёт)
            await self.client.send_message(attack_chat_id, 'биотоп')
            await asyncio.sleep(3)  # даём боту время ответить

            try:
                reply = (await self.client.get_messages(
                    attack_chat_id, limit=1))[0]
            except Exception:
                return
            if not reply or 'ТОП ЛАБОРАТОРИЙ' not in (reply.raw_text or ''):
                return

            me = await self.client.get_me()
            data = await self._compute_top_labs(reply, me)

            # data['plus'] отсортирован по убыванию профита (для вывода в
            # .зз), а бить нужно наоборот — снизу списка вверх
            min_profit = self.config["АвтоБио мин. прибыль"]
            excluded = set(self.db.get('saltwort', 'AutoBioExclude') or [])
            # ФИКС (нагрузка): раньше кулдауны читались из бд ОТДЕЛЬНЫМ
            # вызовом на КАЖДУЮ жертву в биотопе (до ~80 обращений к бд за
            # один проход цикла) — это и грузило юзербот. Теперь один раз.
            cooldowns = self._get_cooldowns()
            targets = [c for c in reversed(data['plus'])
                       if c['profit'] > min_profit
                       and str(c['uid']) not in excluded
                       and c['key'] not in cooldowns]
            if not targets:
                return

            # ФИКС (нагрузка): ограничиваем число атак за один проход цикла —
            # если выгодных целей много, бить всех разом (с паузой 2с между
            # каждой) тоже ощутимо грузит и спамит бота. Остальные подхватит
            # следующий проход через минуту.
            targets = targets[:self.config["АвтоБио макс. атак за цикл"]]

            for target in targets:
                # На случай, если заразили нас самих между итерациями цикла —
                # прекращаем бить и идём лечиться на следующем проходе
                if self._am_i_infected():
                    break

                # ФИКС: атака происходит фразой "заразить <ссылка>", а не
                # "{ник} еб <ссылка>" — последнее для этой команды не подходит
                await self.client.send_message(
                    attack_chat_id,
                    f"заразить tg://openmessage?user_id={target['uid']}"
                )
                # Небольшая пауза между атаками, чтобы не спамить бота
                await asyncio.sleep(2)
        except Exception as e:
            if self.config["отладка"]:
                try:
                    me2 = await self.client.get_me()
                    await self.client.send_message(
                        me2.id, f"🐞 DEBUG: ошибка в АвтоБио: {e}")
                except Exception:
                    pass

    @staticmethod
    def _parse_duration(s: str) -> Optional[int]:
        """'30' -> 1800с (мин. по умолчанию), '2ч'/'2h' -> 7200, '90с'/'90s' ->
        90, '1д'/'1d' -> 86400."""
        m = re.fullmatch(r'\s*(\d+)\s*([смчдsmhd]?)\s*', str(s), re.IGNORECASE)
        if not m:
            return None
        val = int(m.group(1))
        unit = m.group(2).lower()
        mult = {
            '': 60, 'м': 60, 'm': 60,
            'с': 1, 's': 1,
            'ч': 3600, 'h': 3600,
            'д': 86400, 'd': 86400,
        }
        return val * mult.get(unit, 60)

    async def timer_command(self, message: Message, args_list: list, args_raw: str) -> None:
        """.timer add <интервал> <текст> — создать циклотаймер в этом чате
        .timer del <id> — удалить
        .timer list — список активных таймеров"""
        if not args_list:
            await utils.answer(
                message,
                "🔴 <b>Использование:</b>\n"
                "      <code>.timer add 30м текст</code>\n"
                "      <code>.timer del &lt;id&gt;</code>\n"
                "      <code>.timer list</code>"
            )
            return

        sub = args_list[0].lower()
        timers = self.db.get('saltwort', 'Timers') or {}

        if sub == 'add':
            if len(args_list) < 3:
                await utils.answer(
                    message,
                    "🔴 <b>Нужно:</b> <code>.timer add &lt;интервал&gt; &lt;текст&gt;</code>"
                )
                return

            interval = self._parse_duration(args_list[1])
            if not interval or interval < 5:
                await utils.answer(
                    message,
                    "🔴 <b>Не понял интервал.</b> Примеры: <code>30</code> (мин), "
                    "<code>2ч</code>, <code>90с</code>, <code>1д</code>"
                )
                return

            timer_text = args_raw.split(None, 2)[2]
            tid = str(int(datetime.now(pytz.timezone("Europe/Moscow")).timestamp()))
            timers[tid] = {
                'chat_id': message.chat_id,
                'interval': interval,
                'text': timer_text,
                'last_sent': 0,  # 0 => отправит первое сообщение на ближайшем тике
            }
            self.db.set('saltwort', 'Timers', timers)
            await utils.answer(
                message,
                f"🟢 <b>Таймер создан</b>\n      id: <code>{tid}</code>\n"
                f"      Каждые <code>{self._format_timedelta(timedelta(seconds=interval))}</code>"
            )
            return

        if sub == 'del':
            if len(args_list) < 2:
                await utils.answer(message, "🔴 <b>Нужно:</b> <code>.timer del &lt;id&gt;</code>")
                return
            tid = args_list[1]
            if tid not in timers:
                await utils.answer(message, f"🔴 <b>Таймер {tid} не найден</b>")
                return
            del timers[tid]
            self.db.set('saltwort', 'Timers', timers)
            await utils.answer(message, f"🟢 <b>Таймер {tid} удалён</b>")
            return

        if sub == 'list':
            if not timers:
                await utils.answer(message, "🔘 <b>Активных таймеров нет</b>")
                return
            sms = "🟢 <b>Таймеры:</b>\n"
            for tid, t in timers.items():
                preview = t['text'] if len(t['text']) <= 40 else t['text'][:37] + '...'
                sms += (
                    f"      <code>{tid}</code> | чат <code>{t['chat_id']}</code> | "
                    f"каждые {self._format_timedelta(timedelta(seconds=t['interval']))} | "
                    f"«{html.escape(preview)}»\n"
                )
            await utils.answer(message, sms)
            return

        await utils.answer(message, "🔴 <b>Неизвестная подкоманда.</b> add / del / list")

    @loader.loop(interval=15, autostart=True)
    async def timers_loop(self):
        """Раз в 15 секунд проверяет циклотаймеры и рассылает те, чей
        интервал истёк."""
        try:
            timers = self.db.get('saltwort', 'Timers') or {}
            if not timers:
                return

            now = datetime.now(pytz.timezone("Europe/Moscow")).timestamp()
            changed = False
            for tid, t in timers.items():
                if now - t.get('last_sent', 0) >= t['interval']:
                    try:
                        await self.client.send_message(t['chat_id'], t['text'])
                    except Exception:
                        pass
                    t['last_sent'] = now
                    changed = True

            if changed:
                self.db.set('saltwort', 'Timers', timers)
        except Exception:
            pass

    async def excl_command(self, message: Message, args_list: list) -> None:
        """.искл add <id> / .искл del <id> / .искл list — исключения только
        для режима "АвтоБио": такие id никогда не атакуются автоматически,
        даже если они в плюсе. На ручные команды (.зз и т.д.) не влияет."""
        if not args_list:
            await utils.answer(
                message,
                "🔴 <b>Использование:</b>\n"
                "      <code>.искл add &lt;id&gt;</code>\n"
                "      <code>.искл del &lt;id&gt;</code>\n"
                "      <code>.искл list</code>"
            )
            return

        sub = args_list[0].lower()
        excluded = self.db.get('saltwort', 'AutoBioExclude') or []

        if sub == 'add':
            if len(args_list) < 2:
                await utils.answer(message, "🔴 <b>Нужно:</b> <code>.искл add &lt;id&gt;</code>")
                return
            uid = re.sub(r'\D', '', args_list[1])  # берём только цифры (на случай ссылки/@)
            if not uid:
                await utils.answer(message, "🔴 <b>Не нашёл числовой id</b>")
                return
            if uid in excluded:
                await utils.answer(message, f"🔘 <code>{uid}</code> уже в исключениях")
                return
            excluded.append(uid)
            self.db.set('saltwort', 'AutoBioExclude', excluded)
            await utils.answer(
                message,
                f"🟢 <code>{uid}</code> добавлен в исключения АвтоБио"
            )
            return

        if sub == 'del':
            if len(args_list) < 2:
                await utils.answer(message, "🔴 <b>Нужно:</b> <code>.искл del &lt;id&gt;</code>")
                return
            uid = re.sub(r'\D', '', args_list[1])
            if uid not in excluded:
                await utils.answer(message, f"🔴 <code>{uid}</code> не найден в исключениях")
                return
            excluded.remove(uid)
            self.db.set('saltwort', 'AutoBioExclude', excluded)
            await utils.answer(message, f"🟢 <code>{uid}</code> убран из исключений")
            return

        if sub == 'list':
            if not excluded:
                await utils.answer(message, "🔘 <b>Исключений нет</b>")
                return
            sms = "🟢 <b>Исключения АвтоБио:</b>\n"
            for uid in excluded:
                sms += f"      <a href='tg://openmessage?user_id={uid}'>{uid}</a>\n"
            await utils.answer(message, sms)
            return

        await utils.answer(message, "🔴 <b>Неизвестная подкоманда.</b> add / del / list")

    async def export_command(self, message: Message) -> None:
        """.export — экспорт зарлиста в JSON формата обмена (schema_version 1):
        {"schema_version", "exported_at", "owner_telegram_id", "victims":
        [{"telegram_id", "infections": [...]}], ...}. Записи без числового
        id (голые имена из .import) в файл не попадают."""
        me = await self.client.get_me()
        payload, skipped = self._build_export(me.id)

        if not payload['victims']:
            await utils.answer(message, "🔴 <b>Нечего экспортировать — валидных id нет</b>")
            return

        stamp = datetime.now(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
        path = f"/tmp/victims_{me.id}_{stamp}.json"
        with open(path, 'w', encoding='utf-8') as f:
            Json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))

        caption = (f"🟢 <b>Экспортировано жертв:</b> {payload['victims_count']}\n"
                   f"🧬 <b>Заражений:</b> {payload['infections_count']}")
        if skipped:
            caption += f"\n⚠️ <b>Пропущено (без id):</b> {skipped}"

        try:
            await self.client.send_file(message.chat_id, path, caption=caption)
        finally:
            if os.path.exists(path):
                os.remove(path)

    async def _import_json(self, message: Message, reply: Message) -> None:
        try:
            data = await self._read_json_file(reply)
        except Exception as e:
            await utils.answer(message, f"🔴 <b>Не смог прочитать JSON:</b> "
                                        f"<code>{html.escape(str(e))}</code>")
            return

        if not (isinstance(data, dict) and isinstance(data.get('victims'), list)):
            await utils.answer(
                message,
                "🔴 <b>Нужен файл формата экспорта</b> (поле victims). Старый список "
                "[\"@id\", ...] не содержит опыта и дат — импортировать нечего, "
                "его можно только проверить через (ник) зз нов"
            )
            return

        me = await self.client.get_me()
        st = self._merge_import(data, me.id)

        sms = ("🟢 <b>Импорт завершён</b>\n"
               f"      Добавлено: <code>{st['added']}</code>\n"
               f"      Обновлено: <code>{st['updated']}</code>\n"
               f"      Оставлено (в бд свежее): <code>{st['kept']}</code>\n"
               f"      Пропущено (битые записи): <code>{st['invalid']}</code>")
        owner = data.get('owner_telegram_id')
        if owner and str(owner) != str(me.id):
            sms += (f"\n⚠️ <b>Файл экспортирован с другого аккаунта</b> "
                    f"(<code>{owner}</code>)")
        await utils.answer(message, sms)

    async def import_command(self, message: Message, reply: Message) -> None:
        """Импортирует жертв из списка вида '1. Имя | +N | до ДД.ММ.ГГГГ'
        (реплай на сообщение со списком, обычно это ответ внешнего бота на
        команду показа всех больных вашим патогеном)."""
        if not reply:
            await utils.answer(
                message,
                "🔴 <b>Нужно ответить (реплай) на сообщение со списком жертв или JSON-файл</b>"
            )
            return

        if reply.file and (reply.file.name or '').lower().endswith('.json'):
            await self._import_json(message, reply)
            return

        raw_text = reply.raw_text or ''
        lines = raw_text.splitlines()

        # Ссылки/mention-сущности в порядке появления в тексте: (текст, user_id)
        # Строки без ссылки (голый ник без привязанного аккаунта) просто не
        # получат ничего в этой очереди и импортируются по тексту имени.
        ent_queue = []
        for ent, ent_text in reply.get_entities_text():
            uid = None
            if isinstance(ent, MEMN):
                uid = ent.user_id
            elif isinstance(ent, METU):
                m = re.search(r'user[_]?id=(\d+)', ent.url)
                if m:
                    uid = int(m.group(1))
            if uid is not None:
                ent_queue.append((ent_text, uid))

        line_re = re.compile(
            r'^\s*\d+\.\s*(?P<name>.+?)\s*\|\s*\+(?P<count>[0-9.,]+[kк]?)\s*\|\s*'
            r'до\s+(?P<date>\d{1,2}\.\d{1,2}\.\d{2,4})\s*$'
        )

        infection = self.db.get("NumMod", "infection") or {}
        infect_before = self.db.get('saltwort', 'InfectionBefore') or {}

        imported = 0
        skipped = 0
        ent_i = 0

        for line in lines:
            m = line_re.match(line)
            if not m:
                continue

            name = m.group('name').strip()
            count = m.group('count')
            date_str = m.group('date')

            # Если у следующей неиспользованной ссылки текст входит в имя этой
            # строки — значит эта ссылка относится к текущей жертве
            user_key = None
            if ent_i < len(ent_queue):
                ent_text, uid = ent_queue[ent_i]
                if ent_text and ent_text in name:
                    user_key = f'@{uid}'
                    ent_i += 1

            if not user_key:
                # нет привязанного id — импортируем по имени как есть,
                # убрав служебный префикс "им. "
                clean_name = re.sub(r'^им\.\s*', '', name, flags=re.IGNORECASE).strip()
                user_key = f'@{clean_name}' if clean_name else None

            if not user_key:
                skipped += 1
                continue

            try:
                day, month, year = date_str.split('.')
                short_date = f"{int(day):02d}.{int(month):02d}"
            except Exception:
                skipped += 1
                continue

            infection[user_key] = [str(count), short_date]
            infect_before[user_key] = date_str
            imported += 1

        self.db.set("NumMod", "infection", infection)
        self.db.set('saltwort', 'InfectionBefore', infect_before)

        await utils.answer(
            message,
            "🟢 <b>Импорт завершён</b>\n"
            f"      Добавлено/обновлено: <code>{imported}</code>\n"
            f"      Пропущено строк: <code>{skipped}</code>"
        )

# -----------------------Commands-------------------

    async def солянкаcmd(self, message: Message) -> None:
        """Помощь по модулю"""
        args_raw = utils.get_args_raw(message)
        infection = self.db.get("NumMod", "infection")
        famous_users = self.db.get('saltwort', 'FamousUsers')
        dov_users = self.db.get("saltwort", "DovUsers")
        if not args_raw:
            pref = await self.get_pref()
            commands = ""
            comm = self.strings("сommands")
            for com, desc in comm.items():
                commands += f"▫️ <code>{pref}{com}</code> {desc} \n"
                text = self.strings("bio.commands").format(
                    pref, commands)

        elif args_raw.lower() == "зарлист":
            text = self.strings("bio.zar").format()
        elif args_raw.lower() == "навыки":
            text = self.strings("bio.skill").format()
        elif args_raw.lower() == 'инфо':
            exps = int(sum([eval(i[0].replace(",", ".").replace(
                'k', '*1000')) for i in list(infection.values())]))
            text = self.strings("bio.info").format(
                len(infection.keys()),
                '{:,}'.format(exps).replace(',', ' '),
                len(famous_users.keys()),
                len(dov_users.keys())
            )

        else:
            await utils.answer(message, "Что то явно не так")
            return
        await self.send(text, message)
        return

    # @loader.watcher("only_pm", "only_messages")
    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return

        text = message.text
        reply = await message.get_reply_message()
        sndr_id = message.sender_id
        me = await self.client.get_me()
        pref = await self.get_pref()
        args_list, args_raw = utils.get_args(
            message), utils.get_args_raw(message)
        infection = self.db.get("NumMod", "infection")
        msg_splitlines_1 = message.raw_text.splitlines()[0] if text else ''

        # /123456 — запуск заражений по списку (раз в 1.5 мин), /stop — остановка.
        # Работает только на ваши собственные сообщения
        if str(sndr_id) == str(me.id) and message.raw_text:
            cmd_text = message.raw_text.strip().lower()
            if re.fullmatch(r'/\d{6}', cmd_text) or cmd_text == '/stop':
                await self._mass_command(message, cmd_text)
                return

        # Кэшируем расположение сообщения "ТОП ЛАБОРАТОРИЙ ПО БИО-ОПЫТУ..." —
        # его переиспользует фоновый режим "АвтоБио" (сообщение обычно
        # обновляется правкой раз в минуту, поэтому храним chat_id+msg_id,
        # а не сам текст, и перечитываем свежую версию по требованию)
        if 'ТОП ЛАБОРАТОРИЙ' in msg_splitlines_1:
            self.db.set('saltwort', 'LastBiotop',
                         {'chat_id': message.chat_id, 'msg_id': message.id})

        # Подтверждение "Вакцина излечила вас от горячки" — по нему снимаем
        # флаг SelfInfectedUntil, вместо того чтобы снимать его оптимистично
        # сразу после отправки ".купить вакцину" (это ненадёжно, вдруг не
        # хватило био-ресурса и покупка не прошла). "У вас нет горячки" —
        # доп. страховка на случай, если флаг всё же завис ошибочно.
        if 'Вакцина излечила вас' in (text or '') or 'нет горячки' in (text or '').lower():
            self.db.set('saltwort', 'SelfInfectedUntil', None)

        # Относится к автозаписе жертв
        # Берем айди/юзернейм из собщения пользователя и сохраняем в бд (в бд будет лежать айди зараженного)
        if mes := re.fullmatch(r'(заразить ) (?P<lvl>[1-9]?[0]?\s)?((https?://)?t\.me/|@)([0-9a-z_A-Z]+)', msg_splitlines_1.lower()):
            if not self.config["Автозапись жертв"]:
                return
            if str(me.id) != str(sndr_id):
                return
            user = mes.group(5)
            await self.save_last_infect(user)
            return

        # Автозапись жертв
        # ФИКС (2-й проход): вся предыдущая логика опиралась на то, что
        # message.text (=`text`) содержит HTML-разметку вида <a href="...">,
        # но это зависит от parse_mode клиента и на практике, судя по всему,
        # НЕ происходит — из-за этого исходный `if mes := re.search(r'<a href=...')`
        # вообще никогда не матчился, и весь блок ниже просто не выполнялся,
        # что и объясняет "ничего не поменялось" после первого фикса.
        # Теперь детектируем отчёт о заражении по обычному тексту (raw_text,
        # без HTML), а ссылки на атакующего/жертву берём напрямую из entities
        # сообщения через message.get_entities_text() — это не зависит от
        # HTML-рендеринга вообще.
        raw_text = message.raw_text or ''

        # ИСКЛЮЧЕНИЕ: сообщение вида "Служба безопасности Вашей лаборатории
        # докладывает: Организатор заражения: ..." — это отчёт о том, что
        # КТО-ТО ДРУГОЙ заразил ВАС, а не о том, что вы кого-то заразили.
        # Оно тоже содержит "подверг заражению", поэтому без этой проверки
        # ошибочно попало бы в зарлист как будто это ваша победа.
        if 'Служба безопасности Вашей лаборатории докладывает' in raw_text:
            return
        if re.search(r'подвер.{1,3}\s*заражению', raw_text):

            if not self.config["Автозапись жертв"]:
                if self.config["отладка"]:
                    await message.reply(
                    "🐞 DEBUG: сообщение похоже на отчёт о заражении, но настройка "
                    "«Автозапись жертв» выключена. Включите её: .config Saltwort"
                )
                return

            # ФИКС (3-й проход): живой DEBUG показал, что реальные уведомления
            # приходят из чата бота «Biowars» (id 8644732229) — это тот самый id,
            # что был захардкожен в оригинальном коде автора. Разрешаем оба
            # варианта: чат бота Biowars и Избранное (на случай пересланных копий).
            BIOWAR_CHAT_IDS = self.BIOWAR_CHAT_IDS
            if message.chat_id != me.id and message.chat_id not in BIOWAR_CHAT_IDS:
                if self.config["отладка"]:
                    await message.reply(
                    f"🐞 DEBUG: chat_id сообщения ({message.chat_id}) не подходит "
                    f"(ожидался ваш id {me.id} или чат бота Biowars {BIOWAR_CHAT_IDS})"
                )
                return

            link_ids = []  # id пользователей из всех text_link-ссылок сообщения, по порядку
            for ent, ent_text in message.get_entities_text():
                if isinstance(ent, METU):
                    idm = re.search(r'openmessage\?user_id=(\d+)', ent.url)
                    if idm:
                        link_ids.append(idm.group(1))
                    elif me.username and ent.url.lower().rstrip('/').endswith(
                            '/' + me.username.lower()):
                        link_ids.append(str(me.id))

            # ФИКС (4-й проход): сообщение имеет вид "<атакующий> подверг
            # заражению ... <жертва>" — раньше код проверял, встречается ли
            # ваш id ГДЕ УГОДНО среди ссылок, из-за чего когда вас заражал
            # КТО-ТО ДРУГОЙ (вы = жертва, ваш id идёт ВТОРЫМ), это ошибочно
            # сохранялось так, будто это вы кого-то заразили. Атакующий — это
            # всегда ПЕРВАЯ ссылка в сообщении.
            if not link_ids or link_ids[0] != str(me.id):
                if str(me.id) in link_ids[1:]:
                    # Вас заразили — запоминаем это для режима "АвтоБио"
                    # (перед атакой нужно проверить, не заражены ли вы сами).
                    # ВАЖНО: вакцина лечит именно "Горячку" (длится минуты),
                    # а НЕ многодневное "Заражение" — раньше тут ошибочно
                    # бралась длительность заражения (дни), из-за чего флаг
                    # висел на целый день после того, как горячка уже прошла.
                    m = re.search(r'Горячка на (\d+)\s*минут', raw_text)
                    if m:
                        self.db.set(
                            'saltwort', 'SelfInfectedUntil',
                            datetime.now(pytz.timezone("Europe/Moscow")).timestamp()
                            + int(m.group(1)) * 60
                        )
                if self.config["отладка"]:
                    await message.reply(
                        f"🐞 DEBUG: атакующий в сообщении — не вы (id {link_ids[0] if link_ids else '?'}), "
                        f"а ваш id {me.id}. Пропускаю (не ваша победа)."
                    )
                return

            victim_ids = link_ids[1:]

            vremya = datetime.now(pytz.timezone("Europe/Moscow"))
            msg_text = raw_text

#Леталка в отчете о заражении

            # ФИКС: раньше в regex попадали "магические" пробелы от отступа кода
            # (буквальные 12 пробелов после \n), которых нет в реальном тексте
            # сообщения — из-за этого regex никогда не находил совпадение.
            reg = r"Заражение на (\d+) д[еньяей]{1,2}.*?\+([0-9.,]+(?:[kк])?) био-опыта"
            info = re.search(reg, msg_text, flags=re.DOTALL)

            if not info:
                if self.config["отладка"]:
                    await message.reply(
                    "🐞 DEBUG: не нашёл в тексте 'Заражение на N дней' / '+N био-опыта':\n\n"
                    f"<code>{html.escape(msg_text)}</code>"
                )
                return

            letal = int(info.group(1))
            count = info.group(2)

            if victim_ids:
                # ФИКС: раньше искалась несуществующая подстрока 'user?id=' (в
                # реальной ссылке 'user_id=' — с подчёркиванием, а не вопросом),
                # а даже при правильном поиске .index() взял бы ПЕРВУЮ ссылку —
                # а это ссылка на вас, а не на жертву. Теперь берём id жертвы
                # напрямую из entities, исключив свой собственный id.
                user = victim_ids[-1]
                self.db.set('saltwort', 'LastInfect', None)

            else:  # Если нет ссылки на жертву то берем ее из бд
                # Если в заражение от бота есть реплай, то берем айди из реплая, иначе из бд
                if reply:
                    t = reply.raw_text.splitlines()[0]
                    if '@' in t:
                        s = t.find('@')
                        user = t[s:].replace('@', '')
                    else:
                        s = t.find('https://t.me/')
                        user = t[s:].replace('https://t.me/', '')

                    if not user.isdigit():
                        user = await self.return_user(username=user)

                    self.db.set('saltwort', 'LastInfect', None)

                else:
                    # Берем данные о последнем зараженном
                    # Если статус Тру(тоесть еще не заражли его)
                    # То берем его айди и записываем его в дб
                    user = self.db.get('saltwort', 'LastInfect')
                    self.db.set('saltwort', 'LastInfect', None)

            if not user:
                if self.config["отладка"]:
                    await message.reply(
                    "🐞 DEBUG: не удалось определить жертву (нет ссылки на неё в "
                    "сообщении, нет реплая и пусто LastInfect в бд)"
                )
                return
            letal_in_db = self.db.get('saltwort', 'YourLetal')
            user = '@' + str(user)
            if letal != letal_in_db:
                self.db.set('saltwort', 'YourLetal', letal)

            vremya1 = vremya.strftime("%d.%m")
            vremya_do = vremya.strftime("%d.%m") if letal == 1 else (vremya +
                                                                     timedelta(days=int(letal))).strftime("%d.%m.%Y")

            # Хранит данные до какого числа заражение
            # Используется для того чтобы не портить структуры зарлиста наммода
            infectBefore = self.db.get('saltwort', 'InfectionBefore')
            infectBefore[user] = vremya_do

            self.db.set('saltwort', 'InfectionBefore', infectBefore)
            old_count = ' ' + str(infection[user][0]) if user in infection else ''
            if user in infection:
                del infection[user]

            infection[user] = [str(count), vremya1]

            self.db.set("NumMod", "infection", infection)

            # Заносим кулдаун именно на этого зараженного (user уже в формате
            # '@id'/'@имя' — том же ключе, что используется в infection),
            # а не глобально — заражать других это не мешает.
            self._set_cooldown(user)

            if message.chat_id != -1316297204:
                cooldown_str = self._format_timedelta(
                    timedelta(hours=self.INFECT_COOLDOWN_HOURS))
                await message.reply(
                    self.strings('zar.save').format(user, old_count, count, vremya_do) +
                    f"\n⏳ <b>Кулдаун на {user}:</b>\n      Повторно заразить можно через "
                    f"<code>{cooldown_str}</code>"
                )

            return

# Чат айди локдауна
        if message.chat_id == -1316297204:
            return

        if re.fullmatch(r"жд\s@\d{3,12}.{,10}", text, flags=re.ASCII):
            if str(sndr_id) != (me.id):
                return

        elif re.fullmatch(r"жл\s@\d{3,12}", text, flags=re.ASCII):
            if str(sndr_id) != str(me.id):
                return

        # -----------------------Commands-------------------
        owners = list(getattr(self.client.dispatcher.security, "owner"))

        if text.startswith(pref) and sndr_id in owners:
            command = text.replace(pref, "").split()[0].lower()
            if command not in self.strings("сommands"):
                return

#            if command == "z":
#                await self.z_command(message, args_raw, text, reply)
#                return
            elif command == "id":
                await self.id_command(message, args_raw, reply)
                return
            elif command == "ids":
                await self.ids_command(message, args_raw, reply)
                return
            elif command == "dov":
                await self.dov_command(message, args_list, args_raw, reply)
                return
#            elif command == 'zz':
#                await self.bio_command(reply, me)
#                return
            elif command == 'nik':
                await self.nik_command(message, args_list, args_raw)
                return
            elif command == 'pref':
                await self.pref_command(message, args_list)
                return
            elif command == 'import':
                await self.import_command(message, reply)
                return
            elif command == 'timer':
                await self.timer_command(message, args_list, args_raw)
                return
            elif command == 'искл':
                await self.excl_command(message, args_list)
                return
            elif command == 'export':
                await self.export_command(message)
                return

        numfilter = self.db.get("NumMod", "numfilter")
        if self.config["Вкл/Выкл доверки"] and str(sndr_id) in self.db.get("saltwort", "DovUsers").keys() and numfilter['filter']:
            nik = numfilter['filter'].lower()

            if not text.lower().startswith(nik):
                return

            dov_users = self.db.get("saltwort", "DovUsers")

            level = dov_users[str(sndr_id)]
            # убираем из текста имя доверки

            # text = text.replace(
            #    f"{nik} ", '', 1).replace(f'{nik}', '', 1)

            # Сделано из-за небольших проблем к командой replace
            # Оно может случайно и удалить часть вводимой команды
            # Пример: вир +вирусы
            # Убирало вир и убирало вир из +вирусы, в итоге осталовалось +усы

            text = text[len(
                nik)+1:] if f'{nik} ' in text.lower() else text[len(nik):]
            text_low = text.lower()
            text_norm = text

            args_raw = text
            args_list = text.split(' ')

# Чек жертвы
            if level >= 1:
                if re.fullmatch('з', text_norm) and reply:
                    rtext = reply.raw_text

                    if '@' in rtext:
                        s = rtext.find('@')
                        a = rtext[s:].split('\n')
                        a = ' '.join(a).split(' ')
                        user_id = a[0]

                    else:
                        user_id = '@' + str(reply.sender_id)

                    if not user_id[1:].isdigit():
                        user_id = '@' + str(await self.return_user(username=user_id))

                    if user_id in infection:
                        user = infection[user_id]
                        infectBefore = self.db.get(
                            'saltwort', 'InfectionBefore')

                        zar_do = infectBefore[user_id] if user_id in infectBefore else 'Неизвестно'
                        niks = self.db.get('saltwort', 'UsersNik')
                        if str(user_id[1:]) in niks.keys():
                            nik = niks[str(user_id[1:])]
                            usr = f'<a href="tg://openmessage?user_id={user_id[1:]}">{nik}</a>'
                        else:
                            usr = f'<code>{user_id}</code>'

                        await message.reply(self.strings('zar.search').format(usr, user[0], user[1], zar_do))
                    else:
                        await message.reply(self.strings('z.nf').format(user_id))
                    return

# Чек жертвы
                elif send_mesа := re.search(r"з\s", text):
                    en = message.entities[0]
                    link = message.raw_text[en.offset:en.offset+en.length]
                    user_id = await self._handler_link(link) if '@' not in link else link
                    if not user_id[1:].isdigit():
                        user_id = '@' + str(await self.return_user(username=user_id))

                    if user_id in infection:
                        user = infection[user_id]
                        infectBefore = self.db.get(
                            'saltwort', 'InfectionBefore')

                        zar_do = infectBefore[user_id] if user_id in infectBefore else 'Неизвестно'

                        niks = self.db.get('saltwort', 'UsersNik')
                        if str(user_id[1:]) in niks.keys():
                            nik = niks[str(user_id[1:])]
                            usr = f'<a href="tg://openmessage?user_id={user_id[1:]}">{nik}</a>'
                        else:
                            usr = f'<code>{user_id}</code>'

                        await message.reply(self.strings('zar.search').format(usr, user[0], user[1], zar_do))
                    else:
                        await message.reply(self.strings('z.nf').format(user_id))

# калькулятор
                elif mes := re.fullmatch(r'(калькулятор|к|калк) (\w+) (\d+(-\d+)?)', text_low):

                    skill = mes.group(2)
                    n = mes.group(3).split('-')

                    if re.search(r"зз|зараз[уканость]{,5}", text_low,  flags=re.ASCII):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['zar']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Заразность</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return

                    elif re.search(r"(?P<let>летал[укаьность]{,5})", text_low, flags=re.ASCII):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['letal']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Летальность</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return

                    elif re.search(r"(?P<pat>пат[огены]{,5})", text_low, flags=re.ASCII):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['pat']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Патогены</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return

                    elif re.search(r"(?P<kvala>квал[улаификация]{,8}|разраб[откау]{,4})", text_low, flags=re.ASCII):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['kvala']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Квалификация</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return

                    elif re.search(r"(?P<imun>иммун[уеитетка]{,4}|имун[уеитетка]{,4})", text_low, flags=re.ASCII):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['imun']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Иммунитет</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return

                    elif re.search(r'(?P<sb>сб|безопасно[сть]{,3}|служб[ау]{,2})', text_low):
                        n1, n2 = int(n[0]), int(n[1])
                        step = self.strings('calc_formul')['sb']
                        total = 0
                        for i in range(n1+1, n2+1):
                            total += int(i ** step)
                        total = '{:,}'.format(total).replace(',', ' ')

                        text_msg = f'🟢 <b>Прокачка навыка:</b>\n      <i>Безопасность</i>\n🟠 <b>Уровень:</b>\n      {n1} до {n2}\n🟣 <b>Био-ресурсов:</b>\n      {total}'
                        await message.reply(text_msg)
                        return
                    else:
                        return

# Заражение
                elif inf := re.search(
                    r"(бей{,3}|кус[ьайни]{,3}|зарази[тьть]{,3}|еб[ниажшь]{,3}|уеб[иаошть]{,3}|опуст[и]{,3}|организуй горячку{,3})",
                    text_low, flags=re.ASCII
                ):
                    inf = inf.group(1)

                    text = text.replace(
                        f"{inf} ", '').replace(inf, '')

                    args_raw = text
                    args_list = args_raw.split(' ')

                    if args_raw.lower() == 'стоп':
                        status = self.db.get("saltwort", "infStatus")
                        if status:
                            self.db.set("saltwort", "infStatus", False)
                            await utils.answer(message, '🟢 <b>Заражения \n      остановлены</b>')
                            return
                        else:
                            await utils.answer(message, '⭕ <b>Заражения \n      не запущены</b>')
                            return

                    if args_list[0] == 'интервал':
                        if args_list[1] and args_list[1].isdigit():
                            time = float(args_list[1].replace(',', '.'))
                            self.db.set("saltwort", "infInterval", time)
                            await utils.answer(message, f'🟢 <b>Интервал \n      установлен: \n      {time} с</b>')
                            return
                        else:
                            await utils.answer(message, f'⭕ <b>Укажите \n      интервал\n      в секундах</b>')
                            return
                    if send_mesа := re.search(r"(?P<lvl>[1-9]?[0]?\s)?(?P<link>@[0-9a-zA-Z_]+|(?:https?://)?t\.me/[0-9a-zA-Z_]+|tg://openmessage\?user_id=(?P<id>[0-9]+))", text):
                        if self.db.get("saltwort", "infStatus"):
                            await message.reply('⭕ <b>Заражения \n      не завершены</b>')
                            return

                        send_mesа = send_mesа.groupdict()

                        send_mesа['link'], send_mesа['id'] = '@' + \
                            send_mesа['id'] if send_mesа['id'] else send_mesа['link'], ''
                        send_mesа['lvl'] = send_mesа['lvl'] or ''
                        mes = ''.join(send_mesа.values())

                        user = send_mesа['id'] if send_mesа['id'] else send_mesа['link']

                        user = user.replace(
                            '@', '').replace('https://t.me/', '')

                        await self.save_last_infect(user)
                        self.db.set("saltwort", "infStatus", True)
                        await message.reply(f'заразить  {mes}')
                        self.db.set("saltwort", "infStatus", False)
                        return

                    await self.z_command(message, args_raw, text, reply)
                    return

                elif re.fullmatch(r"вак[цинау]{,3}|леч[ись]{,2}|хи[лльсяйинг]{,2}|лек[арство]{,2}", text_low, flags=re.ASCII):
                    await message.reply('.купить вакцину')
                    return

#                if re.fullmatch(r'мл', text):
#                    await message.respond('минилаб')

                if re.fullmatch(r"мл", text, flags=re.ASCII):  # регулярка
                    lab_raw = await self.message_q(  # отправляет сообщение боту и       возвращает текст
                        f"лаб",
                        8644732229,
                        mark_read=True,
                        delete=True,
                    )
                    if lab_raw == 'Timeout':
                        await message.respond('Время ожидания истекло')
                        return

                    lab_lines = lab_raw.splitlines() 
                    sms = ""
                    for i in lab_lines:
                        if "🧪 Патогенов:" in i:
                            s = i.replace("🧪 Патогенов:", "")
                            sms += f"🟢 <b>Патогенов:</b>\n     {s}\n"
                        if "⏳ До нового патогена:" in i:
                            s = i.replace("⏳ До нового патогена:", "")
                            sms += f"🟠      <b>Следующий патоген через:</b>\n     {s}\n"
                        if "☣️ Био-опыт:" in i:
                            s = i.replace("☣️ Био-опыт:", "")
                            sms += f"☣️ <b>Био-опыт:</b>\n     {s}\n"
                        if "🧬 Био-ресурс:" in i:
                            s = i.replace("🧬 Био-ресурс:", "")
                            sms += f"🧬 <b>Био-ресурс:</b>\n     {s}\n"
                        if "🥴 У вас горячка" in i:
                            s = i.replace("🥴 У вас горячка", "")
                            sms += f"️🔴 У вас горячка\n     {s}\n"
                    await message.respond(sms)
                    return

# Чек списка
                elif (zz_m := re.fullmatch(r'(зз|био)(?:\s+(нов\w*))?', args_raw.lower().strip())):
                    if not reply:
                        await utils.answer(message, self.strings('no.reply'))
                        return
                    await self.bio_command(message, reply, me, only_new=bool(zz_m.group(2)))
                    return

# СБ 
                elif args_raw == 'сб':

                    if not reply:
                        await utils.answer(message, self.strings('no.reply'))
                        return

                    if re.search(r"👨🏻‍🔬 Была проведена операция заражения", reply.text):
                        entities = reply.get_entities_text()

                        infect = await self._handler_link(entities[1][0].url)
                        infect = infect.replace("@", "")

                        # except:
                        # infect = await self._handler_link(entities[0][0].url).replace("@","")

                        if not infect.isdigit():
                            username = infect
                            infect = await self.return_user(username)
                        if not infect:
                            return

                        if '@' + str(infect) in infection:
                            user = infection['@' + str(infect)]
                            infectBefore = self.db.get(
                                'saltwort', 'InfectionBefore')

                            zar_do = infectBefore['@' + str(
                                infect)] if infect in infectBefore.keys() else 'Неизвестно'
                            niks = self.db.get('saltwort', 'UsersNik')
                            if str(infect) in niks.keys():
                                nik = niks[str(infect)]
                                usr = f'<a href="tg://openmessage?user_id={infect}">{nik}</a>'
                            else:
                                usr = f'<code>@{infect}</code>'

                            await message.reply(self.strings('zar.search').format(usr, user[0], user[1], zar_do))
                        else:
                            # await message.reply(f'{self.strings("z.nf").format('@' + str(infect)}'
                            await message.reply(self.strings('z.nf').format("@" + str(infect)))
                    return
                # чек жертв с помощью дова
                # Пример: вир з @777000
            #    elif re.search(r"(?P<zarlist>з\s(?P<link>@[0-9a-z_]+|(?:https?# ://)?t\.me/[0-9a-z_]+|tg://openmessage\?user_id=(?P<id>[0-9]+))", # text, flags=re.ASCII):
                    # pass
#            if level >= 2:
                # Запись жертв с помощью дова
                # Пример: вир жд @777000
                if re.search(r"жд\s@\d{3,12}.{,10}", text_low, flags=re.ASCII):
                    pass

# Чек ежедневки
                elif re.fullmatch(r"еж[ау]{,2}", text_low, flags=re.ASCII):
                    await message.reply('жертвы')

                elif send_mesa := re.fullmatch(r"(топ жертв[ыау]{,2} )(?P<list>[0-9]{,10})?", text_low, flags=re.ASCII) or re.fullmatch(r"(топ жертв[ыау]{,2})", text_low, flags=re.ASCII):

                    try:
                        send_mesa = send_mesa.groupdict()
                        n = int(send_mesa['list'])
                    except:
                        n = 1

                    await self.get_top_zhertv(message=message, num_list=n)
                    return

                elif send_mesa := re.fullmatch(r"(жертв[ыау]{,2} )(?P<list>[0-9]{,10})?", text_low, flags=re.ASCII) or re.fullmatch(r"(жертв[ыау]{,2})", text_low, flags=re.ASCII):
                    try:
                        send_mesa = send_mesa.groupdict()
                        n = int(send_mesa['list'])
                    except:
                        n = 1

                    await self.get_zhertv(message=message, num_list=n)
                    return
            # Навыки через доверку: "+навык N" — стоимость, "++навык N" — прокачка
            # (N от 1 до 5 уровней, по умолчанию 1). Стоит ПЕРЕД старой веткой
            # прокачки: её re.search ловил "+заразность 3" и отправлял прокачку.
            if level >= 2:
                skill_m = re.fullmatch(
                    r'(\+{1,2})\s*(?P<skill>[а-яё]+)(?:\s*\(?\s*(?P<n>\d+)\s*\)?)?',
                    text_low.strip())
                skill_name = None
                if skill_m:
                    word = skill_m.group('skill')
                    for pattern, canon in (
                        (r'зараз\w*|зар', 'заразность'),
                        (r'им+ун\w*|имун\w*', 'иммунитет'),
                        (r'пат\w*', 'патоген'),
                        (r'летал\w*|лет', 'летальность'),
                        (r'безопасн\w*|сб|служб\w*', 'безопасность'),
                    ):
                        if re.fullmatch(pattern, word):
                            skill_name = canon
                            break

                if skill_name:
                    n = int(skill_m.group('n') or 1)
                    if not 1 <= n <= 5:
                        await message.reply('🔴 <b>Уровней можно от 1 до 5</b>')
                        return
                    prefix = '++' if skill_m.group(1) == '++' else '+'
                    await message.reply(f'{prefix}{skill_name} {n}')
                    return

            if level == 2:

                if re.fullmatch(r"фл", text, flags=re.ASCII):  # регулярка
                    lab_raw = await self.message_q(  # отправляет сообщение боту и       возвращает текст
                        f"лаб",
                        8644732229,
                        mark_read=True,
                        delete=True,
                    )
                    if lab_raw == 'Timeout':
                        await message.respond('⭕  <b>Время\n      ожидания\n      истекло</b>')
                        return

                    lab_lines = lab_raw.splitlines() 
                    sms = ""
                    for i in lab_lines:
                        if "🦠 Информация о вирусе:" in i:
                            s = i.replace("🦠 Информация о вирусе:","")
                            sms += f"🏷 <b>Патоген:</b> {s}\n\n"
                        if "👺 Владелец:" in i:
                            s = i.replace("👺 Владелец:", "")
                            sms += f"😎 <b>Руководитель</b> {s}\n\n"  
                        if "🧪 Патогенов:" in i:
                            s = i.replace("🧪 Патогенов", "")
                            sms += f"🧪 <b>Патогенов</b> {s}\n"
                        if "⏳ До нового патогена" in i:
                            s = i.replace("⏳ До нового патогена", "")
                            sms += f"⏳ <b>До нового патогена</b> {s}\n"
                        if "👨🏻‍🔬 Разработка" in i:
                            s = i.replace("👨🏻‍🔬 Разработка", "")
                            sms += f"👨🏻‍🔬 <b>Лаборанты</b> {s}\n\n"
                        if "🦠 Заразность" in i:
                            s = i.replace("🦠 Заразность", "")
                            sms += f"🦠 <b>Заразность</b> {s}\n"
                        if "🛡 Иммунитет" in i:
                            s = i.replace("🛡 Иммунитет", "")
                            sms += f"🛡 <b>Иммунитет</b> {s}\n"
                        if "☠️ Летальность:" in i:
                            s = i.replace("☠️ Летальность", "")
                            sms += f"☠️ <b>Летальность</b> {s}\n"
                        if "🕵️‍♂️ Безопасность" in i:
                            s = i.replace("🕵️‍♂️ Безопасность", "")
                            sms += f"🕵️‍♂️ <b>Безопасность</b> {s}\n\n"
                        if "☣️ Био-опыт:" in i:
                            s = i.replace("☣️ Био-опыт:", "")
                            sms += f"☣️ <b>Био-опыт:</b> {s}\n"
                        if "🧬 Био-ресурс:" in i:
                            s = i.replace("🧬 Био-ресурс:", "")
                            sms += f"🧬 <b>Био-ресурс:</b> {s}\n\n"
                        if "🥴 У вас горячка" in i:
                            s = i.replace("🥴 У вас горячка", "")
                            sms += f"🥴 У вас горячка {s}\n"
                        if "🥴 В состоянии горячки ещё" in i:
                            s = i.replace("🥴 В состоянии горячки", "")
                            sms += f"🥴 Горячка на {s}\n"

                    await message.reply(sms)
                    return

                # Чек болезней
                if re.fullmatch(r"б|боль", text_low, flags=re.ASCII):
                    await message.reply('мои болезни')

# Просмотр мешка
                elif re.fullmatch(r'м', text_low):
                    await message.respond('мешок')

#            if level == 4:

# Чек навыков
                if send_mes := re.search(r"(?P<ch>зараз[куаность]{,5} чек[нутьиай]{,4}\s|чек[айниуть]{,4} зараз[куаность]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['ch'] = '+заразность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)

                elif send_mes := re.search(r"(?P<pat>пат[огены]{,5} чек[айниуть]\s|чек[айниуть]{,4} пат[огены]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['pat'] = '+патоген '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<let>летал[каьностьу]{,5} чек[айниуть]{,4}\s|чек[айниуть]{,4} летал[каьностьу]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['let'] = '+летальность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<kvala>квал[лаификацияу]{,8} чек[айниуть]{,4}\s|разраб[откау]{,4} чек[айниуть]{,4}\s|чек[айниуть]{,4} разраб[откау]{,4}\s|чек[айниуть]{,4} квал[улаификация]{,8}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['kvala'] = '+квалификация '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<imun>чек[айниуть]{,4} иммун[еитеткау]{,4}\s|чек[айниуть]{,4} имун[еитеткау]{,4}\s|имун[еитеткау]{,4} чек[айниуть]{,4}\s|иммун[еитеткау]{,4} чек[айниуть]{,4}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['imun'] = '+иммунитет '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<sb>сб чек[айниуть]{,4}\s|безопасно[сть]{,3} чек[айниуть]{,4}\s|служб[ау]{,2} чек[айниуть]{,4}\s|чек[айниуть]{,4} служб[ау]{,2}\s|чек[айниуть]{,4} безопасно[сть]{,3}\s|чек[айниуть]{,4} сб\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['sb'] = '+безопасность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)

# Прокачка навыков 
                elif send_mes := re.search(r"(?P<zar>зараз[уканость]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['zar'] = '++заразность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<pat>пат[огены]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['pat'] = '++патоген '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<let>летал[укаьность]{,5}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['let'] = '++летальность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<kvala>квал[улаификация]{,8}\s|разраб[откау]{,4}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['kvala'] = '++квалификация '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<imun>иммун[уеитетка]{,4}|имун[уеитетка]{,4}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['imun'] = '++иммунитет '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)
                elif send_mes := re.search(r"(?P<sb>сб\s|безопасно[сть]{,3}\s|служб[ау]{,2}\s)(?P<lvl>\d+)", text_low, flags=re.ASCII):
                    send_mes = send_mes.groupdict()
                    send_mes['sb'] = '++безопасность '
                    send_mes['lvl'] = send_mes['lvl'] or ''
                    mes = ''.join(send_mes.values())
                    await message.reply(mes)

# управление вирусами
                elif re.search(r'увед[ыомления]', text_low):
                    await message.reply('+вирусы')

                elif re.search(r'-вирус[аы]{,2}', text_low):
                    await message.reply('-вирусы')

# Смена имени лабы и пата
                elif send_mesa := re.search(r'\пат[оген]{,4}(?P<pat>(\s(\w{1,12})){1,})', text_norm):

                    send_mesa = send_mesa.groupdict()
                    pat = ' '.join(send_mesa['pat'].split())

                    await message.reply(f'+вирус {pat}')
                    return

                elif send_mesa := re.search(r'\+лаб[a]{,1}(?P<lab>(\s(\w{1,12})){1,})', text_norm):

                    send_mesa = send_mesa.groupdict()
                    pat = ' '.join(send_mesa['lab'].split())

                    await message.reply(f'+лаб {pat}')
                    return

                elif send_mesa := re.search(r'-пат[оген]{,4}', text_low):
                    await message.reply(f'-вирус')
                    return

                elif send_mesa := re.search(r'-лаб[a]{,1}', text_low):
                    await message.reply(f'-лаб')
                    return

# Чек фулл лабы
                elif re.search(r'дом', text_low,  flags=re.ASCII):
                    await message.respond('лаб')