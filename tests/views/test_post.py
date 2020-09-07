# import pytest
#
#
# class Describe_PostView:
#     class Describe_like_post:
#         @pytest.fixture
#         def post(self):
#             return PostFactory.create()
#
#         @pytest.fixture
#         def logged_in_user(self):
#             return UserFactory.create()
#
#         @pytest.fixture
#         def subject(self, client, logged_in_user, post):
#             url = url_for('PostView:like_post', post_id=post.id)
#             # headers
#             return client.post(url, headers=headers)
#
#         @pytest.fixture
#         def test_200이_반환된다(self, subject):
#             assert subject.status_code == 200
#
#         @pytest.fixture
#         def test_post의_like한_user가_추가된다(self, subject, post, logged_in_user):
#             post.reload()
#             assert logged_in_user in post.likes
#
#         class Context_이미_like한경우:
#             @pytest.fixture
#             def post(self, post, logged_in_user):
#                 post.likes.create(logged_in_user)
#                 return post
#
#             @pytest.fixture
#             def test_200이_반환된다(self, subject):
#                 assert subject.status_code == 200
#
#             @pytest.fixture
#             def test_아무일도_일어나지_않는다(self, subject, post, logged_in_user):
#                 post.reload()
#                 like_users = post.likes.filter(lambda user: user == logged_in_user)
#                 assert len(like_users) == 1
