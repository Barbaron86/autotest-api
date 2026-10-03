from faker import Faker


class Fake:
    """Обертка над Faker для генерации тестовых данных."""

    def __init__(self, faker: Faker):
        """Инициализирует генератор тестовых данных.

        Args:
            faker: Экземпляр Faker, используемый для генерации данных.
        """
        self.faker = faker

    def text(self) -> str:
        """Генерирует случайный текст.

        Returns:
            Случайный текст.
        """
        return self.faker.text()

    def uuid4(self) -> str:
        """Генерирует UUID версии 4.

        Returns:
            UUID в строковом представлении.
        """
        return self.faker.uuid4()

    def email(self, domain: str | None = None) -> str:
        """Генерирует уникальный случайный email.

        Args:
            domain: Домен электронной почты. Если не указан,
                Faker выбирает случайный домен.

        Returns:
            Уникальный email-адрес.
        """
        return str(self.faker.unique.email(domain=domain))

    def sentence(self) -> str:
        """Генерирует случайное предложение.

        Returns:
            Случайное предложение.
        """
        return self.faker.sentence()

    def password(self) -> str:
        """Генерирует случайный пароль.

        Returns:
            Случайный пароль.
        """
        return self.faker.password()

    def last_name(self) -> str:
        """Генерирует случайную фамилию.

        Returns:
            Случайная фамилия.
        """
        return self.faker.last_name()

    def first_name(self) -> str:
        """Генерирует случайное имя.

        Returns:
            Случайное имя.
        """
        return self.faker.first_name()

    def middle_name(self) -> str:
        """Генерирует случайное отчество.

        Returns:
            Случайное отчество.
        """
        return self.faker.middle_name()

    def integer(self, min_value: int = 0, max_value: int = 100) -> int:
        """Генерирует случайное целое число в заданном диапазоне.

        Args:
            min_value: Минимальное значение.
            max_value: Максимальное значение.

        Returns:
            Случайное целое число.
        """
        return self.faker.random_int(min=min_value, max=max_value)

    def estimated_time(self) -> str:
        """Генерирует случайную длительность курса в неделях.

        Returns:
            Строка с количеством недель.
        """
        return f"{self.faker.random_int(min=1, max=10)} weeks"

    def max_score(self) -> int:
        """Генерирует максимальный балл курса.

        Returns:
            Случайное значение от 50 до 100.
        """
        return self.faker.random_int(min=50, max=100)

    def min_score(self) -> int:
        """Генерирует минимальный балл курса.

        Returns:
            Случайное значение от 0 до 49.
        """
        return self.faker.random_int(min=0, max=49)


fake = Fake(faker=Faker("ru_RU"))
