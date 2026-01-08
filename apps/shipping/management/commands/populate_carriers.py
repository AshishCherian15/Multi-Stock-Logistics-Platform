from django.core.management.base import BaseCommand
from shipping.models import Carrier, ShippingRate

class Command(BaseCommand):
    help = 'Populate sample carriers and shipping rates'

    def handle(self, *args, **kwargs):
        carriers_data = [
            {'name': 'FedEx', 'code': 'FEDEX', 'tracking_url': 'https://www.fedex.com/fedextrack/?tracknumbers=', 'contact_phone': '1800-123-4567', 'contact_email': 'support@fedex.com'},
            {'name': 'DHL Express', 'code': 'DHL', 'tracking_url': 'https://www.dhl.com/in-en/home/tracking.html?tracking-id=', 'contact_phone': '1800-111-3456', 'contact_email': 'support@dhl.com'},
            {'name': 'Blue Dart', 'code': 'BLUEDART', 'tracking_url': 'https://www.bluedart.com/tracking', 'contact_phone': '1860-233-1234', 'contact_email': 'care@bluedart.com'},
            {'name': 'DTDC', 'code': 'DTDC', 'tracking_url': 'https://www.dtdc.in/tracking.asp', 'contact_phone': '1860-208-3838', 'contact_email': 'support@dtdc.com'},
            {'name': 'India Post', 'code': 'INDIAPOST', 'tracking_url': 'https://www.indiapost.gov.in/_layouts/15/dop.portal.tracking/trackconsignment.aspx', 'contact_phone': '1800-11-2011', 'contact_email': 'care@indiapost.gov.in'},
        ]
        
        for data in carriers_data:
            carrier, created = Carrier.objects.get_or_create(code=data['code'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created carrier: {carrier.name}'))
                
                # Add sample rates
                rates = [
                    {'service_type': 'Standard', 'min_weight': 0, 'max_weight': 5, 'base_rate': 50, 'per_kg_rate': 10, 'estimated_days': 5},
                    {'service_type': 'Express', 'min_weight': 0, 'max_weight': 5, 'base_rate': 100, 'per_kg_rate': 20, 'estimated_days': 2},
                    {'service_type': 'Standard', 'min_weight': 5, 'max_weight': 20, 'base_rate': 100, 'per_kg_rate': 15, 'estimated_days': 5},
                    {'service_type': 'Express', 'min_weight': 5, 'max_weight': 20, 'base_rate': 200, 'per_kg_rate': 25, 'estimated_days': 2},
                ]
                
                for rate_data in rates:
                    ShippingRate.objects.create(carrier=carrier, **rate_data)
                
                self.stdout.write(self.style.SUCCESS(f'Added {len(rates)} rates for {carrier.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully populated carriers and rates!'))
