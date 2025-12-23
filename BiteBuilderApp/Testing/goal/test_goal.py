"""
Test suite for Goal model functionality.
Comprehensive testing with high coverage for all goal-related functionality.
"""

import pytest
import uuid
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from apps.core.models import Goal
from apps.users.models import Profile


@pytest.fixture
def test_user(db):
    """Create a test user for testing."""
    return Profile.objects.create(
        id=str(uuid.uuid4()),
        username='testuser',
        email='test@example.com'
    )


@pytest.fixture
def test_user2(db):
    """Create a second test user for testing."""
    return Profile.objects.create(
        id=str(uuid.uuid4()),
        username='testuser2',
        email='test2@example.com'
    )


@pytest.fixture
def test_goal(db, test_user):
    """Create a test goal for testing."""
    return Goal.objects.create(
        user=test_user,
        target_weight_kg=70.0,
        target_calories=2000,
        consumed_calories=1500.0,
        reset_frequency=Goal.ResetFrequency.DAILY
    )


# =========================================================
# GOAL MODEL TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalModel:
    """Tests for Goal model functionality."""
    
    def test_goal_creation(self, test_user):
        """Test basic goal creation."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=75.0,
            target_calories=2500,
            consumed_calories=1800.0
        )
        
        assert goal.user == test_user
        assert goal.target_weight_kg == 75.0
        assert goal.target_calories == 2500
        assert goal.consumed_calories == 1800.0
        assert goal.id is not None
        assert isinstance(goal.id, uuid.UUID)
    
    def test_goal_creation_with_defaults(self, test_user):
        """Test goal creation with default values."""
        goal = Goal.objects.create(user=test_user)
        
        assert goal.user == test_user
        assert goal.target_weight_kg is None
        assert goal.target_calories is None
        assert goal.consumed_calories == 0.0
        assert goal.reset_frequency == Goal.ResetFrequency.NONE
    
    def test_goal_str_representation(self, test_goal):
        """Test goal string representation."""
        str_repr = str(test_goal)
        assert str(test_goal.user_id) in str_repr
        assert test_goal.reset_frequency in str_repr
    
    def test_goal_meta_options(self):
        """Test goal model meta options."""
        assert Goal._meta.db_table == "bitebuilder.goal"
    
    def test_goal_user_relationship(self, test_goal, test_user):
        """Test goal user relationship."""
        assert test_goal.user == test_user
        assert test_user.goal == test_goal
    
    def test_goal_one_to_one_constraint(self, test_user):
        """Test that one user can only have one goal."""
        # Create first goal
        Goal.objects.create(user=test_user)
        
        # Try to create second goal for same user
        with pytest.raises(IntegrityError):
            Goal.objects.create(user=test_user)
    
    def test_goal_cascade_delete_user(self, test_goal):
        """Test that goal is deleted when user is deleted."""
        goal_id = test_goal.id
        user_id = test_goal.user.id
        
        # Delete the user
        test_goal.user.delete()
        
        # Check that goal is also deleted
        assert not Goal.objects.filter(id=goal_id).exists()
        assert not Profile.objects.filter(id=user_id).exists()
    
    def test_goal_related_name(self, test_goal, test_user):
        """Test goal related name access."""
        assert test_user.goal == test_goal
        assert hasattr(test_user, 'goal')
    
    def test_goal_db_column(self, test_goal):
        """Test goal db column configuration."""
        # Check that the field uses the correct db_column
        field = Goal._meta.get_field('user')
        assert field.db_column == 'user_id'


# =========================================================
# GOAL RESET FREQUENCY TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalResetFrequency:
    """Tests for Goal ResetFrequency choices."""
    
    def test_reset_frequency_choices(self):
        """Test reset frequency choices are available."""
        choices = Goal.ResetFrequency.choices
        expected_choices = [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('none', 'No automatic reset')
        ]
        assert choices == expected_choices
    
    def test_reset_frequency_daily(self, test_user):
        """Test goal with daily reset frequency."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency=Goal.ResetFrequency.DAILY
        )
        assert goal.reset_frequency == Goal.ResetFrequency.DAILY
        assert goal.reset_frequency == 'daily'
    
    def test_reset_frequency_weekly(self, test_user):
        """Test goal with weekly reset frequency."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency=Goal.ResetFrequency.WEEKLY
        )
        assert goal.reset_frequency == Goal.ResetFrequency.WEEKLY
        assert goal.reset_frequency == 'weekly'
    
    def test_reset_frequency_monthly(self, test_user):
        """Test goal with monthly reset frequency."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency=Goal.ResetFrequency.MONTHLY
        )
        assert goal.reset_frequency == Goal.ResetFrequency.MONTHLY
        assert goal.reset_frequency == 'monthly'
    
    def test_reset_frequency_none(self, test_user):
        """Test goal with no reset frequency."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency=Goal.ResetFrequency.NONE
        )
        assert goal.reset_frequency == Goal.ResetFrequency.NONE
        assert goal.reset_frequency == 'none'
    
    def test_reset_frequency_default(self, test_user):
        """Test goal with default reset frequency."""
        goal = Goal.objects.create(user=test_user)
        assert goal.reset_frequency == Goal.ResetFrequency.NONE
    
    def test_reset_frequency_string_assignment(self, test_user):
        """Test reset frequency can be assigned as string."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency='daily'
        )
        assert goal.reset_frequency == 'daily'
    
    def test_reset_frequency_invalid_choice(self, test_user):
        """Test reset frequency with invalid choice."""
        goal = Goal.objects.create(user=test_user)
        goal.reset_frequency = 'invalid'
        # This should not raise an error during assignment
        # but might during validation or save
        goal.save()
        assert goal.reset_frequency == 'invalid'


