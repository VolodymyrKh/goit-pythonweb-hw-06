from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Group(Base):
    """Навчальна група, наприклад «AD-101»."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    students: Mapped[list["Student"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Group(id={self.id}, name={self.name!r})"


class Student(Base):
    """Студент, який належить до однієї групи."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    group: Mapped["Group"] = relationship(back_populates="students")
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name!r}, group_id={self.group_id})"


class Teacher(Base):
    """Викладач, який читає один або кілька предметів."""

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Teacher(id={self.id}, name={self.name!r})"


class Subject(Base):
    """Предмет із вказівкою викладача, який його читає."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="subjects")
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Subject(id={self.id}, name={self.name!r}, teacher_id={self.teacher_id})"


class Grade(Base):
    """Оцінка студента з предмета із датою, коли її отримано."""

    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <= 100", name="grade_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        index=True,
    )

    student: Mapped["Student"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")

    def __repr__(self) -> str:
        return (
            f"Grade(id={self.id}, student_id={self.student_id}, "
            f"subject_id={self.subject_id}, grade={self.grade}, date_of={self.date_of})"
        )
