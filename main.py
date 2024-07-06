import json
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Tокен бота, полученный от BotFather
TOKEN = '6947172371:AAGB6jjloVSYMWqoIPKyQ_Ezz_QbT8U3X9I'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Путь к JSON-файлу с трактовками
NUMEROLOGY_JSON_PATH = '.venv/numerology.json'
ADMIN_USER_IDS = [1345460527]  # Замените на ID администратора


# Загрузка трактовок из JSON-файла
def load_numerology_data():
    with open(NUMEROLOGY_JSON_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)


numerology_data = load_numerology_data()


# Функция для вычисления нумерологического числа
def calculate_numerology_number(date_str: str) -> int:
    # Извлекаем цифры из строки
    digits = [int(char) for char in date_str if char.isdigit()]

    # Суммируем цифры
    sum_digits = sum(digits)

    # Если результат суммы равен 11 или 22, возвращаем их как мастер-числа
    if sum_digits == 11 or sum_digits == 22:
        return sum_digits
    else:
        # Иначе сокращаем до однозначного числа путем рекурсивной суммы цифр
        while sum_digits > 9:
            sum_digits = sum(int(digit) for digit in str(sum_digits))
        return sum_digits


# Функция, обрабатывающая команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Отправь мне свою дату рождения в формате ДД.ММ.ГГГГ, и я рассчитаю твое нумерологическое число.",
        reply_markup=ForceReply(selective=True),
    )


# Функция, обрабатывающая текстовые сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    birth_date = update.message.text
    try:
        # Проверяем формат даты
        day, month, year = birth_date.split('.')
        if len(day) == 2 and len(month) == 2 and len(year) == 4:
            # Рассчитываем нумерологическое число
            result = calculate_numerology_number(birth_date)
            # Получаем трактовку из JSON данных
            interpretation = numerology_data.get(str(result), "Трактовка не найдена.")
            await update.message.reply_text(f'Твое нумерологическое число: {result}. Трактовка: {interpretation}')
        else:
            raise ValueError
    except ValueError:
        await update.message.reply_text('Пожалуйста, отправь дату рождения в правильном формате ДД.ММ.ГГГГ.')


# Функция для обновления трактовок нумерологических чисел
async def update_interpretation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        number, interpretation = context.args[0], " ".join(context.args[1:])
        numerology_data[number] = interpretation

        # Сохраняем обновленные данные в JSON-файл
        with open(NUMEROLOGY_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(numerology_data, file, ensure_ascii=False, indent=4)

        await update.message.reply_text(f"Трактовка для числа {number} обновлена.")
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /update_interpretation <число> <трактовка>")


def main() -> None:
    # Создаем приложение и регистрируем обработчики
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("update_interpretation", update_interpretation))

    # Запускаем бота
    app.run_polling()


if __name__ == '__main__':
    main()