# =========================================================
# GOAL FIELD TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalFields:
    """Tests for Goal model fields."""
    
    def test_target_weight_kg_field(self, test_user):
        """Test target_weight_kg field properties."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=65.5
        )
        assert goal.target_weight_kg == 65.5
        assert isinstance(goal.target_weight_kg, float)
    
    def test_target_weight_kg_null(self, test_user):
        """Test target_weight_kg can be null."""
        goal = Goal.objects.create(user=test_user)
        assert goal.target_weight_kg is None
    
    def test_target_weight_kg_blank(self, test_user):
        """Test target_weight_kg can be blank."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=None
        )
        assert goal.target_weight_kg is None
    
    def test_target_calories_field(self, test_user):
        """Test target_calories field properties."""
        goal = Goal.objects.create(
            user=test_user,
            target_calories=2200
        )
        assert goal.target_calories == 2200
        assert isinstance(goal.target_calories, int)
    
    def test_target_calories_null(self, test_user):
        """Test target_calories can be null."""
        goal = Goal.objects.create(user=test_user)
        assert goal.target_calories is None
    
    def test_target_calories_blank(self, test_user):
        """Test target_calories can be blank."""
        goal = Goal.objects.create(
            user=test_user,
            target_calories=None
        )
        assert goal.target_calories is None
    
    def test_consumed_calories_field(self, test_user):
        """Test consumed_calories field properties."""
        goal = Goal.objects.create(
            user=test_user,
            consumed_calories=1200.5
        )
        assert goal.consumed_calories == 1200.5
        assert isinstance(goal.consumed_calories, float)
    
    def test_consumed_calories_default(self, test_user):
        """Test consumed_calories default value."""
        goal = Goal.objects.create(user=test_user)
        assert goal.consumed_calories == 0.0
    
    def test_consumed_calories_zero(self, test_user):
        """Test consumed_calories can be zero."""
        goal = Goal.objects.create(
            user=test_user,
            consumed_calories=0.0
        )
        assert goal.consumed_calories == 0.0
    
    def test_consumed_calories_negative(self, test_user):
        """Test consumed_calories can be negative."""
        goal = Goal.objects.create(
            user=test_user,
            consumed_calories=-100.0
        )
        assert goal.consumed_calories == -100.0
    
    def test_reset_frequency_max_length(self, test_user):
        """Test reset_frequency max_length constraint."""
        goal = Goal.objects.create(
            user=test_user,
            reset_frequency='daily'  # 5 characters, should be fine
        )
        assert goal.reset_frequency == 'daily'
    
    def test_reset_frequency_long_string(self, test_user):
        """Test reset_frequency with long string."""
        goal = Goal.objects.create(user=test_user)
        # This should not raise an error during assignment
        goal.reset_frequency = 'very_long_string_that_exceeds_max_length'
        goal.save()
        assert goal.reset_frequency == 'very_long_string_that_exceeds_max_length'


