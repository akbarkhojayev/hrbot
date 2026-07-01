# HR anketa bot

Aiogram v3 asosida yozilgan Telegram bot. Nomzodlardan shaxsiy ma'lumotlar, yo'nalish, kirish maqsadi, CV, rasm, video, tajriba, loyihalar va AI bo'yicha bilimlarni bosqichma-bosqich so'raydi.

## Ishga tushirish

1. Virtual environment yarating va kutubxonalarni o'rnating:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

2. `.env.example` faylidan `.env` yarating:

```bash
cp .env.example .env
```

3. `.env` ichiga bot tokenini va guruh ID sini yozing:

```env
BOT_TOKEN=123456:ABCDEF_your_telegram_bot_token
GROUP_CHAT_ID=-1001234567890
ADMIN_CHAT_ID=
```

`GROUP_CHAT_ID` berilsa, har yangi anketa shu guruhga yuboriladi. Guruh ID odatda `-100...` bilan boshlanadi. `ADMIN_CHAT_ID` eski sozlama uchun fallback sifatida qolgan.

4. Botni ishga tushiring:

```bash
.venv/bin/python bot.py
```

## Saqlash

To'ldirilgan anketalar `data/applications.jsonl` fayliga yoziladi. Telegramdagi rasm, CV va video fayllar `file_id` ko'rinishida saqlanadi.

## Buyruqlar

- `/start` - anketani boshlash
- `/cancel` - anketani bekor qilish
