from django.test import TestCase
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from apps.models import Site, CustomUser, Category, Blog, BlogViewing, Message, Region, District, Comment


class SiteModelTest(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Test Site",
            picture="test.jpg",
            about_us="About Us Information",
            social={"twitter": "https://twitter.com/test"},
            adress="123 Test Street",
            email="test@example.com",
            phone="+123456789"
        )

    def test_site_creation(self):
        self.assertEqual(self.site.name, "Test Site")
        self.assertTrue(isinstance(self.site, Site))
        self.assertEqual(str(self.site), "Test Site")


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Technology")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Technology")
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(self.category.slug, slugify("Technology"))

    def test_category_slug_uniqueness(self):
        duplicate_category = Category.objects.create(name="Technology")
        self.assertNotEqual(self.category.slug, duplicate_category.slug)
        self.assertTrue(duplicate_category.slug.startswith("technology-"))


class BlogModelTest(TestCase):
    def setUp(self):
        password = make_password("securepassword")
        self.user = CustomUser.objects.create_user(
            username="author",
            email="author@example.com",
            password=password
        )
        self.category = Category.objects.create(name="Test Category")
        self.blog = Blog.objects.create(
            title="Test Blog",
            author=self.user,
            description="This is a test blog",
            is_active=Blog.Active.ACTIVE
        )
        self.blog.category.add(self.category)

    def test_blog_creation(self):
        self.assertEqual(self.blog.title, "Test Blog")
        self.assertTrue(isinstance(self.blog, Blog))
        self.assertEqual(str(self.blog), "Test Blog")
        self.assertEqual(self.blog.slug, "test-blog")
        self.assertEqual(self.blog.category.count(), 1)

    def test_blog_slug_uniqueness(self):
        duplicate_blog = Blog.objects.create(
            title="Test Blog",
            author=self.user,
            description="Duplicate test blog",
            is_active=Blog.Active.ACTIVE
        )
        self.assertNotEqual(self.blog.slug, duplicate_blog.slug)
        self.assertTrue(duplicate_blog.slug.startswith("test-blog"))

    def test_blog_viewing(self):
        BlogViewing.objects.create(blog=self.blog)
        BlogViewing.objects.create(blog=self.blog)
        self.assertEqual(self.blog.view_count, 2)


class MessageModelTest(TestCase):
    def setUp(self):
        password = make_password("securepassword")
        self.user = CustomUser.objects.create_user(
            username="messenger",
            email="messenger@example.com",
            password=password
        )
        self.message = Message.objects.create(
            author=self.user,
            subject="Test Subject",
            message="This is a test message",
        )

    def test_message_creation(self):
        self.assertEqual(self.message.subject, "Test Subject")
        self.assertTrue(isinstance(self.message, Message))
        self.assertFalse(self.message.status)


class RegionAndDistrictModelTest(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        self.district = District.objects.create(name="Test District", region=self.region)

    def test_region_and_district_creation(self):
        self.assertEqual(self.region.name, "Test Region")
        self.assertTrue(isinstance(self.region, Region))
        self.assertEqual(str(self.region), "Test Region")

        self.assertEqual(self.district.name, "Test District")
        self.assertTrue(isinstance(self.district, District))
        self.assertEqual(self.district.region, self.region)
        self.assertEqual(str(self.district), "Test District")


class CommentModelTest(TestCase):
    def setUp(self):
        password = make_password("securepassword")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password=password
        )
        self.blog = Blog.objects.create(
            title="Test Blog",
            description="This is a test blog",
            is_active=Blog.Active.ACTIVE,
        )
        self.comment1 = Comment.objects.create(
            comment="First comment",
            author=self.user,
            blog=self.blog
        )
        self.comment2 = Comment.objects.create(
            comment="Second comment",
            author=self.user,
            blog=self.blog
        )

    def test_comments_on_blog(self):
        comments = self.blog.comment_set.all()
        self.assertEqual(comments.count(), 2)
        self.assertEqual(comments[0].comment, "First comment")
        self.assertEqual(comments[1].comment, "Second comment")


class BlogManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Technology")

        self.blog1 = Blog.objects.create(
            title="Active Blog 1",
            description="Content for active blog 1",
            is_active=Blog.Active.ACTIVE,
        )
        self.blog1.category.add(self.category)

        self.blog2 = Blog.objects.create(
            title="Active Blog 2",
            description="Content for active blog 2",
            is_active=Blog.Active.ACTIVE,
        )
        self.blog2.category.add(self.category)

        self.blog3 = Blog.objects.create(
            title="Canceled Blog",
            description="Content for canceled blog",
            is_active=Blog.Active.CANCEL,
        )
        self.blog3.category.add(self.category)

    def test_active_blogs_manager(self):
        active_blogs = Blog.active.all()
        self.assertEqual(active_blogs.count(), 2)
        self.assertIn(self.blog1, active_blogs)
        self.assertIn(self.blog2, active_blogs)
        self.assertNotIn(self.blog3, active_blogs)

    def test_canceled_blogs_manager(self):
        canceled_blogs = Blog.cancel.all()
        self.assertEqual(canceled_blogs.count(), 1)
        self.assertIn(self.blog3, canceled_blogs)
        self.assertNotIn(self.blog1, canceled_blogs)
        self.assertNotIn(self.blog2, canceled_blogs)
