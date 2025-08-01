# User Subapp

The `user` subapp manages all user-related functionality in this project. It handles user registration, authentication, profile management, following system, and user-specific utilities.

## Features

- User registration and authentication
- Profile management (view, update)
- Following and follower system
- Email verification and privacy settings
- Custom management commands (e.g., seeding users)
- Utility functions for user-related operations

## Structure

- `models.py`: Database models for users and related entities
- `serializers.py`: Serializers for user data validation and transformation
- `views.py`: API views for user endpoints
- `urls.py`: URL routing for user-related endpoints
- `schema.py`: GraphQL or API schema definitions
- `signals.py`: Signal handlers for user events
- `admin.py`: Admin interface configuration
- `management/commands/`: Custom Django management commands
- `utils/`: Helper modules for user operations
- `migrations/`: Database migration files
- `test/`: Unit and integration tests