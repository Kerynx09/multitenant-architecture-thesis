from dataclasses import dataclass

@dataclass
class Student:
    id: int
    name: str
    email: str
    grade: str
    school: str

@dataclass
class Teacher:
    id: int
    name: str
    subject: str
    school: str

@dataclass
class SchoolClass:
    id: int
    name: str
    teacher_id: int
    school: str
