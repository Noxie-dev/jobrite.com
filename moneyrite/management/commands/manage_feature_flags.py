"""
Feature Flag Management Command

Manage feature flags, canary deployments, and release safety mechanisms.
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from moneyrite.feature_flags import feature_flags, RolloutStrategy


class Command(BaseCommand):
    help = 'Manage feature flags and release safety'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all feature flags',
        )
        parser.add_argument(
            '--status',
            type=str,
            help='Get status of specific feature flag',
        )
        parser.add_argument(
            '--enable',
            type=str,
            help='Enable feature flag',
        )
        parser.add_argument(
            '--disable',
            type=str,
            help='Disable feature flag',
        )
        parser.add_argument(
            '--emergency-disable',
            type=str,
            help='Emergency disable feature flag',
        )
        parser.add_argument(
            '--set-percentage',
            nargs=2,
            metavar=('FLAG', 'PERCENTAGE'),
            help='Set percentage rollout for flag',
        )
        parser.add_argument(
            '--canary-status',
            type=str,
            help='Get canary deployment status',
        )
        parser.add_argument(
            '--promote-canary',
            type=str,
            help='Promote canary to full rollout',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_flags(options['json'])
        elif options['status']:
            self.show_flag_status(options['status'], options['json'])
        elif options['enable']:
            self.enable_flag(options['enable'])
        elif options['disable']:
            self.disable_flag(options['disable'])
        elif options['emergency_disable']:
            self.emergency_disable_flag(options['emergency_disable'])
        elif options['set_percentage']:
            self.set_percentage_rollout(options['set_percentage'][0], options['set_percentage'][1])
        elif options['canary_status']:
            self.show_canary_status(options['canary_status'], options['json'])
        elif options['promote_canary']:
            self.promote_canary(options['promote_canary'])
        else:
            self.stdout.write(self.style.ERROR('Please specify an action. Use --help for options.'))

    def list_flags(self, json_output=False):
        """List all feature flags"""
        flags = feature_flags.list_flags()
        
        if json_output:
            self.stdout.write(json.dumps(flags, indent=2, default=str))
            return
        
        self.stdout.write('🚩 Feature Flags Status')
        self.stdout.write('=' * 60)
        
        for flag_name, flag_data in flags.items():
            enabled = flag_data['enabled']
            strategy = flag_data['strategy']
            
            # Status styling
            if enabled:
                status_style = self.style.SUCCESS
                status_text = "ENABLED"
            else:
                status_style = self.style.ERROR
                status_text = "DISABLED"
            
            self.stdout.write(f"\n{flag_name}:")
            self.stdout.write(f"  Status: {status_style(status_text)}")
            self.stdout.write(f"  Strategy: {strategy}")
            self.stdout.write(f"  Description: {flag_data['description']}")
            
            # Strategy-specific details
            if strategy == 'percentage':
                self.stdout.write(f"  Rollout: {flag_data['percentage']}%")
            elif strategy == 'canary':
                self.stdout.write(f"  Canary: {flag_data['canary_percentage']}%")
                if 'canary_metrics' in flag_data:
                    success_rate = flag_data['canary_metrics']['success_rate']
                    self.stdout.write(f"  Success Rate: {success_rate:.1f}%")
            elif strategy == 'shadow':
                self.stdout.write(f"  Shadow: {flag_data['shadow_percentage']}%")

    def show_flag_status(self, flag_name, json_output=False):
        """Show detailed status of specific flag"""
        status = feature_flags.get_flag_status(flag_name)
        
        if not status:
            raise CommandError(f'Feature flag "{flag_name}" not found')
        
        if json_output:
            self.stdout.write(json.dumps(status, indent=2, default=str))
            return
        
        self.stdout.write(f'📊 Feature Flag: {flag_name}')
        self.stdout.write('=' * 50)
        
        enabled = status['enabled']
        status_text = "ENABLED" if enabled else "DISABLED"
        status_style = self.style.SUCCESS if enabled else self.style.ERROR
        
        self.stdout.write(f"Status: {status_style(status_text)}")
        self.stdout.write(f"Strategy: {status['strategy']}")
        self.stdout.write(f"Description: {status['description']}")
        
        if status['strategy'] == 'percentage':
            self.stdout.write(f"Rollout Percentage: {status['percentage']}%")
        elif status['strategy'] == 'canary':
            self.stdout.write(f"Canary Percentage: {status['canary_percentage']}%")
            self.stdout.write(f"Success Threshold: {status['canary_success_threshold']}%")
            if 'canary_metrics' in status:
                success_rate = status['canary_metrics']['success_rate']
                self.stdout.write(f"Current Success Rate: {success_rate:.1f}%")
        elif status['strategy'] == 'user_list':
            self.stdout.write(f"User IDs: {status['user_ids']}")
        elif status['strategy'] == 'shadow':
            self.stdout.write(f"Shadow Percentage: {status['shadow_percentage']}%")

    def enable_flag(self, flag_name):
        """Enable feature flag"""
        if feature_flags.update_flag(flag_name, enabled=True):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Enabled feature flag: {flag_name}')
            )
        else:
            raise CommandError(f'Feature flag "{flag_name}" not found')

    def disable_flag(self, flag_name):
        """Disable feature flag"""
        if feature_flags.update_flag(flag_name, enabled=False):
            self.stdout.write(
                self.style.WARNING(f'⚠️  Disabled feature flag: {flag_name}')
            )
        else:
            raise CommandError(f'Feature flag "{flag_name}" not found')

    def emergency_disable_flag(self, flag_name):
        """Emergency disable feature flag"""
        reason = "Emergency disable via management command"
        
        if feature_flags.emergency_disable(flag_name, reason):
            self.stdout.write(
                self.style.ERROR(f'🚨 EMERGENCY DISABLED: {flag_name}')
            )
            self.stdout.write('This flag has been immediately disabled for all users.')
        else:
            raise CommandError(f'Feature flag "{flag_name}" not found')

    def set_percentage_rollout(self, flag_name, percentage_str):
        """Set percentage rollout for flag"""
        try:
            percentage = float(percentage_str)
            if not 0 <= percentage <= 100:
                raise ValueError("Percentage must be between 0 and 100")
        except ValueError as e:
            raise CommandError(f'Invalid percentage: {e}')
        
        updates = {
            'strategy': RolloutStrategy.PERCENTAGE,
            'percentage': percentage,
            'enabled': True
        }
        
        if feature_flags.update_flag(flag_name, **updates):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Set {flag_name} to {percentage}% rollout')
            )
        else:
            raise CommandError(f'Feature flag "{flag_name}" not found')

    def show_canary_status(self, flag_name, json_output=False):
        """Show canary deployment status"""
        status = feature_flags.get_flag_status(flag_name)
        
        if not status:
            raise CommandError(f'Feature flag "{flag_name}" not found')
        
        if status['strategy'] != 'canary':
            raise CommandError(f'Feature flag "{flag_name}" is not a canary deployment')
        
        canary_data = {
            'flag_name': flag_name,
            'enabled': status['enabled'],
            'canary_percentage': status['canary_percentage'],
            'success_threshold': status['canary_success_threshold'],
            'current_success_rate': status.get('canary_metrics', {}).get('success_rate', 0)
        }
        
        if json_output:
            self.stdout.write(json.dumps(canary_data, indent=2))
            return
        
        self.stdout.write(f'🐤 Canary Deployment: {flag_name}')
        self.stdout.write('=' * 50)
        
        enabled = canary_data['enabled']
        status_text = "ACTIVE" if enabled else "INACTIVE"
        status_style = self.style.SUCCESS if enabled else self.style.ERROR
        
        self.stdout.write(f"Status: {status_style(status_text)}")
        self.stdout.write(f"Canary Users: {canary_data['canary_percentage']}%")
        self.stdout.write(f"Success Threshold: {canary_data['success_threshold']}%")
        self.stdout.write(f"Current Success Rate: {canary_data['current_success_rate']:.1f}%")
        
        # Recommendation
        success_rate = canary_data['current_success_rate']
        threshold = canary_data['success_threshold']
        
        if success_rate >= threshold:
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ Canary is healthy - ready for promotion")
            )
        elif success_rate > 0:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  Canary below threshold - monitor closely")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"\n❌ No canary data - check deployment")
            )

    def promote_canary(self, flag_name):
        """Promote canary to full rollout"""
        status = feature_flags.get_flag_status(flag_name)
        
        if not status:
            raise CommandError(f'Feature flag "{flag_name}" not found')
        
        if status['strategy'] != 'canary':
            raise CommandError(f'Feature flag "{flag_name}" is not a canary deployment')
        
        # Check canary health
        success_rate = status.get('canary_metrics', {}).get('success_rate', 0)
        threshold = status['canary_success_threshold']
        
        if success_rate < threshold:
            self.stdout.write(
                self.style.ERROR(f'❌ Cannot promote canary - success rate {success_rate:.1f}% below threshold {threshold}%')
            )
            return
        
        # Promote to full rollout
        updates = {
            'strategy': RolloutStrategy.ON,
            'enabled': True
        }
        
        if feature_flags.update_flag(flag_name, **updates):
            self.stdout.write(
                self.style.SUCCESS(f'🚀 Promoted canary {flag_name} to full rollout')
            )
            self.stdout.write(f'Success rate: {success_rate:.1f}%')
        else:
            raise CommandError(f'Failed to promote canary "{flag_name}"')
