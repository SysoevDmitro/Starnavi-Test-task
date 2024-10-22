from django.test import TestCase
from django.utils import timezone
from ninja.testing import TestClient
from django.contrib.auth import get_user_model
from posts.api import router as post_router
from user.api import router as user_router


class PostAPITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(user_router)
        self.client2 = TestClient(post_router)
        self.user = get_user_model().objects.create_user(username="test@email.com",
                                                         email='test@email.com',
                                                         password='testpassword')
        response = self.client.post("/login", json={"email": "test@email.com", "password": "testpassword"})
        self.token = response.json().get("access")
        self.client2.headers["Authorization"] = f"Bearer {self.token}"

    def test_list_posts(self):
        response = self.client2.get("/")

        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        post = {
            "title": "test",
            "content": "test",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        response = self.client2.post("/", json=post)
        response2 = self.client2.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(
                            item["title"] == post["title"] and
                            item["content"] == post["content"] and
                            item["author"]["id"] == post["author"]["id"]
                            for item in response2.json()
                        ), "Created post not found in the response.")

    def test_delete_post(self):
        post = {
            "title": "test_delete",
            "content": "test",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        # Создаем пост
        create_response = self.client2.post("/", json=post)
        self.assertEqual(create_response.status_code, 200)

        # Получаем список постов, чтобы найти созданный пост
        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break

        # Удаляем пост
        delete_response = self.client2.delete(f"/{post_id}")
        self.assertEqual(delete_response.status_code, 200)

        # Проверяем, что пост удален
        updated_posts_list = self.client2.get("/").json()
        self.assertFalse(any(item["id"] == post_id for item in updated_posts_list), "Deleted post is still present.")

    def test_update_post(self):
        post = {
            "title": "test",
            "content": "test",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        # Создаем пост
        create_response = self.client2.post("/", json=post)
        self.assertEqual(create_response.status_code, 200)

        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break
        # Обновляем созданный пост
        updated_post = {
            "id": post_id,
            "title": "updated title",
            "content": "updated content",
            "author": post["author"],  # оставляем автора прежним
            "auto_reply": False,  # или True, если нужно
            "reply_delay": 10,  # установите значение по умолчанию или требуемое
            "pub_date": timezone.now().isoformat()  # сохраняем прежнее значение даты
        }
        update_response = self.client2.put(f"/{post_id}", json=updated_post)
        self.assertEqual(update_response.status_code, 200)

        # Проверяем, что пост обновлен
        updated_posts_list = self.client2.get("/").json()
        self.assertTrue(any(
            item["title"] == updated_post["title"] and
            item["content"] == updated_post["content"] and
            item["author"]["id"] == updated_post["author"]["id"]
            for item in updated_posts_list
        ), "Updated post not found in the response.")

    def test_create_comment(self):
        # Создаем пост
        post = {
            "title": "test post",
            "content": "test content",
            "author": {"id": self.user.id, "email": self.user.email},
            "auto_reply": False,
            "reply_delay": 10,
            "pub_date": timezone.now().isoformat()
        }
        post_response = self.client2.post("/", json=post)
        self.assertEqual(post_response.status_code, 200)
        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break

        # Создаем комментарий к посту
        comment = {
            "post": post_id,
            "content": "This is a comment",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        response = self.client2.post(f"/comment/{post_id}", json=comment)
        self.assertEqual(response.status_code, 200)

    def test_update_comment(self):
        # Создаем пост
        post = {
            "title": "test post",
            "content": "test content",
            "author": {"id": self.user.id, "email": self.user.email},
            "auto_reply": False,
            "reply_delay": 10,
            "pub_date": timezone.now().isoformat()
        }
        post_response = self.client2.post("/", json=post)
        self.assertEqual(post_response.status_code, 200)
        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break

        # Создаем комментарий
        comment = {
            "post": post_id,
            "content": "This is a comment",
            "author": {"id": self.user.id, "email": self.user.email}
        }
        create_response = self.client2.post(f"/comment/{post_id}", json=comment)
        self.assertEqual(create_response.status_code, 200)
        get_post = self.client2.get(f"/{post_id}").json()

        comment_id = None
        for item in get_post["comments"]:
            comment_id = item["id"]
            break

        # Обновляем комментарий
        updated_comment = {
            "id": comment_id,
            "post": post_id,
            "content": "Updated comment content",
            "author": comment["author"]["id"]
        }
        update_response = self.client2.put(f"/comment/{post_id}/{comment_id}", json=updated_comment)
        self.assertEqual(update_response.status_code, 200)

    def test_delete_comment(self):
        post = {
            "title": "test post",
            "content": "test content",
            "author": {"id": self.user.id, "email": self.user.email},
            "auto_reply": False,
            "reply_delay": 10,
            "pub_date": timezone.now().isoformat()
        }
        post_response = self.client2.post("/", json=post)
        self.assertEqual(post_response.status_code, 200)
        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break

        # Создаем комментарий
        comment = {
            "post": post_id,
            "content": "This is a comment",
            "author": {"id": self.user.id, "email": self.user.email}
        }
        create_response = self.client2.post(f"comment/{post_id}", json=comment)
        self.assertEqual(create_response.status_code, 200)
        get_post = self.client2.get(f"/{post_id}").json()

        comment_id = None
        for item in get_post["comments"]:
            comment_id = item["id"]
            break

        # Удаляем комментарий
        delete_response = self.client2.delete(f"comment/{post_id}/{comment_id}")
        self.assertEqual(delete_response.status_code, 200)

    def test_comment_daily_breakdown(self):
        post = {
            "title": "test2",
            "content": "test",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        create_response = self.client2.post("/", json=post)
        self.assertEqual(create_response.status_code, 200)
        posts_list = self.client2.get("/").json()
        post_id = None
        for item in posts_list:
            if item["title"] == post["title"]:
                post_id = item["id"]
                break
        comment = {
            "post": post_id,
            "content": "This is a comment",
            "author": {"id": self.user.id, "email": self.user.email}
        }

        response_comment = self.client2.post(f"/comment/{post_id}", json=comment)
        self.assertEqual(response_comment.status_code, 200)
        response = self.client2.get(
            f"/{post_id}/comments-daily-breakdown?date_from=2024-01-01&date_to=2024-01-02")
        self.assertEqual(response.status_code, 200)
