# Generated by Django 4.2 on 2025-06-24 00:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('company_name', models.CharField(max_length=255)),
                ('sector', models.CharField(blank=True, max_length=100)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['symbol'],
            },
        ),
        migrations.CreateModel(
            name='IndicatorResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indicator_name', models.CharField(max_length=50)),
                ('timeframe', models.CharField(max_length=20)),
                ('success_rate', models.FloatField()),
                ('avg_return', models.FloatField()),
                ('total_signals', models.IntegerField()),
                ('max_drawdown', models.FloatField(default=0)),
                ('sharpe_ratio', models.FloatField(default=0)),
                ('date_calculated', models.DateTimeField(default=django.utils.timezone.now)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicator_results', to='stocks.stock')),
            ],
            options={
                'ordering': ['-success_rate'],
            },
        ),
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open_price', models.FloatField()),
                ('high_price', models.FloatField()),
                ('low_price', models.FloatField()),
                ('close_price', models.FloatField()),
                ('volume', models.BigIntegerField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_data', to='stocks.stock')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('stock', 'date')},
            },
        ),
    ]
