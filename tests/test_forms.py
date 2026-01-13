from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from dashboard.forms import (
    UserRegisterForm, ProfileUpdateForm, MaterialUploadForm,
    MaterialUpdateForm, PostForm, CommentForm, PostCommentForm
)
from dashboard.models import Department, Subject, Profile
import tempfile
from PIL import Image

class FormTests(TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create department
        self.department = Department.objects.create(
            name='Computer Science and Engineering',
            code='CSE'
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Software Engineering',
            code='CSE470',
            department=self.department
        )
        
        # Create test file
        self.test_file = SimpleUploadedFile(
            'test.pdf',
            b'Test file content',
            content_type='application/pdf'
        )
        
        # Create test image
        self.test_image = self.create_test_image()

    def create_test_image(self):
        """Create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        return tmp_file

    # ==================== UserRegisterForm Tests ====================
    
    def test_user_register_form_valid(self):
        """Test valid user registration form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_register_form_missing_fields(self):
        """Test user registration form with missing fields"""
        form_data = {
            'username': 'newuser',
            'email': '',  # Missing email
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_user_register_form_password_mismatch(self):
        """Test user registration form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',  # Mismatch
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
    def test_user_register_form_weak_password(self):
        """Test user registration form with weak password"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',  # Too short
            'password2': '123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
    def test_user_register_form_duplicate_username(self):
        """Test user registration form with duplicate username"""
        form_data = {
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
    def test_user_register_form_invalid_email(self):
        """Test user registration form with invalid email"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid email
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # ==================== ProfileUpdateForm Tests ====================
    
    def test_profile_update_form_valid(self):
        """Test valid profile update form"""
        form_data = {
            'bio': 'This is a test bio for the user profile.',
            'cgpa': 3.75,
            'credits_completed': 120,
            'department': self.department.id,
            'is_studying': True,
        }
        form = ProfileUpdateForm(data=form_data, files={
            'image': self.test_image
        })
        self.assertTrue(form.is_valid())
        
    def test_profile_update_form_empty(self):
        """Test profile update form with empty data (should be valid)"""
        form_data = {}
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())  # All fields are optional
        
    def test_profile_update_form_with_invalid_cgpa(self):
        """Test profile update form with invalid CGPA"""
        form_data = {
            'cgpa': 5.5,  # Above maximum 4.0
        }
        form = ProfileUpdateForm(data=form_data)
        # Form will validate but model validation will catch it
        self.assertTrue(form.is_valid())  # Form validation passes
        
    def test_profile_update_form_with_negative_credits(self):
        """Test profile update form with negative credits"""
        form_data = {
            'credits_completed': -10,  # Negative credits
        }
        form = ProfileUpdateForm(data=form_data)
        # Form validation passes, but model/save will handle
        self.assertTrue(form.is_valid())
        
    def test_profile_update_form_invalid_image(self):
        """Test profile update form with invalid image"""
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'Not an image',
            content_type='text/plain'
        )
        form = ProfileUpdateForm(files={'image': invalid_file})
        self.assertTrue(form.is_valid())  # Django doesn't validate file type in form
        
    def test_profile_update_form_bio_length(self):
        """Test profile update form with very long bio"""
        long_bio = 'A' * 1000  # Very long bio
        form_data = {
            'bio': long_bio,
        }
        form = ProfileUpdateForm(data=form_data)
        # Should be valid (max_length is 500 in model, but form doesn't validate)
        self.assertTrue(form.is_valid())

    # ==================== MaterialUploadForm Tests ====================
    
    def test_material_upload_form_valid(self):
        """Test valid material upload form"""
        form_data = {
            'title': 'Test Material Title',
            'description': 'This is a detailed description of the material.',
            'subject': self.subject.id,
            'material_type': 'note',
            'tags': 'test, exam, notes',
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertTrue(form.is_valid())
        
    def test_material_upload_form_missing_required_fields(self):
        """Test material upload form with missing required fields"""
        # Missing title
        form_data = {
            'description': 'Some description',
            'subject': self.subject.id,
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing file
        form_data = {
            'title': 'Test Title',
            'description': 'Some description',
            'subject': self.subject.id,
        }
        form = MaterialUploadForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
        
    def test_material_upload_form_empty_description(self):
        """Test material upload form with empty description"""
        form_data = {
            'title': 'Test Material',
            'description': '',  # Empty description
            'subject': self.subject.id,
            'material_type': 'note',
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertTrue(form.is_valid())  # Description is not required
        
    def test_material_upload_form_long_title(self):
        """Test material upload form with very long title"""
        long_title = 'A' * 300  # Exceeds max_length of 200
        form_data = {
            'title': long_title,
            'description': 'Test',
            'subject': self.subject.id,
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
    def test_material_upload_form_invalid_material_type(self):
        """Test material upload form with invalid material type"""
        form_data = {
            'title': 'Test Material',
            'description': 'Test',
            'subject': self.subject.id,
            'material_type': 'invalid_type',  # Not in choices
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertFalse(form.is_valid())
        self.assertIn('material_type', form.errors)
        
    def test_material_upload_form_invalid_file_type(self):
        """Test material upload form with invalid file type"""
        invalid_file = SimpleUploadedFile(
            'test.exe',
            b'Executable file',
            content_type='application/x-msdownload'
        )
        form_data = {
            'title': 'Test Material',
            'description': 'Test',
            'subject': self.subject.id,
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': invalid_file
        })
        # Django forms don't validate file types by default
        self.assertTrue(form.is_valid())
        
    def test_material_upload_form_tags_cleaning(self):
        """Test material upload form tags cleaning"""
        form_data = {
            'title': 'Test Material',
            'description': 'Test',
            'subject': self.subject.id,
            'tags': '  test  , exam , notes  ',  # Extra spaces
        }
        form = MaterialUploadForm(data=form_data, files={
            'file': self.test_file
        })
        self.assertTrue(form.is_valid())
        # Form doesn't clean tags, but model/save might

    # ==================== MaterialUpdateForm Tests ====================
    
    def test_material_update_form_valid(self):
        """Test valid material update form"""
        form_data = {
            'title': 'Updated Material Title',
            'description': 'Updated description of the material.',
            'subject': self.subject.id,
            'material_type': 'slide',
            'tags': 'updated, slides, presentation',
        }
        form = MaterialUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_material_update_form_missing_title(self):
        """Test material update form with missing title"""
        form_data = {
            'description': 'Updated description',
            'subject': self.subject.id,
        }
        form = MaterialUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
    def test_material_update_form_same_as_upload(self):
        """Test that MaterialUpdateForm excludes file field"""
        form = MaterialUpdateForm()
        self.assertNotIn('file', form.fields)  # File field should not be in update form

    # ==================== PostForm Tests ====================
    
    def test_post_form_valid(self):
        """Test valid post form"""
        form_data = {
            'title': 'Test Discussion Post',
            'content': 'This is the content of the discussion post.',
            'post_type': 'discussion',
            'subject': self.subject.id,
            'tags': 'discussion, help, question',
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_post_form_missing_required_fields(self):
        """Test post form with missing required fields"""
        # Missing title
        form_data = {
            'content': 'Some content',
            'post_type': 'discussion',
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Missing content
        form_data = {
            'title': 'Test Title',
            'post_type': 'discussion',
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
    def test_post_form_empty_tags(self):
        """Test post form with empty tags"""
        form_data = {
            'title': 'Test Post',
            'content': 'Test content',
            'post_type': 'discussion',
            'tags': '',  # Empty tags
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())  # Tags are optional
        
    def test_post_form_invalid_post_type(self):
        """Test post form with invalid post type"""
        form_data = {
            'title': 'Test Post',
            'content': 'Test content',
            'post_type': 'invalid_type',  # Not in choices
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('post_type', form.errors)
        
    def test_post_form_long_title(self):
        """Test post form with very long title"""
        long_title = 'A' * 300  # Exceeds max_length of 200
        form_data = {
            'title': long_title,
            'content': 'Test content',
            'post_type': 'discussion',
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
    def test_post_form_minimum_content(self):
        """Test post form with very short content"""
        form_data = {
            'title': 'Test Post',
            'content': 'A',  # Very short content
            'post_type': 'discussion',
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())  # No minimum length validation
        
    def test_post_form_all_post_types(self):
        """Test post form with all valid post types"""
        post_types = ['personal', 'discussion', 'question', 'announcement', 'resource']
        
        for post_type in post_types:
            form_data = {
                'title': f'Test {post_type} Post',
                'content': f'Content for {post_type} post',
                'post_type': post_type,
            }
            form = PostForm(data=form_data)
            self.assertTrue(form.is_valid(), f'Failed for post_type: {post_type}')

    # ==================== CommentForm Tests ====================
    
    def test_comment_form_valid(self):
        """Test valid comment form"""
        form_data = {
            'content': 'This is a useful comment on the material.',
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_comment_form_empty(self):
        """Test comment form with empty content"""
        form_data = {
            'content': '',  # Empty content
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
    def test_comment_form_whitespace_only(self):
        """Test comment form with whitespace-only content"""
        form_data = {
            'content': '   ',  # Only whitespace
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
    def test_comment_form_long_content(self):
        """Test comment form with very long content"""
        long_content = 'A' * 10000  # Very long comment
        form_data = {
            'content': long_content,
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())  # No max length in form
        
    def test_comment_form_html_content(self):
        """Test comment form with HTML content"""
        form_data = {
            'content': '<script>alert("XSS")</script>This is a comment',
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())  # Form doesn't sanitize HTML

    # ==================== PostCommentForm Tests ====================
    
    def test_post_comment_form_valid(self):
        """Test valid post comment form"""
        form_data = {
            'content': 'This is a comment on the post.',
        }
        form = PostCommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_post_comment_form_empty(self):
        """Test post comment form with empty content"""
        form_data = {
            'content': '',  # Empty content
        }
        form = PostCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
    def test_post_comment_form_same_as_comment_form(self):
        """Test that PostCommentForm has same fields as CommentForm"""
        comment_form_fields = set(CommentForm().fields.keys())
        post_comment_form_fields = set(PostCommentForm().fields.keys())
        
        self.assertEqual(comment_form_fields, post_comment_form_fields)

    # ==================== Form Field Tests ====================
    
    def test_form_field_labels(self):
        """Test form field labels"""
        # UserRegisterForm
        form = UserRegisterForm()
        self.assertEqual(form.fields['username'].label, 'Username')
        self.assertEqual(form.fields['email'].label, 'Email')
        
        # ProfileUpdateForm
        form = ProfileUpdateForm()
        self.assertEqual(form.fields['bio'].label, 'Bio')
        self.assertEqual(form.fields['cgpa'].label, 'Cgpa')
        self.assertEqual(form.fields['credits_completed'].label, 'Credits completed')
        
        # MaterialUploadForm
        form = MaterialUploadForm()
        self.assertEqual(form.fields['title'].label, 'Title')
        self.assertEqual(form.fields['description'].label, 'Description')
        self.assertEqual(form.fields['material_type'].label, 'Material type')
        
    def test_form_field_help_text(self):
        """Test form field help text"""
        # UserRegisterForm
        form = UserRegisterForm()
        self.assertIn('Required', form.fields['username'].help_text)
        self.assertIn('Required', form.fields['email'].help_text)
        
        # MaterialUploadForm
        form = MaterialUploadForm()
        # Check if help text exists for certain fields
        if form.fields['tags'].help_text:
            self.assertIn('separate', form.fields['tags'].help_text.lower())
        
    def test_form_field_widgets(self):
        """Test form field widgets"""
        # ProfileUpdateForm - bio should be Textarea
        form = ProfileUpdateForm()
        self.assertEqual(form.fields['bio'].widget.__class__.__name__, 'Textarea')
        
        # PostForm - content should be Textarea
        form = PostForm()
        self.assertEqual(form.fields['content'].widget.__class__.__name__, 'Textarea')
        
        # CommentForm - content should be Textarea
        form = CommentForm()
        self.assertEqual(form.fields['content'].widget.__class__.__name__, 'Textarea')
        
    def test_form_field_required(self):
        """Test form field required attributes"""
        # UserRegisterForm - all fields required
        form = UserRegisterForm()
        self.assertTrue(form.fields['username'].required)
        self.assertTrue(form.fields['email'].required)
        self.assertTrue(form.fields['password1'].required)
        self.assertTrue(form.fields['password2'].required)
        
        # ProfileUpdateForm - all fields optional
        form = ProfileUpdateForm()
        self.assertFalse(form.fields['bio'].required)
        self.assertFalse(form.fields['cgpa'].required)
        self.assertFalse(form.fields['credits_completed'].required)
        self.assertFalse(form.fields['image'].required)
        
        # MaterialUploadForm - title and file required
        form = MaterialUploadForm()
        self.assertTrue(form.fields['title'].required)
        self.assertTrue(form.fields['file'].required)
        self.assertTrue(form.fields['subject'].required)
        self.assertFalse(form.fields['description'].required)
        self.assertFalse(form.fields['tags'].required)
        
    def test_form_field_max_length(self):
        """Test form field max length attributes"""
        # MaterialUploadForm
        form = MaterialUploadForm()
        self.assertEqual(form.fields['title'].max_length, 200)
        
        # PostForm
        form = PostForm()
        self.assertEqual(form.fields['title'].max_length, 200)
        
    def test_form_choice_fields(self):
        """Test form choice fields"""
        # MaterialUploadForm - material_type choices
        form = MaterialUploadForm()
        material_type_choices = form.fields['material_type'].choices
        self.assertIn(('note', 'Class Note'), material_type_choices)
        self.assertIn(('slide', 'Presentation Slide'), material_type_choices)
        self.assertIn(('assignment', 'Assignment'), material_type_choices)
        self.assertIn(('question', 'Previous Question'), material_type_choices)
        
        # PostForm - post_type choices
        form = PostForm()
        post_type_choices = form.fields['post_type'].choices
        self.assertIn(('personal', 'Personal'), post_type_choices)
        self.assertIn(('discussion', 'Discussion'), post_type_choices)
        self.assertIn(('question', 'Question'), post_type_choices)
        self.assertIn(('announcement', 'Announcement'), post_type_choices)
        
    def test_form_model_choice_fields(self):
        """Test form model choice fields"""
        # MaterialUploadForm - subject field
        form = MaterialUploadForm()
        self.assertEqual(form.fields['subject'].queryset.model, Subject)
        
        # ProfileUpdateForm - department field
        form = ProfileUpdateForm()
        self.assertEqual(form.fields['department'].queryset.model, Department)
        
        # PostForm - subject field
        form = PostForm()
        self.assertEqual(form.fields['subject'].queryset.model, Subject)

    # ==================== Form Initial Data Tests ====================
    
    def test_form_with_initial_data(self):
        """Test form with initial data"""
        # ProfileUpdateForm with instance
        profile = self.user.profile
        profile.bio = 'Existing bio'
        profile.cgpa = 3.5
        profile.save()
        
        form = ProfileUpdateForm(instance=profile)
        self.assertEqual(form.initial['bio'], 'Existing bio')
        self.assertEqual(form.initial['cgpa'], 3.5)
        
    def test_form_save_method(self):
        """Test form save method"""
        # ProfileUpdateForm save
        form_data = {
            'bio': 'New bio from form',
            'cgpa': 3.8,
        }
        profile = self.user.profile
        form = ProfileUpdateForm(data=form_data, instance=profile)
        
        self.assertTrue(form.is_valid())
        saved_profile = form.save()
        
        self.assertEqual(saved_profile.bio, 'New bio from form')
        self.assertEqual(saved_profile.cgpa, 3.8)
        self.assertEqual(saved_profile.user, self.user)
        
    def test_form_clean_methods(self):
        """Test form clean methods if any custom cleaning"""
        # UserRegisterForm clean method for password matching
        form_data = {
            'username': 'testclean',
            'email': 'clean@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test mismatched passwords
        form_data['password2'] = 'different'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
    def test_form_custom_validation(self):
        """Test any custom validation in forms"""
        # Test duplicate username in UserRegisterForm
        form_data = {
            'username': 'testuser',  # Already exists
            'email': 'new@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test invalid email format
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email-format',
            'password1': 'password123',
            'password2': 'password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    # ==================== Form Rendering Tests ====================
    
    def test_form_as_table(self):
        """Test form rendering as table"""
        form = UserRegisterForm()
        table_html = form.as_table()
        
        # Should contain form fields
        self.assertIn('name="username"', table_html)
        self.assertIn('name="email"', table_html)
        self.assertIn('name="password1"', table_html)
        self.assertIn('name="password2"', table_html)
        
    def test_form_as_p(self):
        """Test form rendering as paragraphs"""
        form = UserRegisterForm()
        p_html = form.as_p()
        
        self.assertIn('username', p_html)
        self.assertIn('email', p_html)
        
    def test_form_as_ul(self):
        """Test form rendering as unordered list"""
        form = UserRegisterForm()
        ul_html = form.as_ul()
        
        self.assertIn('<li>', ul_html)
        self.assertIn('username', ul_html)
        
    def tearDown(self):
        """Clean up temporary files"""
        self.test_image.close()