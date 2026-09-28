from assignment_tool import (
    add_course,
    get_courses,
    find_course
)


print("\n================================")
print("COURSE MANAGER TEST")
print("================================")


# --------------------------------------------
# ADD COURSES
# --------------------------------------------

courses_to_add = [
    ("CN", "Computer Networks", "7"),
    ("RL", "Reinforcement Learning", "7"),
    ("KRR", "Knowledge Representation and Reasoning", "7"),
    ("COAL", "Computer Organization and Assembly Language", "7"),
    ("BIGDATA", "Big Data", "7"),
]


for code, name, semester in courses_to_add:

    result = add_course(
        code=code,
        name=name,
        semester=semester
    )

    print("\nADD COURSE:")
    print(result)


# --------------------------------------------
# GET ALL COURSES
# --------------------------------------------

print("\n================================")
print("ALL COURSES")
print("================================")

courses = get_courses()

for course in courses:
    print(course)


# --------------------------------------------
# FIND COURSE
# --------------------------------------------

print("\n================================")
print("FIND COURSE")
print("================================")

course = find_course("BIGDATA")

print(course)


print("\n================================")
print("TEST COMPLETE")
print("================================")