from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('goal', models.CharField(choices=[('weight_loss', 'Weight Loss & Fat Burn'), ('muscle_gain', 'Muscle Gain & Strength Training'), ('endurance', 'Endurance & Stamina Boost'), ('flexibility', 'Flexibility & Mobility'), ('core_strength', 'Core & Functional Strength'), ('balanced_fitness', 'Balanced Fitness & Well-being'), ('athletic_performance', 'Athletic Performance & Conditioning'), ('custom_wellness', 'Customized & Holistic Wellness')], default='balanced_fitness', max_length=50)),
                ('duration_minutes', models.IntegerField(help_text='Total workout duration in minutes')),
                ('intensity', models.CharField(choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], default='moderate', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]