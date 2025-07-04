# Generated by Django 4.2 on 2025-06-17 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minha_pagina', '0002_consumorvn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Botija',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField()),
                ('peso_atual', models.FloatField()),
                ('peso_anterior', models.FloatField()),
                ('valor_inicial', models.FloatField()),
                ('data_registro', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='registroconsumo',
            name='tipo',
            field=models.CharField(choices=[('Água', 'Água'), ('Gás', 'Gás'), ('Eletricidade', 'eEetricidade')], max_length=20),
        ),
    ]
