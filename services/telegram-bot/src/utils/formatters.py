from datetime import UTC, datetime


def _pluralize_ru(number: int, one: str, few: str, many: str) -> str:
    """
    Вспомогательная функция для плюрализации русских слов.

    number: Число для определения формы слова.
    one: Форма для единственного числа (1, 21, 31...).
    few: Форма для малого количества (2-4, 22-24...).
    many: Форма для большого количества (5-20, 25-30...).
    """
    num = int(number)
    if num % 10 == 1 and num % 100 != 11:  # noqa: PLR2004 Magic value
        return one
    if num % 10 in {2, 3, 4} and num % 100 not in {12, 13, 14}:
        return few
    return many


# FIXME Накидал через gpt. Хорошее место для добавления тестов
def format_publication_time(vacancy_publication_date: datetime) -> str:  # noqa: PLR0911 Too many return statements
    """
    Форматирует время публикации вакансии в относительном виде.

    Примеры вывода:
    - только что (если в течении 5 минут)
    - 5 минут назад
    - 1 час назад
    - 2 дня назад
    - неделю назад
    - 2 недели назад
    - 3 недели назад
    - 24.06.2025 (если прошло больше 3 недель)
    """
    now = datetime.now(UTC)
    delta = now - vacancy_publication_date

    seconds = delta.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7

    if minutes < 5:  # noqa: PLR2004 Magic value
        return "только что"

    if minutes < 60:  # noqa: PLR2004
        val = int(minutes)
        unit = _pluralize_ru(val, "минуту", "минуты", "минут")
        return f"{val} {unit} назад"

    if hours < 24:  # noqa: PLR2004
        val = int(hours)
        unit = _pluralize_ru(val, "час", "часа", "часов")
        return f"{val} {unit} назад"

    if days < 7:  # noqa: PLR2004
        val = int(days)
        unit = _pluralize_ru(val, "день", "дня", "дней")
        return f"{val} {unit} назад"

    if 1 <= weeks < 1.5:  # noqa: PLR2004
        return "неделю назад"
    if 1.5 <= weeks < 2.5:  # noqa: PLR2004
        return "2 недели назад"
    if 2.5 <= weeks < 3.5:  # noqa: PLR2004
        return "3 недели назад"

    # Если прошло более 3-х недель, возвращаем абсолютную дату
    return vacancy_publication_date.strftime("%d.%m.%Y")
