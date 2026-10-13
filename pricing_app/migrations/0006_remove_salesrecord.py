from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pricing_app', '0005_alter_competitorprice_competitor_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesrecord',
            name='product',
        ),
        migrations.DeleteModel(
            name='SalesRecord',
        ),
    ]