# =========================================================
# GOAL RELATIONSHIP TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalRelationships:
    """Tests for Goal model relationships."""
    
    def test_goal_user_foreign_key(self, test_user):
        """Test goal user foreign key relationship."""
        goal = Goal.objects.create(user=test_user)
        
        # Test forward relationship
        assert goal.user == test_user
        assert goal.user_id == test_user.id
        
        # Test reverse relationship
        assert test_user.goal == goal
    
    def test_goal_user_related_name(self, test_goal, test_user):
        """Test goal user related name."""
        assert hasattr(test_user, 'goal')
        assert test_user.goal == test_goal
    
    def test_goal_user_cascade_delete(self, test_goal):
        """Test goal is deleted when user is deleted."""
        goal_id = test_goal.id
        
        # Delete user
        test_goal.user.delete()
        
        # Check goal is also deleted
        assert not Goal.objects.filter(id=goal_id).exists()
    
    def test_goal_user_set_null_not_allowed(self, test_user):
        """Test that user field cannot be set to null."""
        goal = Goal.objects.create(user=test_user)
        
        # This should raise an error since user is required
        with pytest.raises(ValidationError):
            goal.user = None
            goal.full_clean()
    
    def test_goal_user_required(self):
        """Test that user field is required."""
        with pytest.raises(IntegrityError):
            Goal.objects.create()


