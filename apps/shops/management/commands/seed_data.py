"""
Management command: seed_data
Usage: python manage.py seed_data
Seeds the database with sample data for development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample BeautyMap Congo data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Flush all data before seeding')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            from django.core.management import call_command
            call_command('flush', '--no-input')

        self.stdout.write(self.style.HTTP_INFO('🌱 Seeding BeautyMap Congo data...'))

        self.create_users()
        self.create_shops()
        self.create_reviews()
        self.create_bookings()

        self.stdout.write(self.style.SUCCESS('✅ Data seeded successfully!'))

    def create_users(self):
        self.stdout.write('  Creating users...')

        # Admin
        admin, created = User.objects.get_or_create(
            email='admin@beautymap.cg',
            defaults={
                'first_name': 'Admin', 'last_name': 'BeautyMap',
                'user_type': 'admin', 'is_staff': True, 'is_superuser': True,
                'is_verified': True, 'phone': '+242 06 000 00 00',
            }
        )
        if created:
            admin.set_password('Admin@123!')
            admin.save()
            self.stdout.write(f'    ✓ Admin: admin@beautymap.cg / Admin@123!')

        # Pros
        pros_data = [
            {'email': 'marie.kouba@beautymap.cg', 'first_name': 'Marie', 'last_name': 'Kouba', 'phone': '+242 06 123 45 67'},
            {'email': 'pascal.barber@beautymap.cg', 'first_name': 'Pascal', 'last_name': 'Mboungou', 'phone': '+242 06 234 56 78'},
            {'email': 'joelle.nails@beautymap.cg', 'first_name': 'Joëlle', 'last_name': 'Tamba', 'phone': '+242 05 345 67 89'},
        ]
        self.pros = []
        for pd in pros_data:
            user, created = User.objects.get_or_create(
                email=pd['email'],
                defaults={**pd, 'user_type': 'pro', 'is_verified': True}
            )
            if created:
                user.set_password('Pro@123!')
                user.save()
                from apps.accounts.models import ProProfile
                ProProfile.objects.get_or_create(user=user, defaults={'subscription': 'premium'})
            self.pros.append(user)

        # Clients
        clients_data = [
            {'email': 'amelie.koumba@gmail.com', 'first_name': 'Amélie', 'last_name': 'Koumba', 'phone': '+242 05 456 78 90'},
            {'email': 'sandra.mpanu@gmail.com', 'first_name': 'Sandra', 'last_name': 'Mpanu', 'phone': '+242 06 567 89 01'},
            {'email': 'charlene.bilamba@gmail.com', 'first_name': 'Charlène', 'last_name': 'Bilamba', 'phone': '+242 05 678 90 12'},
            {'email': 'joelle.tamba@gmail.com', 'first_name': 'Joëlle', 'last_name': 'Tamba', 'phone': '+242 06 789 01 23'},
            {'email': 'carole.nguesso@gmail.com', 'first_name': 'Carole', 'last_name': 'Nguesso', 'phone': '+242 05 890 12 34'},
        ]
        self.clients = []
        for cd in clients_data:
            user, created = User.objects.get_or_create(
                email=cd['email'],
                defaults={**cd, 'user_type': 'client', 'is_verified': True}
            )
            if created:
                user.set_password('Client@123!')
                user.save()
                from apps.accounts.models import ClientProfile
                ClientProfile.objects.get_or_create(user=user)
            self.clients.append(user)

        self.stdout.write(f'    ✓ {len(self.pros)} professionals, {len(self.clients)} clients')

    def create_shops(self):
        self.stdout.write('  Creating shops...')
        from apps.shops.models import Shop, Service, Schedule

        shops_data = [
            {
                'owner': self.pros[0], 'name': 'Salon Élégance', 'category': 'coiffure',
                'quartier': 'bacongo', 'phone': '+242 06 123 45 67', 'whatsapp': '+242061234567',
                'latitude': -4.2765, 'longitude': 15.2714,
                'is_verified': True, 'is_featured': True,
                'description': "Spécialiste des tresses africaines, coiffures de mariée et lissages brésiliens depuis 10 ans à Brazzaville. Équipe de 4 coiffeuses certifiées, espace climatisé.",
                'address': 'Avenue des Palmiers, Bacongo',
                'services': [
                    {'name': 'Tresses africaines', 'price': 5000, 'duration_minutes': 180},
                    {'name': 'Lissage brésilien', 'price': 12000, 'duration_minutes': 120},
                    {'name': 'Coupe femme', 'price': 3000, 'duration_minutes': 60},
                    {'name': 'Coloration', 'price': 8000, 'duration_minutes': 90},
                    {'name': 'Coiffure de mariée', 'price': 25000, 'duration_minutes': 240},
                    {'name': 'Tissage', 'price': 9000, 'duration_minutes': 120},
                ],
            },
            {
                'owner': self.pros[1], 'name': 'Barber King', 'category': 'barbier',
                'quartier': 'poto_poto', 'phone': '+242 06 234 56 78', 'whatsapp': '+242062345678',
                'latitude': -4.2614, 'longitude': 15.2850,
                'is_verified': True, 'is_featured': True,
                'description': "Le barbier de référence à Poto-Poto. Coupes modernes, dégradés américains, barbe taillée et soins capillaires pour hommes.",
                'address': 'Rue Bouenza, Poto-Poto',
                'services': [
                    {'name': 'Coupe homme', 'price': 2000, 'duration_minutes': 30},
                    {'name': 'Dégradé', 'price': 3000, 'duration_minutes': 40},
                    {'name': 'Barbe taillée', 'price': 1500, 'duration_minutes': 20},
                    {'name': 'Coupe + Barbe', 'price': 4000, 'duration_minutes': 50},
                ],
            },
            {
                'owner': self.pros[2], 'name': 'Nails Paradise', 'category': 'onglerie',
                'quartier': 'poto_poto', 'phone': '+242 05 345 67 89', 'whatsapp': '+242053456789',
                'latitude': -4.2640, 'longitude': 15.2820,
                'is_verified': False, 'is_featured': False,
                'description': "Onglerie moderne. Poses gel, nail art créatif, semi-permanent longue durée. Techniciennes certifiées.",
                'address': 'Boulevard Denis Sassou Nguesso, Poto-Poto',
                'services': [
                    {'name': 'Pose gel', 'price': 8000, 'duration_minutes': 90},
                    {'name': 'Semi-permanent', 'price': 6000, 'duration_minutes': 60},
                    {'name': 'Nail art', 'price': 12000, 'duration_minutes': 120},
                    {'name': 'Manucure', 'price': 4000, 'duration_minutes': 45},
                    {'name': 'Pédicure', 'price': 5000, 'duration_minutes': 60},
                ],
            },
            {
                'owner': self.pros[0], 'name': 'Beauty & Glow', 'category': 'esthetique',
                'quartier': 'ouenze', 'phone': '+242 06 456 78 90', 'whatsapp': '+242064567890',
                'latitude': -4.2700, 'longitude': 15.2652,
                'is_verified': True, 'is_featured': True,
                'description': "Institut de beauté premium. Soins du visage bio, épilation, massages relaxants, hammam. Produits naturels africains.",
                'address': "Avenue de l'Indépendance, Ouenzé",
                'services': [
                    {'name': 'Soin visage hydratant', 'price': 10000, 'duration_minutes': 60},
                    {'name': 'Épilation jambes', 'price': 6000, 'duration_minutes': 45},
                    {'name': 'Massage relaxant', 'price': 15000, 'duration_minutes': 90},
                    {'name': 'Hammam', 'price': 12000, 'duration_minutes': 75},
                ],
            },
            {
                'owner': self.pros[1], 'name': 'Mode Africa Style', 'category': 'vetements',
                'quartier': 'moungali', 'phone': '+242 05 567 89 01', 'whatsapp': '+242055678901',
                'latitude': -4.2490, 'longitude': 15.2735,
                'is_verified': False, 'is_featured': False,
                'description': "Boutique de mode africaine contemporaine. Pagnes wax, tenues sur mesure, confection rapide.",
                'address': 'Marché de Moungali, Moungali',
                'services': [
                    {'name': 'Pagne wax 3 yards', 'price': 8000, 'duration_minutes': 15},
                    {'name': 'Confection robe', 'price': 25000, 'duration_minutes': 60},
                    {'name': 'Tenue homme', 'price': 15000, 'duration_minutes': 60},
                ],
            },
            {
                'owner': self.pros[2], 'name': 'Teint de Lumière', 'category': 'esthetique',
                'quartier': 'makelekele', 'phone': '+242 05 789 01 23', 'whatsapp': '+242057890123',
                'latitude': -4.2850, 'longitude': 15.2600,
                'is_verified': True, 'is_featured': False,
                'description': "Spécialiste du soin du teint. Traitement anti-taches, peeling doux, soins anti-âge pour peau noire.",
                'address': 'Avenue du Djoué, Makélékélé',
                'services': [
                    {'name': 'Traitement anti-taches', 'price': 18000, 'duration_minutes': 90},
                    {'name': 'Peeling doux', 'price': 12000, 'duration_minutes': 60},
                    {'name': 'Soin hydratant visage', 'price': 7000, 'duration_minutes': 45},
                ],
            },
        ]

        self.shops = []
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        for sd in shops_data:
            services_data = sd.pop('services')
            shop, created = Shop.objects.get_or_create(
                name=sd['name'],
                defaults=sd
            )
            if created:
                # Services
                for i, svc in enumerate(services_data):
                    Service.objects.create(shop=shop, order=i+1, **svc)
                # Schedules
                for i, day in enumerate(days):
                    if i < 5:  # Mon-Fri
                        Schedule.objects.create(shop=shop, day=day, open_time=time(8,0), close_time=time(19,0))
                    elif i == 5:  # Sat
                        Schedule.objects.create(shop=shop, day=day, open_time=time(9,0), close_time=time(17,0))
                    else:  # Sun
                        Schedule.objects.create(shop=shop, day=day, is_closed=True)
                shop.views_count = random.randint(200, 1500)
                shop.save()
            self.shops.append(shop)

        self.stdout.write(f'    ✓ {len(self.shops)} shops with services and schedules')

    def create_reviews(self):
        self.stdout.write('  Creating reviews...')
        from apps.reviews.models import Review

        review_texts = [
            "Service exceptionnel ! Marie est une vraie artiste. Mes tresses ont duré 3 semaines, j'ai eu pleins de compliments. Je reviendrai !",
            "Très bonne coiffeuse, propre et professionnelle. Le seul bémol : un peu d'attente à l'arrivée. Mais le résultat est top !",
            "Ma coloration est parfaite, exactement ce que je voulais. Prix raisonnable pour la qualité. Je reviens la semaine prochaine !",
            "J'ai fait ma coiffure de mariée ici. Absolument magnifique ! Tous mes invités ont été bluffés. Merci infiniment !",
            "Salon propre, équipe accueillante et compétente. Je recommande vivement à toutes les femmes de Brazzaville.",
            "Excellent rapport qualité-prix. Mon dégradé est parfait, le coiffeur a su exactement ce que je voulais. À recommander !",
            "Superbe prestation, l'ambiance est agréable et le personnel souriant. Je suis venue pour une manucure, je suis repartie ravie.",
            "Très professionnel, ponctuel et soigneux. Le soin visage était relaxant et ma peau est rayonnante. Je reviendrai.",
            "Bonne boutique, belle collection de pagnes. La confection est rapide et le rendu est propre. Très satisfaite !",
            "Traitement anti-taches impeccable. Ma peau est beaucoup plus uniforme après 3 séances. Je continue le traitement.",
        ]

        count = 0
        for i, shop in enumerate(self.shops[:4]):
            for j, client in enumerate(self.clients[:3]):
                if random.random() > 0.3:
                    rating = random.choices([3, 4, 5], weights=[1, 3, 6])[0]
                    try:
                        Review.objects.get_or_create(
                            client=client, shop=shop,
                            defaults={
                                'rating': rating,
                                'comment': random.choice(review_texts),
                                'title': f"{'Excellent' if rating == 5 else 'Très bien' if rating == 4 else 'Bien'}",
                                'is_approved': True,
                                'created_at': timezone.now() - timedelta(days=random.randint(1, 60)),
                            }
                        )
                        count += 1
                    except Exception:
                        pass

        self.stdout.write(f'    ✓ {count} reviews')

    def create_bookings(self):
        self.stdout.write('  Creating bookings...')
        from apps.bookings.models import Booking

        statuses = ['confirmed', 'confirmed', 'confirmed', 'pending', 'cancelled', 'completed']
        count = 0
        today = date.today()

        for shop in self.shops[:3]:
            services = list(shop.services.filter(is_active=True)[:3])
            if not services:
                continue
            for client in self.clients:
                if random.random() > 0.4:
                    svc = random.choice(services)
                    booking_date = today + timedelta(days=random.randint(-30, 14))
                    status = random.choice(statuses)
                    try:
                        Booking.objects.create(
                            client=client, shop=shop, service=svc,
                            date=booking_date,
                            start_time=time(random.choice([9, 10, 11, 14, 15, 16]), random.choice([0, 30])),
                            status=status,
                            total_price=svc.price,
                            client_phone=client.phone,
                            notes="Réservation de test" if random.random() > 0.7 else "",
                        )
                        count += 1
                    except Exception:
                        pass

        self.stdout.write(f'    ✓ {count} bookings')
