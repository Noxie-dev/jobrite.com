"""
Versioned Rate Engine for MoneyRite

Manages SARS tax tables, UIF thresholds, and medical credits with versioning,
integrity verification, and hot-update capabilities.
"""

import json
import hashlib
import logging
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from django.conf import settings
from django.core.cache import cache
import requests

logger = logging.getLogger(__name__)


@dataclass
class TaxBracket:
    """Tax bracket definition"""
    min_income: Decimal
    max_income: Optional[Decimal]  # None for top bracket
    rate: Decimal
    
    def to_dict(self):
        return {
            'min_income': str(self.min_income),
            'max_income': str(self.max_income) if self.max_income else None,
            'rate': str(self.rate)
        }


@dataclass
class TaxRebate:
    """Tax rebate definition"""
    name: str
    amount: Decimal
    age_category: str
    
    def to_dict(self):
        return {
            'name': self.name,
            'amount': str(self.amount),
            'age_category': self.age_category
        }


@dataclass
class RateConfiguration:
    """Complete rate configuration for a tax year"""
    version: str
    effective_date: date
    tax_year: str
    description: str
    
    # Tax brackets
    tax_brackets: List[TaxBracket]
    
    # Tax rebates
    tax_rebates: List[TaxRebate]
    
    # UIF configuration
    uif_rate: Decimal
    uif_monthly_cap: Decimal
    uif_annual_cap: Decimal
    
    # Medical tax credits
    medical_credit_main: Decimal
    medical_credit_first_dependent: Decimal
    medical_credit_additional_dependent: Decimal
    
    # Metadata
    source_urls: List[str]
    checksum: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'version': self.version,
            'effective_date': self.effective_date.isoformat(),
            'tax_year': self.tax_year,
            'description': self.description,
            'tax_brackets': [bracket.to_dict() for bracket in self.tax_brackets],
            'tax_rebates': [rebate.to_dict() for rebate in self.tax_rebates],
            'uif_rate': str(self.uif_rate),
            'uif_monthly_cap': str(self.uif_monthly_cap),
            'uif_annual_cap': str(self.uif_annual_cap),
            'medical_credit_main': str(self.medical_credit_main),
            'medical_credit_first_dependent': str(self.medical_credit_first_dependent),
            'medical_credit_additional_dependent': str(self.medical_credit_additional_dependent),
            'source_urls': self.source_urls,
            'checksum': self.checksum
        }
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of configuration data"""
        # Create deterministic JSON representation
        data = self.to_dict()
        data.pop('checksum', None)  # Remove checksum from calculation
        
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


class RateEngine:
    """Manages versioned tax rate configurations"""
    
    CACHE_KEY_CURRENT = 'moneyrite:current_rates'
    CACHE_KEY_MANIFEST = 'moneyrite:rates_manifest'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self):
        self.rates_dir = Path(settings.BASE_DIR) / 'moneyrite' / 'rates'
        self.rates_dir.mkdir(exist_ok=True)
        self._current_config: Optional[RateConfiguration] = None
    
    def get_current_rates(self) -> RateConfiguration:
        """Get current active rate configuration"""
        if self._current_config is None:
            # Try cache first
            cached_config = cache.get(self.CACHE_KEY_CURRENT)
            if cached_config:
                self._current_config = self._deserialize_config(cached_config)
            else:
                # Load from file
                self._current_config = self._load_current_config()
                if self._current_config:
                    cache.set(self.CACHE_KEY_CURRENT, self._current_config.to_dict(), self.CACHE_TIMEOUT)
        
        if self._current_config is None:
            # Fallback to hardcoded 2025 rates
            logger.warning("No rate configuration found, using hardcoded 2025 rates")
            self._current_config = self._get_default_2025_config()
        
        return self._current_config
    
    def _load_current_config(self) -> Optional[RateConfiguration]:
        """Load current configuration from file"""
        current_file = self.rates_dir / 'current.json'
        if not current_file.exists():
            return None
        
        try:
            with open(current_file, 'r') as f:
                data = json.load(f)
            return self._deserialize_config(data)
        except Exception as e:
            logger.error(f"Failed to load current rate configuration: {e}")
            return None
    
    def _deserialize_config(self, data: dict) -> RateConfiguration:
        """Deserialize configuration from dictionary"""
        tax_brackets = []
        for bracket_data in data['tax_brackets']:
            tax_brackets.append(TaxBracket(
                min_income=Decimal(bracket_data['min_income']),
                max_income=Decimal(bracket_data['max_income']) if bracket_data['max_income'] else None,
                rate=Decimal(bracket_data['rate'])
            ))
        
        tax_rebates = []
        for rebate_data in data['tax_rebates']:
            tax_rebates.append(TaxRebate(
                name=rebate_data['name'],
                amount=Decimal(rebate_data['amount']),
                age_category=rebate_data['age_category']
            ))
        
        return RateConfiguration(
            version=data['version'],
            effective_date=datetime.fromisoformat(data['effective_date']).date(),
            tax_year=data['tax_year'],
            description=data['description'],
            tax_brackets=tax_brackets,
            tax_rebates=tax_rebates,
            uif_rate=Decimal(data['uif_rate']),
            uif_monthly_cap=Decimal(data['uif_monthly_cap']),
            uif_annual_cap=Decimal(data['uif_annual_cap']),
            medical_credit_main=Decimal(data['medical_credit_main']),
            medical_credit_first_dependent=Decimal(data['medical_credit_first_dependent']),
            medical_credit_additional_dependent=Decimal(data['medical_credit_additional_dependent']),
            source_urls=data['source_urls'],
            checksum=data.get('checksum')
        )
    
    def _get_default_2025_config(self) -> RateConfiguration:
        """Get hardcoded 2025 tax configuration as fallback"""
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
        
        config = RateConfiguration(
            version='2025.1.0',
            effective_date=date(2025, 3, 1),
            tax_year='2025/2026',
            description='SARS Tax Tables 2025/2026 - Hardcoded Fallback',
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
                'https://www.sars.gov.za/tax-rates/medical-tax-credit-rates/'
            ]
        )
        
        config.checksum = config.calculate_checksum()
        return config
    
    def save_configuration(self, config: RateConfiguration, make_current: bool = False) -> bool:
        """Save rate configuration to file"""
        try:
            # Calculate and set checksum
            config.checksum = config.calculate_checksum()
            
            # Save versioned file
            version_file = self.rates_dir / f'rates-{config.version}.json'
            with open(version_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Update current if requested
            if make_current:
                current_file = self.rates_dir / 'current.json'
                with open(current_file, 'w') as f:
                    json.dump(config.to_dict(), f, indent=2)
                
                # Clear cache
                cache.delete(self.CACHE_KEY_CURRENT)
                self._current_config = None
            
            logger.info(f"Saved rate configuration {config.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rate configuration: {e}")
            return False
    
    def verify_integrity(self, config: RateConfiguration) -> bool:
        """Verify configuration integrity"""
        calculated_checksum = config.calculate_checksum()
        return calculated_checksum == config.checksum
    
    def list_available_versions(self) -> List[str]:
        """List all available rate configuration versions"""
        versions = []
        for file_path in self.rates_dir.glob('rates-*.json'):
            version = file_path.stem.replace('rates-', '')
            versions.append(version)
        return sorted(versions, reverse=True)


# Global rate engine instance
rate_engine = RateEngine()
