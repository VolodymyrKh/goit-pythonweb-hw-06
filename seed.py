import random
from collections import Counter
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import text

from src.db import session_scope
from src.models import Grade, Group, Student, Subject, Teacher

fake = Faker("uk_UA")


def full_name() -> str:
    return f"{fake.first_name()} {fake.last_name()}"

GROUPS = ["AD-101", "AD-102", "AD-103"]
TEACHERS_COUNT = (3, 5)
STUDENTS_COUNT = (30, 50)
GRADES_PER_STUDENT = (12, 20)

SUBJECT_POOL = [
    "Вища математика",
    "Бази даних",
    "Алгоритми та структури даних",
    "Операційні системи",
    "Комп'ютерні мережі",
    "Веб-технології",
    "Теорія ймовірностей",
    "Англійська мова",
]

SEMESTER_START = date(2026, 2, 2)
LESSONS_PER_SUBJECT = 16


def truncate_all(session) -> None:
    """Очищає всі таблиці та скидає послідовності id.

    TRUNCATE ... CASCADE прибирає залежні рядки в один прохід,
    RESTART IDENTITY повертає автоінкремент до 1.
    """
    session.execute(
        text(
            "TRUNCATE TABLE grades, students, subjects, teachers, groups "
            "RESTART IDENTITY CASCADE"
        )
    )


def lesson_dates(count: int = LESSONS_PER_SUBJECT) -> list[date]:
    """Розписання предмета: одне заняття на тиждень від початку семестру."""
    return [SEMESTER_START + timedelta(weeks=i) for i in range(count)]


def make_grade(ability: int) -> int:
    return max(1, min(100, round(random.gauss(ability, 8))))


def seed() -> None:
    with session_scope() as session:
        truncate_all(session)

        # --- групи ---
        groups = [Group(name=name) for name in GROUPS]
        session.add_all(groups)

        # --- викладачі ---
        teachers = [
            Teacher(name=full_name()) for _ in range(random.randint(*TEACHERS_COUNT))
        ]
        session.add_all(teachers)

        # flush відправляє INSERT'и в БД і заповнює id, але не завершує транзакцію,
        # тому наступні рядки вже можуть посилатися на groups[i].id / teachers[i].id.
        session.flush()

        # --- предмети: кожен читає випадковий викладач ---
        subject_names = random.sample(SUBJECT_POOL, random.randint(5, 8))
        subjects = [
            Subject(name=name, teacher_id=random.choice(teachers).id)
            for name in subject_names
        ]
        session.add_all(subjects)

        # --- студенти, рівномірно розкидані по групах ---
        students = [
            Student(name=full_name(), group_id=random.choice(groups).id)
            for _ in range(random.randint(*STUDENTS_COUNT))
        ]
        session.add_all(students)
        session.flush()

        # --- оцінки ---
        schedule = {subject.id: lesson_dates() for subject in subjects}
        grades: list[Grade] = []

        for student in students:
            ability = random.randint(55, 95)
            total = random.randint(*GRADES_PER_STUDENT)

            # Розподіляємо total оцінок між предметами з повтореннями:
            # Counter дає, скільки оцінок припало на кожен предмет.
            picks = Counter(random.choices(subjects, k=total))

            for subject, count in picks.items():
                dates = random.sample(
                    schedule[subject.id],
                    min(count, len(schedule[subject.id])),
                )
                for lesson_date in dates:
                    grades.append(
                        Grade(
                            student_id=student.id,
                            subject_id=subject.id,
                            grade=make_grade(ability),
                            date_of=lesson_date,
                        )
                    )

        session.add_all(grades)

        print("База наповнена:")
        print(f"  груп:       {len(groups)}")
        print(f"  викладачів: {len(teachers)}")
        print(f"  предметів:  {len(subjects)}")
        print(f"  студентів:  {len(students)}")
        print(f"  оцінок:     {len(grades)}")


if __name__ == "__main__":
    seed()
