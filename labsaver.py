# meta developer: @enicaaa
# scope: hikka_only

import re
from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class LabSaverMod(loader.Module):
    """Модуль для сохранения и просмотра досье лабораторий """

    strings = {
        "name": "LabSaver",
        "no_id": "<b>❌ Укажите ID, юзернейм или ответьте на сообщение пользователя.</b>",
        "not_found": "<b>❌ В базе нет сохраненного досье для ID:</b> <code>{}</code>",
        "list_empty": "<b>ℹ️ База данных лабораторий пуста.</b>",
        "list_header": "<b>🧪 Сохраненные лаборатории (всего: {}):</b>\n\n",
    }

    async def client_ready(self, client, db):
        self._db = db
        if not self._db.get("LabSaver", "labs", False):
            self._db.set("LabSaver", "labs", {})

    @loader.watcher(only_messages=True)
    async def watcher(self, message: Message):
        """Автоматически перехватывает досье и берет ID из сущности после слова Руководитель"""
        if not message.text:
            return

        # Проверяем наличие ключевых фраз
        if "Досье лаборатории " in message.text and "Руководитель:" in message.text:
            user_id = None
            username = "Неизвестно"

            # Ищем позицию слова "Руководитель:" в тексте
            match = re.search(r"Руководитель:", message.text)
            if match and message.entities:
                owner_offset = match.end()

                # Ищем сущность (entity) типа tg://user?id=... или с явным user_id,
                # которая находится сразу после слова "Руководитель:"
                for entity in message.entities:
                    if entity.offset >= owner_offset:
                        # Если это кликабельное имя с прямой ссылкой на ID (MessageEntityMentionName)
                        if hasattr(entity, "user_id") and entity.user_id:
                            user_id = entity.user_id
                            break
                        # Если это ссылка вида t.me/username или tg://user?id=123456
                        elif hasattr(entity, "url") and entity.url:
                            url_match = re.search(r"tg://openmessage\?user_id=(\d+)", entity.url)
                            if url_match:
                                user_id = int(url_match.group(1))
                                break

            # Запасной вариант: если ID не был найден в entities, пытаемся разрешить username из текста после "Руководитель:"
            if match:
                leader_line = message.text[match.end():].split("\n")[0].strip()
                # Извлекаем текст или username из строки руководителя
                username_match = re.search(r"@?([a-zA-Z0-9_]{5,32})", leader_line)
                if username_match and not user_id:
                    try:
                        user = await self._client.get_entity(username_match.group(1))
                        if user:
                            user_id = user.id
                    except Exception:
                        pass
                
                # Пытаемся забрать чистый текст никнейма/имени из строчки для отображения
                clean_name = re.sub(r'<[^>]+>', '', leader_line).strip()
                if clean_name:
                    username = clean_name

            # Если ID определен, пробуем также подтянуть актуальный юзернейм через клиент (если доступен)
            if user_id:
                try:
                    user_entity = await self._client.get_entity(user_id)
                    if user_entity:
                        if user_entity.username:
                            username = f"@{user_entity.username}"
                        elif user_entity.first_name:
                            username = user_entity.first_name
                except Exception:
                    pass

                labs = self._db.get("LabSaver", "labs", {})
                labs[str(user_id)] = {
                    "text": message.text,
                    "date": message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else "",
                    "username": username
                }
                self._db.set("LabSaver", "labs", labs)

    @loader.command()
    async def lab(self, message: Message):
        """[ID/reply/username] — Показать сохраненное досье лаборатории"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        user_id = None

        if args:
            if args.isdigit():
                user_id = int(args)
            else:
                try:
                    user = await self._client.get_entity(args)
                    if user:
                        user_id = user.id
                except Exception:
                    pass
        elif reply:
            user_id = reply.sender_id
        else:
            user_id = message.sender_id

        if not user_id:
            await utils.answer(message, self.strings("no_id"))
            return

        labs = self._db.get("LabSaver", "labs", {})
        data = labs.get(str(user_id))

        if not data:
            await utils.answer(message, self.strings("not_found").format(user_id))
            return

        text = data["text"]
        if data.get("date"):
            text += f"\n\n<b>🗓 Обновлено:</b> <code>{data['date']}</code>"

        await utils.answer(message, text)

    @loader.command()
    async def lablist(self, message: Message):
        """— Показать список сохраненных ID и никнеймов лабораторий"""
        labs = self._db.get("LabSaver", "labs", {})
        if not labs:
            await utils.answer(message, self.strings("list_empty"))
            return

        # Сортировка списка по возрастанию ID
        sorted_ids = sorted(labs.keys(), key=lambda x: int(x))

        res = self.strings("list_header").format(len(sorted_ids))
        for uid in sorted_ids:
            uname = labs[uid].get("username", "Неизвестно")
            res += f"• <code>{uid}</code> — <b>{uname}</b>\n"

        await utils.answer(message, res)