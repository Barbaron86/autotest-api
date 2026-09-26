from clients.courses.courses_client import CreateCourseRequestDict, get_courses_client
from clients.files.files_client import CreateFileRequestDict, get_files_client
from clients.private_http_builder import AuthenticationUserDict
from clients.users.public_users_client import CreateUserRequestDict, get_public_users_client
from tools.fakers import get_random_email

public_users_client = get_public_users_client()

create_user_request = CreateUserRequestDict(
    email=get_random_email(), password="string", lastName="string", firstName="string", middleName="string"
)

create_user_response_data = public_users_client.create_user(request=create_user_request)
print(create_user_response_data)

authentication_user = AuthenticationUserDict(
    email=create_user_request["email"], password=create_user_request["password"]
)

files_client = get_files_client(user=authentication_user)
courses_client = get_courses_client(user=authentication_user)

create_file_request = CreateFileRequestDict(
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
    previewFileId=create_file_response_data["file"]["id"],
    createdByUserId=create_user_response_data["user"]["id"],
)

create_course_response_data = courses_client.create_course(request=create_course_request)
print(create_course_response_data)
