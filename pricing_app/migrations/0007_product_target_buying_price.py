from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing_app', '0006_remove_salesrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='target_buying_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
