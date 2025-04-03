from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0002_workoutplan_weekly_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workoutplan',
            name='weekly_plan',
            field=models.JSONField(blank=True, default=dict, help_text='Full week daily workout plan as JSON', null=True),
        ),
    ]
