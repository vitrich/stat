# main/test_generator.py
import math
import random
from fractions import Fraction

# ...

def generate_test_for_lesson_3(user):
    """
    Урок 3. Приведение к общему знаменателю, сложение и вычитание дробей с разными знаменателями.
    Возвращает список словарей:
    {
        "question": "текст",
        "answer": "правильный_ответ_как_строка",
        "meta": {... по желанию ...}
    }
    """

    questions = []

    # 1–3. Приведение к общему знаменателю (без действия)
    for _ in range(3):
        a = random.randint(1, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 9)
        d = random.randint(2, 9)
        # избегаем одинаковых знаменателей — это уже другой тип
        while b == d:
            d = random.randint(2, 9)

        frac1 = Fraction(a, b)
        frac2 = Fraction(c, d)

        l = (b * d) // math.gcd(b, d)
        k1 = l // b
        k2 = l // d
        new1 = Fraction(a * k1, l)
        new2 = Fraction(c * k2, l)

        question_text = (
            f"Приведи дроби \\(\\frac{{{a}}}{{{b}}}\\) и "
            f"\\(\\frac{{{c}}}{{{d}}}\\) к общему знаменателю."
            " Напиши ответ в виде двух дробей через запятую, например: 3/10, 7/10"
        )
        answer_text = f"{new1.numerator}/{new1.denominator}, {new2.numerator}/{new2.denominator}"

        questions.append({
            "question": question_text,
            "answer": answer_text,
            "type": "common_denom_only"
        })

    # 4–6. Сложение дробей с разными знаменателями
    for _ in range(3):
        a = random.randint(1, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 9)
        d = random.randint(2, 9)
        while b == d:
            d = random.randint(2, 9)

        frac1 = Fraction(a, b)
        frac2 = Fraction(c, d)
        result = frac1 + frac2
        result = Fraction(result.numerator, result.denominator)  # сразу в несократимом виде

        question_text = (
            f"Выполни сложение и запиши ответ в виде несократимой дроби: "
            f"\\(\\frac{{{a}}}{{{b}}} + \\frac{{{c}}}{{{d}}}\\). "
            "Ответ запиши в виде m/n, например: 5/12"
        )
        answer_text = f"{result.numerator}/{result.denominator}"

        questions.append({
            "question": question_text,
            "answer": answer_text,
            "type": "add_diff_denom"
        })

    # 7–9. Вычитание дробей с разными знаменателями (берём так, чтобы результат был положительным)
    for _ in range(3):
        a = random.randint(1, 9)
        b = random.randint(2, 9)
        c = random.randint(1, 9)
        d = random.randint(2, 9)
        while b == d:
            d = random.randint(2, 9)

        frac1 = Fraction(a, b)
        frac2 = Fraction(c, d)

        # переставим, чтобы результат не был отрицательным
        if frac1 < frac2:
            frac1, frac2 = frac2, frac1
            a, b, c, d = c, d, a, b

        result = frac1 - frac2
        result = Fraction(result.numerator, result.denominator)

        question_text = (
            f"Выполни вычитание и запиши ответ в виде несократимой дроби: "
            f"\\(\\frac{{{a}}}{{{b}}} - \\frac{{{c}}}{{{d}}}\\). "
            "Ответ запиши в виде m/n, например: 1/6"
        )
        answer_text = f"{result.numerator}/{result.denominator}"

        questions.append({
            "question": question_text,
            "answer": answer_text,
            "type": "sub_diff_denom"
        })

    return questions
