import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.reverse import reverse

from user.models import User


@pytest.mark.django_db
def test_user_registration(client, setup_users):
    response = client.post(reverse('users-list'), setup_users)
    assert response.status_code == 201
    assert response.data["username"] == setup_users["username"]
    assert response.data["email"] == setup_users["email"]
    assert "id" in response.data


@pytest.mark.django_db
def test_user_registration_invalid_data(client, setup_users):
    response = client.post(reverse('users-list'), {**setup_users, "username": ""})

    assert response.status_code == 400
    assert response.data["username"][0] == "This field may not be blank."


@pytest.mark.django_db
def test_get_token(client, login_user):
    response = client.post(reverse('token_obtain_pair'), data=login_user)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_get_access_token_with_invalid_credentials(client):
    response = client.post(reverse('token_obtain_pair'), data={"username": "admin", "password": "wrong_pass"})
    assert response.status_code == 401
    assert "detail" in response.data
    assert response.data["detail"] == "No active account found with the given credentials"


@pytest.mark.django_db
def test_refresh_token(client, login_user):
    response = client.post(reverse('token_obtain_pair'), data=login_user)
    refresh_token = response.data['refresh']
    response = client.post(reverse('token_refresh'), data={"refresh": refresh_token})
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_update_user(active_created_user, setup_users, logged_in_client, client):
    header = {"AUTHORIZATION": f"Bearer {logged_in_client}"}
    response = client.put("/api/user/users/update-account/",
                          {**setup_users, "full_name": "admin test"}, headers=header)
    assert response.status_code == 200
    active_created_user.refresh_from_db()
    assert active_created_user.full_name == "admin test"


@pytest.mark.django_db
def test_update_user_invalid(active_created_user, setup_users, logged_in_client, client):
    password = User.objects.all()[0].password
    header = {"AUTHORIZATION": f"Bearer {logged_in_client}"}
    response = client.put("/api/user/users/update-account/",
               {"password": "updated_user"}, headers=header)
    assert response.status_code == 200
    assert User.objects.all()[0].password == password


@pytest.mark.django_db
def test_update_user_no_login(active_created_user, setup_users, client):
    response = client.put("/api/user/users/update-account/",
                          {"full_name": "updated_user"})
    assert response.status_code == 403
    assert response.data["error"] == "Authentication credentials were not provided."
    assert User.objects.all()[0].full_name == "Test User"


@pytest.mark.django_db
def test_update_password(active_created_user, setup_users, logged_in_client, client):
    password = User.objects.all()[0].password
    header = {"AUTHORIZATION": f"Bearer {logged_in_client}"}
    response = client.put("/api/user/users/update-password/", {"password": "new_password"}, headers=header)
    assert response.status_code == 200
    assert response.data["message"] == "Password updated successfully"
    assert User.objects.all()[0].password != password


@pytest.mark.django_db
def test_update_password_no_login(active_created_user, setup_users, client):
    password = User.objects.all()[0].password
    response = client.put("/api/user/users/update-password/", {"password": "new_password"})
    assert response.status_code == 403
    assert response.data["error"] == "Authentication credentials were not provided."
    assert User.objects.all()[0].password == password


@pytest.mark.django_db
def test_update_email(active_created_user, setup_users, logged_in_client, client):
    header = {"AUTHORIZATION": f"Bearer {logged_in_client}"}
    response = client.put("/api/user/users/update-email/", data={"email": "new_test@gmail.com"}, headers=header)
    assert response.status_code == 200
    active_created_user.refresh_from_db()
    assert active_created_user.email_verified is False
    assert active_created_user.email == "new_test@gmail.com"


@pytest.mark.django_db
def test_resend_verification_email(client, active_created_user):
    url = reverse("resend_email_verification_email")
    response = client.post(url, {"email": active_created_user.email})
    assert response.status_code == 201


@pytest.mark.django_db
def test_send_password_reset_email(client, active_created_user):
    url = reverse("password_reset_email")
    response = client.post(url, {"email": active_created_user.email})
    assert response.status_code == 200


@pytest.mark.django_db
def test_send_password_reset_email_nonexistent(client):
    url = reverse("password_reset_email")
    response = client.post(url, {"email": "missing@example.com"})
    assert response.status_code == 404


@pytest.mark.django_db
def test_verify_reset_password_link_valid(client, active_created_user):
    uid = urlsafe_base64_encode(force_bytes(active_created_user.pk))
    token = default_token_generator.make_token(active_created_user)
    url = reverse("verify_reset_password_link")
    response = client.get(url, data={"uid": uid, "token": token})
    assert response.status_code == 200


@pytest.mark.django_db
def test_change_password_via_email(client, active_created_user):
    uid = urlsafe_base64_encode(force_bytes(active_created_user.pk))
    token = default_token_generator.make_token(active_created_user)
    url = reverse("change_password_reset_link") + f"?uid={uid}&token={token}"
    response = client.post(url, {"password": "newpassword123"})
    print(response.data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_resend_email_verification_email(client, active_created_user):
    url = reverse("resend_email_verification_email")
    response = client.post(url, {"email": active_created_user.email})
    assert response.status_code == 201


@pytest.mark.django_db
def test_verify_email(client, active_created_user):
    uid = urlsafe_base64_encode(force_bytes(active_created_user.pk))
    token = default_token_generator.make_token(active_created_user)
    url = reverse("verify_email") + f"?uid={uid}&token={token}"
    response = client.post(url)
    assert response.status_code in [200]
