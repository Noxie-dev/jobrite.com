"""
Management command to update tax rates and configurations

Usage:
    python manage.py update_tax_rates --init  # Initialize with 2025 rates
    python manage.py update_tax_rates --verify  # Verify current configuration
    python manage.py update_tax_rates --list  # List available versions
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date
from decimal import Decimal
import json

from moneyrite.rate_engine import RateEngine, RateConfiguration, TaxBracket, TaxRebate


class Command(BaseCommand):
    help = 'Manage tax rate configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--init',
            action='store_true',
            help='Initialize with current 2025 tax rates',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify current configuration integrity',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available rate versions',
        )
        parser.add_argument(
            '--load-version',
            type=str,
            help='Load specific version as current',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export current configuration to file',
        )

    def handle(self, *args, **options):
        rate_engine = RateEngine()

        if options['init']:
            self.init_rates(rate_engine)
        elif options['verify']:
            self.verify_rates(rate_engine)
        elif options['list']:
            self.list_versions(rate_engine)
        elif options['load_version']:
            self.load_version(rate_engine, options['load_version'])
        elif options['export']:
            self.export_config(rate_engine, options['export'])
        else:
            self.stdout.write(self.style.ERROR('Please specify an action. Use --help for options.'))

    def init_rates(self, rate_engine):
        """Initialize with 2025 SARS tax rates"""
        self.stdout.write('Initializing MoneyRite with 2025 SARS tax rates...')
        
        # Create 2025 configuration
        config = self.create_2025_config()
        
        # Save configuration
        if rate_engine.save_configuration(config, make_current=True):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully initialized rates version {config.version}')
            )
            self.stdout.write(f'Tax Year: {config.tax_year}')
            self.stdout.write(f'Effective Date: {config.effective_date}')
            self.stdout.write(f'Checksum: {config.checksum[:16]}...')
        else:
            raise CommandError('Failed to save rate configuration')

    def verify_rates(self, rate_engine):
        """Verify current configuration integrity"""
        self.stdout.write('Verifying current rate configuration...')
        
        try:
            config = rate_engine.get_current_rates()
            
            self.stdout.write(f'Current Version: {config.version}')
            self.stdout.write(f'Tax Year: {config.tax_year}')
            self.stdout.write(f'Effective Date: {config.effective_date}')
            
            if rate_engine.verify_integrity(config):
                self.stdout.write(self.style.SUCCESS('✅ Configuration integrity verified'))
                self.stdout.write(f'Checksum: {config.checksum[:16]}...')
            else:
                self.stdout.write(self.style.ERROR('❌ Configuration integrity check failed'))
                raise CommandError('Configuration may be corrupted')
                
        except Exception as e:
            raise CommandError(f'Failed to verify configuration: {e}')

    def list_versions(self, rate_engine):
        """List available rate versions"""
        self.stdout.write('Available rate configuration versions:')
        
        versions = rate_engine.list_available_versions()
        if not versions:
            self.stdout.write('No saved configurations found.')
            return
        
        current_config = rate_engine.get_current_rates()
        
        for version in versions:
            marker = ' (CURRENT)' if version == current_config.version else ''
            self.stdout.write(f'  • {version}{marker}')

    def load_version(self, rate_engine, version):
        """Load specific version as current"""
        self.stdout.write(f'Loading version {version} as current...')
        
        # This would require implementing version loading in RateEngine
        # For now, show what would happen
        self.stdout.write(self.style.WARNING('Version loading not yet implemented'))
        self.stdout.write('This would:')
        self.stdout.write(f'  1. Load rates-{version}.json')
        self.stdout.write('  2. Verify integrity')
        self.stdout.write('  3. Set as current configuration')
        self.stdout.write('  4. Clear cache')

    def export_config(self, rate_engine, filename):
        """Export current configuration to file"""
        self.stdout.write(f'Exporting current configuration to {filename}...')
        
        try:
            config = rate_engine.get_current_rates()
            
            with open(filename, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Configuration exported to {filename}'))
            
        except Exception as e:
            raise CommandError(f'Failed to export configuration: {e}')

    def create_2025_config(self):
        """Create 2025 SARS tax configuration"""
        tax_brackets = [
            TaxBracket(Decimal('0'), Decimal('237100'), Decimal('0.18')),
            TaxBracket(Decimal('237100'), Decimal('370500'), Decimal('0.26')),
            TaxBracket(Decimal('370500'), Decimal('512800'), Decimal('0.31')),
            TaxBracket(Decimal('512800'), Decimal('673000'), Decimal('0.36')),
            TaxBracket(Decimal('673000'), Decimal('857900'), Decimal('0.39')),
            TaxBracket(Decimal('857900'), Decimal('1817000'), Decimal('0.41')),
            TaxBracket(Decimal('1817000'), None, Decimal('0.45')),
        ]
        
        tax_rebates = [
            TaxRebate('Primary Rebate', Decimal('17235'), 'under_65'),
            TaxRebate('Secondary Rebate', Decimal('3300'), '65_to_74'),
            TaxRebate('Tertiary Rebate', Decimal('1470'), '75_plus'),
        ]
        
        return RateConfiguration(
            version='2025.1.0',
            effective_date=date(2025, 3, 1),
            tax_year='2025/2026',
            description='SARS Tax Tables 2025/2026 - Official rates with no changes from 2024',
            tax_brackets=tax_brackets,
            tax_rebates=tax_rebates,
            uif_rate=Decimal('0.01'),
            uif_monthly_cap=Decimal('177.12'),
            uif_annual_cap=Decimal('17712'),
            medical_credit_main=Decimal('364'),
            medical_credit_first_dependent=Decimal('364'),
            medical_credit_additional_dependent=Decimal('246'),
            source_urls=[
                'https://www.sars.gov.za/tax-rates/income-tax/rates-of-tax-for-individuals/',
                'https://www.sars.gov.za/tax-rates/medical-tax-credit-rates/',
                'https://www.sars.gov.za/types-of-tax/unemployment-insurance-fund/'
            ]
        )
