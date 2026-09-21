from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='recorded_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]