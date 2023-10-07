from django.test import TestCase
from core.template_render import CustomFilters

fiom_fixture = "иванов иван петрович"
fiom_results = {
    "fio_short": "Иванов И.П.",
    "fio_title": "Иванов Иван Петрович",
    "genitive": "иванова ивана петровича",
    "dative": "иванову ивану петровичу",
}
fiof_fixture = "иванова ирина петровна"
fiof_results = {
    "fio_short": "Иванова И.П.",
    "fio_title": "Иванова Ирина Петровна",
    "genitive": "ивановой ирины петровны",
    "dative": "ивановой ирине петровне",
}
adj_fixture = "календарный"
adj_results = {
    1: "календарный",
    2: "календарных",
    3: "календарных",
    4: "календарных",
    5: "календарных",
    6: "календарных",
    7: "календарных",
    8: "календарных",
    9: "календарных",
    10: "календарных",
    11: "календарных",
    12: "календарных",
    21: "календарный",
    31: "календарный",
    100: "календарных",
    101: "календарный",
}

noun_fixture = "день"
noun_results = {
    1: "день",
    2: "дня",
    3: "дня",
    4: "дня",
    5: "дней",
    6: "дней",
    7: "дней",
    8: "дней",
    9: "дней",
    10: "дней",
    11: "дней",
    21: "день",
    22: "дня",
    100: "дней",
    101: "день",
}

filters_fixture = [
    "fio_short",
    "fio_title",
    "genitive",
    "dative",
    "noun_plural",
    "adj_plural",
]


class Test(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.filters = CustomFilters()

    def test_get_filters(self):
        """Проверка, что get_filter возвращает требуемый набор фильтров"""
        all_filters = Test.filters.get_filters()
        for filter in filters_fixture:
            with self.subTest(filter=filter):
                self.assertIn(
                    filter,
                    all_filters,
                    f"Фильтр {filter} не возвращен методом get_filters",
                )

    def test_fio_filters(self):
        """Проверка фильтров fio_short, fio_title"""
        all_filters = Test.filters.get_filters()
        # мужской род
        for filter, result in fiom_results.items():
            with self.subTest(filter=filter, result=result):
                self.assertEqual(
                    all_filters[filter](fiom_fixture),
                    result,
                    f"Filter {filter} returns unexpected result",
                )
        # женский род
        for filter, result in fiof_results.items():
            with self.subTest(filter=filter, result=result):
                self.assertEqual(
                    all_filters[filter](fiof_fixture),
                    result,
                    f"Filter {filter} returns unexpected result",
                )

    def test_adj_plural(self):
        """Проверка фильтра adj_plural (склонение прилагательных)"""
        for number, result in adj_results.items():
            with self.subTest(number=number, result=result):
                self.assertEqual(
                    self.filters.adj_plural(adj_fixture, number),
                    result,
                    "Filter adj_plural returns unexpected result",
                )

    def test_noun_plural(self):
        """Проверка фильтра noun_plural (склонение существительных)"""
        for number, result in noun_results.items():
            with self.subTest(number=number, result=result):
                self.assertEqual(
                    self.filters.noun_plural(noun_fixture, number),
                    result,
                    "Filter noun_plural returns unexpected result",
                )
