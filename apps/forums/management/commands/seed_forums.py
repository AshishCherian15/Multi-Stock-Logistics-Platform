from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from forums.models import ForumCategory, Topic, Post
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed forum data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding forums...')
        
        users = list(User.objects.all()[:5])
        if not users:
            self.stdout.write(self.style.ERROR('❌ No users found'))
            return
        
        # Create categories
        cats = [
            {'name': 'General Discussion', 'desc': 'Platform-wide chat, announcements, and casual interaction', 'icon': 'fa-comments', 'color': 'primary', 'topics': 15, 'posts': 127},
            {'name': 'Product Reviews', 'desc': 'Honest feedback and user experiences', 'icon': 'fa-star', 'color': 'success', 'topics': 12, 'posts': 89},
            {'name': 'Technical Support', 'desc': 'Get help with technical issues and troubleshooting', 'icon': 'fa-tools', 'color': 'warning', 'topics': 18, 'posts': 156},
            {'name': 'Business Tips', 'desc': 'Share strategies and business insights', 'icon': 'fa-lightbulb', 'color': 'info', 'topics': 10, 'posts': 74},
        ]
        
        for i, cat_data in enumerate(cats):
            cat, _ = ForumCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['desc'], 'icon': cat_data['icon'], 'color': cat_data['color'], 'order': i+1}
            )
            
            # Create topics
            for j in range(cat_data['topics']):
                topic, created = Topic.objects.get_or_create(
                    category=cat,
                    title=f'{cat_data["name"]} Topic {j+1}',
                    defaults={'author': users[j % len(users)], 'views': j*10, 'created_at': timezone.now() - timedelta(hours=j)}
                )
                
                if created:
                    # Create posts
                    posts_count = cat_data['posts'] // cat_data['topics']
                    for k in range(posts_count):
                        Post.objects.create(
                            topic=topic,
                            author=users[k % len(users)],
                            content=f'This is post {k+1} in {topic.title}. Lorem ipsum dolor sit amet.',
                            created_at=timezone.now() - timedelta(hours=j, minutes=k*10)
                        )
        
        self.stdout.write(self.style.SUCCESS('✅ Forums seeded!'))
