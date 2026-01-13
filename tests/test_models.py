from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from dashboard.models import (
    Profile, Department, Subject, Material,
    Rating, Comment, SavedMaterial, Post,
    PostComment, StudyGroup
)
import tempfile
from PIL import Image

class ModelTests(TestCase):
    
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
            department=self.department,
            description='Software development course'
        )
        
        # Create another user for interactions
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test automatic profile creation for new user"""
        # Profile should be created automatically via signals
        self.assertEqual(Profile.objects.count(), 2)  # 2 users created
        profile = self.user.profile
        
        # Check default values
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.image.name, 'default.jpg')
        self.assertEqual(profile.bio, None)
        self.assertEqual(profile.cgpa, None)
        self.assertEqual(profile.credits_completed, 0)
        self.assertEqual(profile.department, None)
        self.assertEqual(profile.is_studying, False)
        self.assertEqual(profile.reputation, 0)
        
        # Check __str__ method
        self.assertEqual(str(profile), 'testuser Profile')

    def test_profile_update(self):
        """Test profile update functionality"""
        profile = self.user.profile
        
        # Update profile fields
        profile.bio = 'Test bio for user'
        profile.cgpa = 3.75
        profile.credits_completed = 120
        profile.department = self.department
        profile.is_studying = True
        profile.reputation = 10
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        # Check updated values
        self.assertEqual(profile.bio, 'Test bio for user')
        self.assertEqual(profile.cgpa, 3.75)
        self.assertEqual(profile.credits_completed, 120)
        self.assertEqual(profile.department, self.department)
        self.assertEqual(profile.is_studying, True)
        self.assertEqual(profile.reputation, 10)

    def test_profile_with_custom_image(self):
        """Test profile with custom image upload"""
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        
        # Update profile image
        profile = self.user.profile
        profile.image.save('test.jpg', image_file, save=True)
        
        # Check image was saved
        self.assertIn('profile_pics', profile.image.name)
        self.assertTrue(profile.image.name.endswith('.jpg'))
        
        # Cleanup
        profile.image.delete()

    def test_department_model(self):
        """Test Department model"""
        dept = Department.objects.create(
            name='Electrical and Electronic Engineering',
            code='EEE'
        )
        
        self.assertEqual(str(dept), 'EEE - Electrical and Electronic Engineering')
        self.assertEqual(dept.name, 'Electrical and Electronic Engineering')
        self.assertEqual(dept.code, 'EEE')

    def test_subject_model(self):
        """Test Subject model"""
        subject = Subject.objects.create(
            name='Data Structures',
            code='CSE220',
            department=self.department,
            description='Fundamental data structures course'
        )
        
        self.assertEqual(str(subject), 'CSE220 - Data Structures')
        self.assertEqual(subject.name, 'Data Structures')
        self.assertEqual(subject.code, 'CSE220')
        self.assertEqual(subject.department, self.department)
        self.assertEqual(subject.description, 'Fundamental data structures course')

    def test_material_model(self):
        """Test Material model creation"""
        # Create a test file
        test_file = SimpleUploadedFile(
            'test_note.pdf',
            b'Test file content',
            content_type='application/pdf'
        )
        
        material = Material.objects.create(
            title='Test Material',
            description='This is a test material',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject,
            material_type='note',
            tags='test,exam,note'
        )
        
        # Check material properties
        self.assertEqual(str(material), 'Test Material')
        self.assertEqual(material.title, 'Test Material')
        self.assertEqual(material.description, 'This is a test material')
        self.assertEqual(material.uploaded_by, self.user)
        self.assertEqual(material.subject, self.subject)
        self.assertEqual(material.material_type, 'note')
        self.assertEqual(material.tags, 'test,exam,note')
        self.assertEqual(material.is_approved, True)  # Default
        self.assertEqual(material.reports, 0)  # Default
        self.assertEqual(material.downloads, 0)  # Default
        self.assertEqual(material.views, 0)  # Default
        
        # Check file was saved
        self.assertIn('materials/', material.file.name)
        
        # Check ordering
        materials = Material.objects.all()
        self.assertEqual(materials.count(), 1)

    def test_material_ordering(self):
        """Test material ordering by upload date"""
        # Create materials with different upload dates
        test_file = SimpleUploadedFile('test.pdf', b'content')
        
        material1 = Material.objects.create(
            title='Old Material',
            description='Old',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        material2 = Material.objects.create(
            title='New Material',
            description='New',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        # By default, should be ordered by -upload_date (newest first)
        materials = Material.objects.all()
        self.assertEqual(materials[0].title, 'New Material')
        self.assertEqual(materials[1].title, 'Old Material')

    def test_rating_model(self):
        """Test Rating model"""
        # Create material first
        test_file = SimpleUploadedFile('test.pdf', b'content')
        material = Material.objects.create(
            title='Test Material',
            description='Test',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        # Create rating
        rating = Rating.objects.create(
            material=material,
            user=self.user,
            score=5
        )
        
        self.assertEqual(str(rating), '5/5 by testuser for Test Material')
        self.assertEqual(rating.material, material)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.score, 5)
        
        # Test unique constraint
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Rating.objects.create(
                material=material,
                user=self.user,
                score=4
            )

    def test_comment_model(self):
        """Test Comment model"""
        # Create material first
        test_file = SimpleUploadedFile('test.pdf', b'content')
        material = Material.objects.create(
            title='Test Material',
            description='Test',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        # Create comment
        comment = Comment.objects.create(
            material=material,
            user=self.user,
            content='This is a test comment'
        )
        
        self.assertEqual(str(comment), 'Comment by testuser')
        self.assertEqual(comment.material, material)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.upvotes, 0)
        self.assertEqual(comment.downvotes, 0)
        self.assertEqual(comment.is_reported, False)

    def test_saved_material_model(self):
        """Test SavedMaterial model"""
        # Create material first
        test_file = SimpleUploadedFile('test.pdf', b'content')
        material = Material.objects.create(
            title='Test Material',
            description='Test',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        # Save material
        saved = SavedMaterial.objects.create(
            user=self.user,
            material=material,
            note='Important for exam'
        )
        
        self.assertEqual(str(saved), 'testuser saved Test Material')
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.material, material)
        self.assertEqual(saved.note, 'Important for exam')
        
        # Test unique constraint
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            SavedMaterial.objects.create(
                user=self.user,
                material=material
            )

    def test_post_model(self):
        """Test Post model"""
        post = Post.objects.create(
            user=self.user,
            title='Test Discussion',
            content='This is a test discussion post',
            post_type='discussion',
            subject=self.subject,
            tags='test,discussion,help'
        )
        
        self.assertEqual(str(post), 'Test Discussion')
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.title, 'Test Discussion')
        self.assertEqual(post.content, 'This is a test discussion post')
        self.assertEqual(post.post_type, 'discussion')
        self.assertEqual(post.subject, self.subject)
        self.assertEqual(post.tags, 'test,discussion,help')
        self.assertEqual(post.upvotes, 0)
        self.assertEqual(post.downvotes, 0)
        self.assertEqual(post.is_reported, False)
        self.assertEqual(post.is_pinned, False)

    def test_post_comment_model(self):
        """Test PostComment model"""
        # Create post first
        post = Post.objects.create(
            user=self.user,
            title='Test Post',
            content='Test content',
            post_type='discussion'
        )
        
        # Create comment on post
        comment = PostComment.objects.create(
            post=post,
            user=self.user,
            content='This is a comment on the post'
        )
        
        self.assertEqual(str(comment), 'Comment by testuser')
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'This is a comment on the post')
        self.assertEqual(comment.upvotes, 0)
        self.assertEqual(comment.downvotes, 0)
        self.assertEqual(comment.is_reported, False)

    def test_study_group_model(self):
        """Test StudyGroup model"""
        group = StudyGroup.objects.create(
            name='CSE470 Study Group',
            description='Study group for Software Engineering',
            subject=self.subject,
            created_by=self.user,
            is_public=True,
            max_members=15
        )
        
        # Add members
        group.members.add(self.user)
        group.members.add(self.user2)
        
        self.assertEqual(str(group), 'CSE470 Study Group')
        self.assertEqual(group.name, 'CSE470 Study Group')
        self.assertEqual(group.description, 'Study group for Software Engineering')
        self.assertEqual(group.subject, self.subject)
        self.assertEqual(group.created_by, self.user)
        self.assertEqual(group.is_public, True)
        self.assertEqual(group.max_members, 15)
        self.assertEqual(group.members.count(), 2)
        self.assertIn(self.user, group.members.all())
        self.assertIn(self.user2, group.members.all())

    def test_material_type_choices(self):
        """Test Material type choices"""
        test_file = SimpleUploadedFile('test.pdf', b'content')
        
        # Test all material types
        types = ['note', 'slide', 'assignment', 'book', 'question', 'other']
        for mat_type in types:
            material = Material.objects.create(
                title=f'{mat_type} Material',
                description='Test',
                file=test_file,
                uploaded_by=self.user,
                subject=self.subject,
                material_type=mat_type
            )
            
            # Check get_material_type_display method
            display = material.get_material_type_display()
            self.assertIsNotNone(display)
            
            # Clean up
            material.delete()

    def test_post_type_choices(self):
        """Test Post type choices"""
        types = ['personal', 'discussion', 'question', 'announcement', 'resource']
        for post_type in types:
            post = Post.objects.create(
                user=self.user,
                title=f'{post_type} Post',
                content='Test content',
                post_type=post_type
            )
            
            # Check get_post_type_display method
            display = post.get_post_type_display()
            self.assertIsNotNone(display)
            
            # Clean up
            post.delete()

    def test_cgpa_validation(self):
        """Test CGPA field validation"""
        profile = self.user.profile
        
        # Test valid CGPA
        profile.cgpa = 3.5
        profile.save()
        self.assertEqual(profile.cgpa, 3.5)
        
        # Test valid CGPA at boundaries
        profile.cgpa = 0.0
        profile.save()
        self.assertEqual(profile.cgpa, 0.0)
        
        profile.cgpa = 4.0
        profile.save()
        self.assertEqual(profile.cgpa, 4.0)
        
        # Test invalid CGPA (should still save due to model validation)
        profile.cgpa = 4.5  # Above max
        profile.save()
        self.assertEqual(profile.cgpa, 4.5)  # Django doesn't enforce at model level
        
        profile.cgpa = -1.0  # Below min
        profile.save()
        self.assertEqual(profile.cgpa, -1.0)  # Django doesn't enforce at model level

    def test_material_views_increment(self):
        """Test material views increment functionality"""
        test_file = SimpleUploadedFile('test.pdf', b'content')
        material = Material.objects.create(
            title='Test Material',
            description='Test',
            file=test_file,
            uploaded_by=self.user,
            subject=self.subject
        )
        
        # Initial views should be 0
        self.assertEqual(material.views, 0)
        
        # Simulate view increment
        material.views += 1
        material.save()
        material.refresh_from_db()
        
        self.assertEqual(material.views, 1)
        
        # Increment multiple times
        material.views += 5
        material.save()
        material.refresh_from_db()
        
        self.assertEqual(material.views, 6)

    def tearDown(self):
        """Clean up after tests"""
        # Delete any uploaded files
        for material in Material.objects.all():
            if material.file:
                material.file.delete()
        
        for profile in Profile.objects.all():
            if profile.image and profile.image.name != 'default.jpg':
                profile.image.delete()