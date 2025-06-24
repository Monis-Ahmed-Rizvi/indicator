
from django.core.management.base import BaseCommand
from stocks.models import Stock

class Command(BaseCommand):
    help = 'Populate database with common stocks'

    def handle(self, *args, **options):
        common_stocks = [
            {'symbol': 'AAPL', 'company_name': 'Apple Inc.', 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'company_name': 'Alphabet Inc.', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'company_name': 'Microsoft Corporation', 'sector': 'Technology'},
            {'symbol': 'AMZN', 'company_name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
            {'symbol': 'TSLA', 'company_name': 'Tesla Inc.', 'sector': 'Consumer Discretionary'},
            {'symbol': 'META', 'company_name': 'Meta Platforms Inc.', 'sector': 'Technology'},
            {'symbol': 'NVDA', 'company_name': 'NVIDIA Corporation', 'sector': 'Technology'},
            {'symbol': 'BRK.B', 'company_name': 'Berkshire Hathaway Inc.', 'sector': 'Financial Services'},
            {'symbol': 'JPM', 'company_name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
            {'symbol': 'JNJ', 'company_name': 'Johnson & Johnson', 'sector': 'Healthcare'},
            {'symbol': 'V', 'company_name': 'Visa Inc.', 'sector': 'Financial Services'},
            {'symbol': 'PG', 'company_name': 'Procter & Gamble Co.', 'sector': 'Consumer Staples'},
            {'symbol': 'UNH', 'company_name': 'UnitedHealth Group Inc.', 'sector': 'Healthcare'},
            {'symbol': 'HD', 'company_name': 'Home Depot Inc.', 'sector': 'Consumer Discretionary'},
            {'symbol': 'MA', 'company_name': 'Mastercard Inc.', 'sector': 'Financial Services'},
            {'symbol': 'BAC', 'company_name': 'Bank of America Corp.', 'sector': 'Financial Services'},
            {'symbol': 'XOM', 'company_name': 'Exxon Mobil Corporation', 'sector': 'Energy'},
            {'symbol': 'DIS', 'company_name': 'Walt Disney Co.', 'sector': 'Communication Services'},
            {'symbol': 'ADBE', 'company_name': 'Adobe Inc.', 'sector': 'Technology'},
            {'symbol': 'CRM', 'company_name': 'Salesforce Inc.', 'sector': 'Technology'},
        ]

        created_count = 0
        for stock_data in common_stocks:
            stock, created = Stock.objects.get_or_create(
                symbol=stock_data['symbol'],
                defaults={
                    'company_name': stock_data['company_name'],
                    'sector': stock_data['sector']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {stock.symbol} - {stock.company_name}")
            else:
                self.stdout.write(f"Exists: {stock.symbol} - {stock.company_name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(common_stocks)} stocks. {created_count} new stocks created.')
        )
