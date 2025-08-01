# Post Subapp

The `post` subapp manages all features related to posts and stories in this project. It provides functionality for creating, updating, deleting, and retrieving posts and stories, as well as handling comments, likes, hashtags, permissions, and story views.

## Features

- CRUD operations for posts and stories
- Commenting and liking system
- Hashtag management
- Story view tracking and expiration
- Content toxicity checking
- Private post handling
- Permissions and access control
- Utilities for serializing comments

## Structure

- `models.py`: Database models for posts, stories, comments, and related entities
- `serializers.py`: Serializers for API data validation and transformation
- `views.py`: API views for handling requests
- `tasks.py`: Background tasks (e.g., for story expiration)
- `utils/`: Helper modules for permissions, toxicity checks, etc.
- `migrations/`: Database migration files
- `test/`: Unit and integration tests
- `urls.py`: URL routing for the post subapp
