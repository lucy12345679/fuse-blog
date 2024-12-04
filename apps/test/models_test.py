import pytest
from django.utils.text import slugify

from apps.models import Site, CustomUser, Category, Blog, BlogViewing, Message, Region, District, Comment


@pytest.mark.django_db
def test_site_str():
    site = Site.objects.create(
        name="Test Site",
        picture="test.jpg",
        about_us="About Us Information",
        social={"twitter": "https://twitter.com/test"},
        adress="123 Test Street",
        email="test@example.com",
        phone="+123456789"
    )
    assert str(site) == "Test Site"


@pytest.mark.django_db
def test_blog_slug():
    user = CustomUser.objects.create_user(
        username="author", email="author@example.com", password="password123"
    )
    category = Category.objects.create(name="Test Category")
    blog = Blog.objects.create(
        title="Test Blog",
        author=user,
        description="This is a test blog",
    )
    blog.category.add(category)

    assert blog.slug == "test-blog"
    assert blog.category.count() == 1


@pytest.mark.django_db
def test_blog_viewing():
    user = CustomUser.objects.create_user(
        username="viewer", email="viewer@example.com", password="password123"
    )
    blog = Blog.objects.create(
        title="Test Blog",
        author=user,
        description="This is a test blog",
    )
    BlogViewing.objects.create(blog=blog)
    BlogViewing.objects.create(blog=blog)

    assert blog.view_count == 2


@pytest.mark.django_db
def test_message_creation():
    user = CustomUser.objects.create_user(
        username="messenger", email="messenger@example.com", password="password123"
    )
    message = Message.objects.create(
        author=user,
        subject="Test Subject",
        message="This is a test message",
    )

    assert str(message.subject) == "Test Subject"
    assert message.status is False


@pytest.mark.django_db
def test_region_and_district_creation():
    region = Region.objects.create(name="Test Region")
    district = District.objects.create(name="Test District", region=region)

    assert district.region == region
    assert str(region.name) == "Test Region"
    assert str(district.name) == "Test District"


@pytest.mark.django_db
def test_category_without_slug():
    category = Category.objects.create(name="Technology")

    assert category.slug == slugify("Technology")
    assert category.name == "Technology"

    duplicate_category = Category.objects.create(name="Technology")
    assert duplicate_category.slug != slugify("Technology")
    assert duplicate_category.slug.startswith("technology-")

@pytest.mark.django_db
def test_active_blogs_manager():
    category = Category.objects.create(name="Technology")

    blog1 = Blog.objects.create(
        title="Active Blog 1",
        description="Content for active blog 1",
        is_active=Blog.Active.ACTIVE,
    )
    blog1.category.add(category)

    blog2 = Blog.objects.create(
        title="Active Blog 2",
        description="Content for active blog 2",
        is_active=Blog.Active.ACTIVE,
    )
    blog2.category.add(category)

    blog3 = Blog.objects.create(
        title="Canceled Blog",
        description="Content for canceled blog",
        is_active=Blog.Active.CANCEL,
    )
    blog3.category.add(category)

    active_blogs = Blog.active.all()
    assert active_blogs.count() == 2
    assert blog1 in active_blogs
    assert blog2 in active_blogs
    assert blog3 not in active_blogs

@pytest.mark.django_db
def test_cancel_blogs_manager():
    blog1 = Blog.objects.create(
        title="Active Blog",
        description="Content for active blog",
        is_active=Blog.Active.ACTIVE,
    )

    blog2 = Blog.objects.create(
        title="Canceled Blog 1",
        description="Content for canceled blog 1",
        is_active=Blog.Active.CANCEL,
    )

    blog3 = Blog.objects.create(
        title="Canceled Blog 2",
        description="Content for canceled blog 2",
        is_active=Blog.Active.CANCEL,
    )

    canceled_blogs = Blog.cancel.all()
    assert canceled_blogs.count() == 2
    assert blog2 in canceled_blogs
    assert blog3 in canceled_blogs
    assert blog1 not in canceled_blogs

@pytest.mark.django_db
def test_blog_slug_auto_generation():
    # Create a blog without providing a slug
    blog = Blog.objects.create(
        title="Test Blog",
        description="This is a test blog",
        is_active=Blog.Active.ACTIVE,
    )

    assert blog.slug == "test-blog"

    duplicate_blog = Blog.objects.create(
        title="Test Blog",
        description="This is another test blog",
        is_active=Blog.Active.ACTIVE,
    )

    assert duplicate_blog.slug != "test-blog"
    assert duplicate_blog.slug.startswith("test-blog")

@pytest.mark.django_db
def test_multiple_comments_on_blog():
    # Create a user
    user = CustomUser.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="securepassword",
    )

    # Create a blog
    blog = Blog.objects.create(
        title="Test Blog",
        description="This is a test blog",
        is_active=Blog.Active.ACTIVE,
    )

    # Create multiple comments
    Comment.objects.create(comment="First comment.", author=user, blog=blog)
    Comment.objects.create(comment="Second comment.", author=user, blog=blog)

    # Retrieve comments using the related name
    comments = blog.comment_set.all()
    assert comments.count() == 2
    assert comments[0].comment == "First comment."
    assert comments[1].comment == "Second comment."

@pytest.mark.django_db
def test_district_creation():
    # Create a region
    region = Region.objects.create(name="Test Region")

    # Create a district linked to the region
    district = District.objects.create(name="Test District", region=region)

    # Verify the district attributes
    assert district.name == "Test District"
    assert district.region == region

    # Ensure string representation matches the name
    assert str(district) == "Test District"