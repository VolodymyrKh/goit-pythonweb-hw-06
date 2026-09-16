from sqlalchemy import Row, desc, func, select

from src.db import session_scope
from src.models import Grade, Group, Student, Subject

AVG_GRADE = func.round(func.avg(Grade.grade), 2).label("avg_grade")


def select_1() -> list[Row]:
    """1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів."""
    stmt = (
        select(Student.id, Student.name, AVG_GRADE)
        .join(Grade, Grade.student_id == Student.id)
        .group_by(Student.id, Student.name)
        .order_by(desc("avg_grade"))
        .limit(5)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_2(subject_id: int) -> Row | None:
    """2. Знайти студента із найвищим середнім балом з певного предмета."""
    stmt = (
        select(Student.id, Student.name, AVG_GRADE)
        .join(Grade, Grade.student_id == Student.id)
        .where(Grade.subject_id == subject_id)
        .group_by(Student.id, Student.name)
        .order_by(desc("avg_grade"))
        .limit(1)
    )
    with session_scope() as session:
        return session.execute(stmt).first()


def select_3(subject_id: int) -> list[Row]:
    """3. Знайти середній бал у групах з певного предмета."""
    stmt = (
        select(Group.id, Group.name, AVG_GRADE)
        .select_from(Grade)
        .join(Student, Grade.student_id == Student.id)
        .join(Group, Student.group_id == Group.id)
        .where(Grade.subject_id == subject_id)
        .group_by(Group.id, Group.name)
        .order_by(Group.name)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_4() -> float | None:
    """4. Знайти середній бал на потоці (по всій таблиці оцінок)."""
    stmt = select(AVG_GRADE)
    with session_scope() as session:
        return session.execute(stmt).scalar()


def select_5(teacher_id: int) -> list[Row]:
    """5. Знайти які курси читає певний викладач."""
    stmt = (
        select(Subject.id, Subject.name)
        .where(Subject.teacher_id == teacher_id)
        .order_by(Subject.name)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_6(group_id: int) -> list[Row]:
    """6. Знайти список студентів у певній групі."""
    stmt = (
        select(Student.id, Student.name)
        .where(Student.group_id == group_id)
        .order_by(Student.name)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_7(group_id: int, subject_id: int) -> list[Row]:
    """7. Знайти оцінки студентів у окремій групі з певного предмета."""
    stmt = (
        select(Student.id, Student.name, Grade.grade, Grade.date_of)
        .join(Grade, Grade.student_id == Student.id)
        .where(Student.group_id == group_id, Grade.subject_id == subject_id)
        .order_by(Student.name, Grade.date_of)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_8(teacher_id: int) -> float | None:
    """8. Знайти середній бал, який ставить певний викладач зі своїх предметів."""
    stmt = (
        select(AVG_GRADE)
        .select_from(Grade)
        .join(Subject, Grade.subject_id == Subject.id)
        .where(Subject.teacher_id == teacher_id)
    )
    with session_scope() as session:
        return session.execute(stmt).scalar()


def select_9(student_id: int) -> list[Row]:
    """9. Знайти список курсів, які відвідує певний студент."""
    stmt = (
        select(Subject.id, Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .where(Grade.student_id == student_id)
        .distinct()
        .order_by(Subject.name)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


def select_10(student_id: int, teacher_id: int) -> list[Row]:
    """10. Список курсів, які певному студенту читає певний викладач."""
    stmt = (
        select(Subject.id, Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        .distinct()
        .order_by(Subject.name)
    )
    with session_scope() as session:
        return session.execute(stmt).all()


# --------------------------------------------------------------------------
# Демонстрація: підставляє реальні id з бази, щоб вивід не був порожнім.
# --------------------------------------------------------------------------


def _demo_ids() -> dict[str, int]:
    """Бере по одному існуючому id кожної сутності для прикладів."""
    with session_scope() as session:
        teacher_id = session.execute(
            select(Subject.teacher_id).group_by(Subject.teacher_id).limit(1)
        ).scalar()
        subject_id = session.execute(
            select(Subject.id).where(Subject.teacher_id == teacher_id).limit(1)
        ).scalar()
        group_id = session.execute(select(Group.id).order_by(Group.id).limit(1)).scalar()
        student_id = session.execute(
            select(Grade.student_id)
            .join(Subject, Grade.subject_id == Subject.id)
            .where(Subject.teacher_id == teacher_id)
            .limit(1)
        ).scalar()
    return {
        "teacher_id": teacher_id,
        "subject_id": subject_id,
        "group_id": group_id,
        "student_id": student_id,
    }


def _show(title: str, result) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if result is None or result == []:
        print("  (немає даних)")
    elif isinstance(result, Row):
        print("  " + " | ".join(str(value) for value in result))
    elif isinstance(result, list):
        for row in result:
            print("  " + " | ".join(str(value) for value in row))
    else:
        print(f"  {result}")


def main() -> None:
    ids = _demo_ids()
    subject_id = ids["subject_id"]
    teacher_id = ids["teacher_id"]
    group_id = ids["group_id"]
    student_id = ids["student_id"]

    _show("1. Топ-5 студентів за середнім балом з усіх предметів", select_1())
    _show(f"2. Найкращий студент з предмета id={subject_id}", select_2(subject_id))
    _show(f"3. Середній бал у групах з предмета id={subject_id}", select_3(subject_id))
    _show("4. Середній бал на потоці", select_4())
    _show(f"5. Курси викладача id={teacher_id}", select_5(teacher_id))
    _show(f"6. Студенти групи id={group_id}", select_6(group_id))
    _show(
        f"7. Оцінки групи id={group_id} з предмета id={subject_id}",
        select_7(group_id, subject_id),
    )
    _show(f"8. Середній бал викладача id={teacher_id}", select_8(teacher_id))
    _show(f"9. Курси студента id={student_id}", select_9(student_id))
    _show(
        f"10. Курси, які студенту id={student_id} читає викладач id={teacher_id}",
        select_10(student_id, teacher_id),
    )


if __name__ == "__main__":
    main()