# =========================================================
# GOAL EDGE CASES AND BOUNDARY TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_goal_zero_values(self, test_user):
        """Test goal with zero values."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=0.0,
            target_calories=0,
            consumed_calories=0.0
        )
        
        assert goal.target_weight_kg == 0.0
        assert goal.target_calories == 0
        assert goal.consumed_calories == 0.0
    
    def test_goal_negative_values(self, test_user):
        """Test goal with negative values."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=-10.0,
            target_calories=-100,
            consumed_calories=-50.0
        )
        
        assert goal.target_weight_kg == -10.0
        assert goal.target_calories == -100
        assert goal.consumed_calories == -50.0
    
    def test_goal_very_large_values(self, test_user):
        """Test goal with very large values."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=999999.99,
            target_calories=999999,
            consumed_calories=999999.99
        )
        
        assert goal.target_weight_kg == 999999.99
        assert goal.target_calories == 999999
        assert goal.consumed_calories == 999999.99
    
    def test_goal_float_precision(self, test_user):
        """Test goal float precision."""
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=123.456789,
            consumed_calories=987.654321
        )
        
        assert goal.target_weight_kg == 123.456789
        assert goal.consumed_calories == 987.654321
    
    def test_goal_string_representation_edge_cases(self, test_user):
        """Test string representation with edge case values."""
        # Test with None values
        goal = Goal.objects.create(user=test_user)
        str_repr = str(goal)
        assert str(test_user.id) in str_repr
        assert goal.reset_frequency in str_repr
        
        # Test with zero values
        goal.target_weight_kg = 0.0
        goal.target_calories = 0
        goal.consumed_calories = 0.0
        goal.save()
        
        str_repr = str(goal)
        assert str(test_user.id) in str_repr
        assert goal.reset_frequency in str_repr


# =========================================================
# GOAL PERFORMANCE AND QUERY TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalPerformance:
    """Tests for performance and query optimization."""
    
    def test_goal_select_related(self, test_goal):
        """Test that select_related works properly for goal queries."""
        # Test select_related optimization
        goals = Goal.objects.select_related('user').all()
        for goal in goals:
            # Accessing related objects should not trigger additional queries
            _ = goal.user.username
            _ = goal.user.email
        
        # Verify that we can access the related objects
        assert len(goals) == 1
        assert goals[0].user.username == test_goal.user.username
        assert goals[0].user.email == test_goal.user.email
    
    def test_goal_bulk_operations(self, test_user, test_user2):
        """Test bulk operations with goals."""
        # Create multiple users
        users = [test_user, test_user2]
        
        # Bulk create goals
        goals = []
        for i, user in enumerate(users):
            goals.append(Goal(
                user=user,
                target_weight_kg=70.0 + i,
                target_calories=2000 + i * 100,
                consumed_calories=1500.0 + i * 50
            ))
        
        Goal.objects.bulk_create(goals)
        
        # Verify all were created
        assert Goal.objects.count() == 2
        
        # Test bulk update
        Goal.objects.update(consumed_calories=2000.0)
        
        # Verify update
        for goal in Goal.objects.all():
            assert goal.consumed_calories == 2000.0
    
    def test_goal_filtering(self, test_user, test_user2):
        """Test goal filtering operations."""
        # Create goals with different reset frequencies
        goal1 = Goal.objects.create(
            user=test_user,
            reset_frequency=Goal.ResetFrequency.DAILY
        )
        goal2 = Goal.objects.create(
            user=test_user2,
            reset_frequency=Goal.ResetFrequency.WEEKLY
        )
        
        # Test filtering by reset frequency
        daily_goals = Goal.objects.filter(reset_frequency=Goal.ResetFrequency.DAILY)
        assert daily_goals.count() == 1
        assert daily_goals.first() == goal1
        
        weekly_goals = Goal.objects.filter(reset_frequency=Goal.ResetFrequency.WEEKLY)
        assert weekly_goals.count() == 1
        assert weekly_goals.first() == goal2
        
        # Test filtering by user
        user1_goals = Goal.objects.filter(user=test_user)
        assert user1_goals.count() == 1
        assert user1_goals.first() == goal1
    
    def test_goal_ordering(self, test_user, test_user2):
        """Test goal ordering operations."""
        # Create goals with different consumed calories
        goal1 = Goal.objects.create(
            user=test_user,
            consumed_calories=1000.0
        )
        goal2 = Goal.objects.create(
            user=test_user2,
            consumed_calories=2000.0
        )
        
        # Test ordering by consumed calories
        goals_asc = Goal.objects.order_by('consumed_calories')
        assert goals_asc[0] == goal1
        assert goals_asc[1] == goal2
        
        goals_desc = Goal.objects.order_by('-consumed_calories')
        assert goals_desc[0] == goal2
        assert goals_desc[1] == goal1


# =========================================================
# GOAL INTEGRATION TESTS
# =========================================================

@pytest.mark.django_db
class TestGoalIntegration:
    """Integration tests for goal functionality."""
    
    def test_goal_user_integration(self, test_user):
        """Test goal integration with user model."""
        # Create goal
        goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=70.0,
            target_calories=2000
        )
        
        # Test accessing goal through user
        assert test_user.goal == goal
        assert test_user.goal.target_weight_kg == 70.0
        assert test_user.goal.target_calories == 2000
        
        # Test updating goal through user
        test_user.goal.consumed_calories = 1500.0
        test_user.goal.save()
        
        # Verify update
        goal.refresh_from_db()
        assert goal.consumed_calories == 1500.0
    
    def test_goal_serialization_roundtrip(self, test_user):
        """Test goal serialization and deserialization."""
        # Create goal
        original_goal = Goal.objects.create(
            user=test_user,
            target_weight_kg=75.0,
            target_calories=2500,
            consumed_calories=1800.0,
            reset_frequency=Goal.ResetFrequency.DAILY
        )
        
        # Get goal data
        goal_data = {
            'target_weight_kg': original_goal.target_weight_kg,
            'target_calories': original_goal.target_calories,
            'consumed_calories': original_goal.consumed_calories,
            'reset_frequency': original_goal.reset_frequency
        }
        
        # Create new goal with same data (using different user to avoid unique constraint)
        user2 = Profile.objects.create(
            id=str(uuid.uuid4()),
            username='testuser2',
            email='test2@example.com'
        )
        
        new_goal = Goal.objects.create(
            user=user2,
            **goal_data
        )
        
        # Verify data matches
        assert new_goal.target_weight_kg == original_goal.target_weight_kg
        assert new_goal.target_calories == original_goal.target_calories
        assert new_goal.consumed_calories == original_goal.consumed_calories
        assert new_goal.reset_frequency == original_goal.reset_frequency
    
    def test_goal_multiple_users(self, test_user, test_user2):
        """Test multiple users with goals."""
        # Create goals for both users
        goal1 = Goal.objects.create(
            user=test_user,
            target_weight_kg=70.0,
            target_calories=2000
        )
        goal2 = Goal.objects.create(
            user=test_user2,
            target_weight_kg=80.0,
            target_calories=2500
        )
        
        # Test that goals are independent
        assert goal1.user == test_user
        assert goal2.user == test_user2
        assert goal1 != goal2
        
        # Test accessing goals through users
        assert test_user.goal == goal1
        assert test_user2.goal == goal2
        
        # Test that goals have different data
        assert goal1.target_weight_kg != goal2.target_weight_kg
        assert goal1.target_calories != goal2.target_calories
