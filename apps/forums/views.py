from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import ForumCategory, Topic, Post

def is_team_member(user):
	"""Check if user is a team member (not customer)"""
	return user.is_staff or user.is_superuser or (hasattr(user, 'role') and user.role.role != 'customer')

def forum_home(request):
	if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.role == 'customer':
		return HttpResponseForbidden("Customers cannot access forums")
	categories = ForumCategory.objects.all()
	for cat in categories:
		cat.topic_count = cat.topics.count()
		cat.post_count = sum(t.post_count() for t in cat.topics.all())
		cat.latest = cat.topics.order_by('-updated_at').first()
	return render(request, 'forums/home.html', {'categories': categories})

def category_topics(request, category_id):
	if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.role == 'customer':
		return HttpResponseForbidden("Customers cannot access forums")
	category = get_object_or_404(ForumCategory, id=category_id)
	topics = category.topics.all()
	return render(request, 'forums/topics.html', {'category': category, 'topics': topics})

def topic_detail(request, topic_id):
	if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.role == 'customer':
		return HttpResponseForbidden("Customers cannot access forums")
	topic = get_object_or_404(Topic, id=topic_id)
	topic.views += 1
	topic.save(update_fields=['views'])
	posts = topic.posts.all()
	return render(request, 'forums/topic.html', {'topic': topic, 'posts': posts})

@login_required
def create_topic(request, category_id):
	if hasattr(request.user, 'role') and request.user.role.role == 'customer':
		return HttpResponseForbidden("Customers cannot create topics")
	category = get_object_or_404(ForumCategory, id=category_id)
	if request.method == 'POST':
		title = request.POST.get('title')
		content = request.POST.get('content')
		topic = Topic.objects.create(category=category, title=title, author=request.user)
		Post.objects.create(topic=topic, author=request.user, content=content)
		messages.success(request, 'Topic created!')
		return redirect('forums:topic_detail', topic_id=topic.id)
	return render(request, 'forums/create_topic.html', {'category': category})

@login_required
def create_post(request, topic_id):
	if hasattr(request.user, 'role') and request.user.role.role == 'customer':
		return HttpResponseForbidden("Customers cannot post in forums")
	topic = get_object_or_404(Topic, id=topic_id)
	if topic.is_locked:
		messages.error(request, 'Topic is locked')
		return redirect('forums:topic_detail', topic_id=topic.id)
	if request.method == 'POST':
		content = request.POST.get('content')
		Post.objects.create(topic=topic, author=request.user, content=content)
		messages.success(request, 'Reply posted!')
		return redirect('forums:topic_detail', topic_id=topic.id)
	return redirect('forums:topic_detail', topic_id=topic.id)

@login_required
def edit_post(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.author != request.user and not request.user.is_staff:
		messages.error(request, 'Permission denied')
		return redirect('forums:topic_detail', topic_id=post.topic.id)
	if request.method == 'POST':
		post.content = request.POST.get('content')
		post.save()
		messages.success(request, 'Post updated!')
		return redirect('forums:topic_detail', topic_id=post.topic.id)
	return render(request, 'forums/edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.author != request.user and not request.user.is_staff:
		messages.error(request, 'Permission denied')
		return redirect('forums:topic_detail', topic_id=post.topic.id)
	topic = post.topic
	if post.topic.posts.count() == 1:
		topic.delete()
		messages.success(request, 'Topic deleted!')
		return redirect('forums:category_topics', category_id=topic.category.id)
	post.delete()
	messages.success(request, 'Post deleted!')
	return redirect('forums:topic_detail', topic_id=topic.id)

@login_required
def delete_topic(request, topic_id):
	topic = get_object_or_404(Topic, id=topic_id)
	if topic.author != request.user and not request.user.is_staff:
		messages.error(request, 'Permission denied')
		return redirect('forums:topic_detail', topic_id=topic.id)
	category_id = topic.category.id
	topic.delete()
	messages.success(request, 'Topic deleted!')
	return redirect('forums:category_topics', category_id=category_id)
