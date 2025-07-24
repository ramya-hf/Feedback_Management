from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from feedback.models import Board, Feedback, Comment, FeedbackStatusHistory
import random

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to create sample data for the feedback management system.
    
    Usage:
    python manage.py create_sample_data --boards 3 --feedback 10 --comments 20
    """
    help = 'Create sample boards, feedback, and comments for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--boards',
            type=int,
            default=3,
            help='Number of boards to create'
        )
        parser.add_argument(
            '--feedback',
            type=int,
            default=10,
            help='Number of feedback items to create per board'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=20,
            help='Number of comments to create per feedback item'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of additional users to create'
        )

    def handle(self, *args, **options):
        num_boards = options['boards']
        num_feedback = options['feedback']
        num_comments = options['comments']
        num_users = options['users']

        self.stdout.write("Creating sample data for feedback management system...")

        # Create additional users
        users = self.create_users(num_users)
        
        # Get existing admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            users.append(admin_user)

        if not users:
            self.stdout.write(self.style.ERROR("No users found. Please create an admin user first."))
            return

        # Create boards
        boards = self.create_boards(num_boards, users[0])
        
        # Create feedback items
        feedback_items = self.create_feedback(num_feedback, boards, users)
        
        # Create comments
        self.create_comments(num_comments, feedback_items, users)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(boards)} boards\n'
                f'- {len(feedback_items)} feedback items\n'
                f'- {Comment.objects.count()} comments\n'
                f'- {len(users)} users'
            )
        )

    def create_users(self, num_users):
        """Create sample users."""
        users = []
        for i in range(num_users):
            user, created = User.objects.get_or_create(
                email=f'user{i+1}@example.com',
                defaults={
                    'username': f'user{i+1}',
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                    'role': random.choice(['contributor', 'moderator']),
                    'is_email_verified': True,
                    'company': f'Company {i+1}',
                    'job_title': random.choice(['Developer', 'Designer', 'Manager', 'Analyst']),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f"Created user: {user.email}")
            users.append(user)
        return users

    def create_boards(self, num_boards, owner):
        """Create sample boards."""
        board_names = [
            "Product Feedback",
            "Feature Requests", 
            "Bug Reports",
            "User Experience",
            "Mobile App",
            "Web Platform",
            "API Improvements",
            "Documentation",
            "Performance",
            "Security"
        ]
        
        boards = []
        for i in range(num_boards):
            name = board_names[i] if i < len(board_names) else f"Board {i+1}"
            board, created = Board.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Sample board for {name.lower()}',
                    'slug': f'board-{i+1}',
                    'visibility': random.choice(['public', 'private']),
                    'owner': owner,
                    'allow_anonymous_feedback': random.choice([True, False]),
                    'require_approval': random.choice([True, False]),
                    'allow_comments': True,
                    'allow_voting': True,
                }
            )
            if created:
                # Add some moderators and members
                users = User.objects.filter(role__in=['moderator', 'contributor'])[:3]
                board.moderators.add(*users[:2])
                board.members.add(*users[2:])
                self.stdout.write(f"Created board: {board.name}")
            boards.append(board)
        return boards

    def create_feedback(self, num_feedback, boards, users):
        """Create sample feedback items."""
        feedback_items = []
        
        titles = [
            "Add dark mode support",
            "Improve search functionality", 
            "Fix login issue on mobile",
            "Add export to PDF feature",
            "Optimize page loading speed",
            "Add keyboard shortcuts",
            "Improve error messages",
            "Add bulk actions",
            "Fix notification system",
            "Add data visualization",
            "Improve accessibility",
            "Add multi-language support",
            "Fix responsive design issues",
            "Add file upload progress",
            "Improve user onboarding"
        ]
        
        descriptions = [
            "This would greatly improve the user experience, especially for users who prefer dark themes.",
            "The current search is too basic and doesn't provide relevant results.",
            "Users are experiencing issues logging in on mobile devices.",
            "Many users have requested the ability to export their data to PDF format.",
            "The application is taking too long to load, especially on slower connections.",
            "Power users would benefit from keyboard shortcuts for common actions.",
            "Error messages are not clear enough and don't help users understand what went wrong.",
            "Users need to be able to perform actions on multiple items at once.",
            "The notification system is not working reliably across different browsers.",
            "Data visualization would help users better understand their information.",
            "The application needs better accessibility features for users with disabilities.",
            "Supporting multiple languages would make the app more accessible globally.",
            "The responsive design breaks on certain screen sizes.",
            "Users need to see the progress of file uploads.",
            "New users find it difficult to get started with the application."
        ]

        for board in boards:
            for i in range(num_feedback):
                title = random.choice(titles)
                description = random.choice(descriptions)
                author = random.choice(users)
                
                feedback = Feedback.objects.create(
                    title=f"{title} #{i+1}",
                    description=description,
                    board=board,
                    author=author,
                    status=random.choice(Feedback.Status.choices)[0],
                    priority=random.choice(Feedback.Priority.choices)[0],
                    category=random.choice(Feedback.Category.choices)[0],
                    assigned_to=random.choice(users) if random.choice([True, False]) else None,
                )
                
                # Add some votes
                voters = random.sample(list(users), min(3, len(users)))
                for voter in voters:
                    if random.choice([True, False]):
                        feedback.upvotes.add(voter)
                    else:
                        feedback.downvotes.add(voter)
                
                feedback_items.append(feedback)
                self.stdout.write(f"Created feedback: {feedback.title}")
        
        return feedback_items

    def create_comments(self, num_comments, feedback_items, users):
        """Create sample comments."""
        comment_texts = [
            "This is a great idea! I've been waiting for this feature.",
            "I agree, this would be very useful for our workflow.",
            "Have you considered the performance implications?",
            "This is already implemented in the latest version.",
            "I think this should be a high priority item.",
            "We should gather more user feedback before implementing this.",
            "This would solve a major pain point for our team.",
            "I'm not sure this is the right approach. Have you considered alternatives?",
            "This is exactly what we need! When can we expect this?",
            "I've been experiencing this issue too. It's quite frustrating.",
            "This would be a nice-to-have but not critical for our use case.",
            "I think this should be lower priority compared to other features.",
            "Great suggestion! This would improve the user experience significantly.",
            "I'm concerned about the security implications of this feature.",
            "This is a duplicate of an existing request.",
            "I'd like to see more details about the implementation plan.",
            "This feature would be perfect for our enterprise customers.",
            "I think we should focus on fixing bugs first before adding new features.",
            "This would require significant changes to the architecture.",
            "I'm excited about this feature! Can't wait to see it implemented."
        ]
        
        for feedback in feedback_items:
            num_feedback_comments = random.randint(0, num_comments // len(feedback_items))
            
            for i in range(num_feedback_comments):
                author = random.choice(users)
                content = random.choice(comment_texts)
                
                comment = Comment.objects.create(
                    content=content,
                    feedback=feedback,
                    author=author,
                )
                
                # Add some votes to comments
                voters = random.sample(list(users), min(2, len(users)))
                for voter in voters:
                    if random.choice([True, False]):
                        comment.upvotes.add(voter)
                    else:
                        comment.downvotes.add(voter)
                
                # Create some replies
                if random.choice([True, False]) and i > 0:
                    parent_comment = Comment.objects.filter(feedback=feedback).first()
                    if parent_comment:
                        reply_content = random.choice([
                            "I agree with this comment.",
                            "Good point!",
                            "I have a different perspective on this.",
                            "This is helpful information.",
                            "Thanks for sharing your thoughts."
                        ])
                        
                        reply = Comment.objects.create(
                            content=reply_content,
                            feedback=feedback,
                            author=random.choice(users),
                            parent=parent_comment,
                        )
                
                self.stdout.write(f"Created comment on: {feedback.title}") 