from clients.courses.courses_client import CreateCourseRequestDict, get_courses_client
from clients.exercises.exercises_client import CreateExerciseRequestDict, get_exercises_client
from clients.files.files_client import get_files_client
from clients.files.files_schema import CreateFileRequestSchema
from clients.private_http_builder import AuthenticationUserSchema
from clients.users.public_users_client import get_public_users_client
from clients.users.user_schema import CreateUserRequestSchema
from tools.fakers import get_random_email

public_users_client = get_public_users_client()

create_user_request = CreateUserRequestSchema(
    email=get_random_email(), password="string", last_name="string", first_name="string", middle_name="string"
)

create_user_response_data = public_users_client.create_user(request=create_user_request)
print(create_user_response_data)

authentication_user = AuthenticationUserSchema(email=create_user_request.email, password=create_user_request.password)

files_client = get_files_client(user=authentication_user)
courses_client = get_courses_client(user=authentication_user)
exercise_client = get_exercises_client(user=authentication_user)

create_file_request = CreateFileRequestSchema(
    filename="image.png", directory="courses", upload_file="./testdata/files/image.png"
)
create_file_response_data = files_client.create_file(request=create_file_request)
print(create_file_response_data)

create_course_request = CreateCourseRequestDict(
    title="Python",
    description="Python API course",
    minScore=10,
    maxScore=100,
    estimatedTime="2 weeks",
    previewFileId=create_file_response_data.file.id,
    createdByUserId=create_user_response_data.user.id,
)

create_course_response_data = courses_client.create_course(request=create_course_request)
print(create_course_response_data)

create_exercise_request = CreateExerciseRequestDict(
    title="Python Exercise",
    description="Python Exercise Description",
    courseId=create_user_response_data.user.id,
    maxScore=100,
    minScore=10,
    estimatedTime="1 week",
    orderIndex=0,
)
create_exercise_response_data = exercise_client.create_exercise(request=create_exercise_request)
print(create_exercise_response_data)
