from clients.courses.courses_client import get_courses_client
from clients.courses.courses_schema import CreateCourseRequestSchema
from clients.exercises.exercises_client import get_exercises_client
from clients.exercises.exercises_schema import CreateExerciseRequestSchema
from clients.files.files_client import get_files_client
from clients.files.files_schema import CreateFileRequestSchema
from clients.private_http_builder import AuthenticationUserSchema
from clients.users.public_users_client import get_public_users_client
from clients.users.user_schema import CreateUserRequestSchema
from config import settings

public_users_client = get_public_users_client()

create_user_request = CreateUserRequestSchema()

create_user_response_data = public_users_client.create_user(request=create_user_request)
print(create_user_response_data)

authentication_user = AuthenticationUserSchema(email=create_user_request.email, password=create_user_request.password)

files_client = get_files_client(user=authentication_user)
courses_client = get_courses_client(user=authentication_user)
exercise_client = get_exercises_client(user=authentication_user)

create_file_request = CreateFileRequestSchema(upload_file=settings.test_data.image_png_file)
create_file_response_data = files_client.create_file(request=create_file_request)
print(create_file_response_data)

create_course_request = CreateCourseRequestSchema(
    preview_file_id=create_file_response_data.file.id,
    created_by_user_id=create_user_response_data.user.id,
)

create_course_response_data = courses_client.create_course(request=create_course_request)
print(create_course_response_data)

create_exercise_request = CreateExerciseRequestSchema(
    course_id=create_course_response_data.course.id,
)
create_exercise_response_data = exercise_client.create_exercise(request=create_exercise_request)
print(create_exercise_response_data)
