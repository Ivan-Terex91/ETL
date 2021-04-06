# Generated by Django 3.1 on 2021-04-06 08:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='идентификатор')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
            ],
            options={
                'verbose_name': 'жанр',
                'verbose_name_plural': 'жанры',
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='идентификатор')),
                ('title', models.CharField(max_length=255, verbose_name='название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='описание')),
                ('creation_date', models.DateField(blank=True, db_index=True, verbose_name='дата создания фильма')),
                ('age_limit', models.PositiveSmallIntegerField(db_index=True, validators=[django.core.validators.MaxValueValidator(21)], verbose_name='ограничение по возрасту')),
                ('rating', models.FloatField(blank=True, db_index=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='рейтинг пользователей')),
                ('imdb_rating', models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='IMDB рейтинг')),
                ('movie_type', models.CharField(choices=[('movie', 'фильм'), ('serial', 'сериал'), ('tv_show', 'шоу'), ('cartoon', 'мультфильм')], db_index=True, max_length=20, verbose_name='тип')),
                ('file_path', models.FileField(blank=True, upload_to='movie_files/', verbose_name='файл')),
            ],
            options={
                'verbose_name': 'кинопроизведение',
                'verbose_name_plural': 'кинопроизведения',
            },
        ),
        migrations.CreateModel(
            name='MoviePerson',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='идентификатор')),
                ('role', models.CharField(choices=[('director', 'режиссер'), ('actor', 'актер'), ('writer', 'сценарист')], db_index=True, max_length=20, verbose_name='роль')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='идентификатор')),
                ('firstname', models.CharField(max_length=128, verbose_name='имя')),
                ('lastname', models.CharField(max_length=128, verbose_name='фамилия')),
                ('birthdate', models.DateField(verbose_name='дата рождения')),
                ('birthplace', models.CharField(max_length=255, verbose_name='место рождения')),
            ],
            options={
                'verbose_name': 'Человек',
                'verbose_name_plural': 'Люди',
            },
        ),
        migrations.AddIndex(
            model_name='person',
            index=models.Index(fields=['modified'], name='movies_pers_modifie_c7f904_idx'),
        ),
        migrations.AddConstraint(
            model_name='person',
            constraint=models.UniqueConstraint(fields=('firstname', 'lastname', 'birthdate', 'birthplace'), name='person_unique'),
        ),
        migrations.AddField(
            model_name='movieperson',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.movie', verbose_name='кинопроизведение'),
        ),
        migrations.AddField(
            model_name='movieperson',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movies.person', verbose_name='человек'),
        ),
        migrations.AddField(
            model_name='movie',
            name='genres',
            field=models.ManyToManyField(db_index=True, to='movies.Genre', verbose_name='Жанры'),
        ),
        migrations.AddField(
            model_name='movie',
            name='persons',
            field=models.ManyToManyField(through='movies.MoviePerson', to='movies.Person'),
        ),
        migrations.AddIndex(
            model_name='genre',
            index=models.Index(fields=['modified'], name='movies_genr_modifie_8b830f_idx'),
        ),
        migrations.AddConstraint(
            model_name='movieperson',
            constraint=models.UniqueConstraint(fields=('movie', 'person', 'role'), name='movie_person_unique'),
        ),
        migrations.AddIndex(
            model_name='movie',
            index=models.Index(fields=['modified'], name='movies_movi_modifie_9179a7_idx'),
        ),
        migrations.AddConstraint(
            model_name='movie',
            constraint=models.UniqueConstraint(fields=('title', 'creation_date'), name='movie_unique'),
        ),
    ]
