# apps/shops/migrations/0002_shoppost_shoppostimage_postlike.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopPost',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('post_type', models.CharField(
                    choices=[
                        ('realisation', '✨ Réalisation'),
                        ('produit',     '🛒 Produit'),
                        ('promo',       '🎉 Promotion'),
                        ('soin',        '💆 Soin'),
                        ('avant_apres', '🔄 Avant / Après'),
                        ('annonce',     '📢 Annonce'),
                    ],
                    default='realisation', max_length=20
                )),
                ('caption',      models.TextField(blank=True)),
                ('price',        models.DecimalField(decimal_places=0, max_digits=10, null=True, blank=True)),
                ('is_published', models.BooleanField(default=True)),
                ('likes_count',  models.PositiveIntegerField(default=0)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('updated_at',   models.DateTimeField(auto_now=True)),
                ('shop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='posts', to='shops.shop'
                )),
            ],
            options={
                'verbose_name': 'Publication',
                'verbose_name_plural': 'Publications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ShopPostImage',
            fields=[
                ('id',    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='shops/posts/%Y/%m/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('post',  models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='images', to='shops.shoppost'
                )),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='likes', to='shops.shoppost'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={'unique_together': {('post', 'user')}},
        ),
    ]
