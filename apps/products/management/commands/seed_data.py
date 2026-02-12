import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from products.models import Category, Product
from stores.models import Store, Inventory

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        
        with transaction.atomic():
            # Create 10+ categories
            categories = []
            for i in range(12):
                cat, _ = Category.objects.get_or_create(name=fake.unique.word().capitalize())
                categories.append(cat)
            
            self.stdout.write(f"Created {len(categories)} categories.")

            # Create 1000+ products
            products = []
            for i in range(1050):
                prod = Product.objects.create(
                    title=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=200),
                    price=random.uniform(10.0, 1000.0),
                    category=random.choice(categories)
                )
                products.append(prod)
            
            self.stdout.write(f"Created {len(products)} products.")

            # Create 20+ stores
            stores = []
            for i in range(25):
                store = Store.objects.create(
                    name=fake.company(),
                    location=fake.address()
                )
                stores.append(store)
            
            self.stdout.write(f"Created {len(stores)} stores.")

            # Create Inventory for each store with at least 300 products
            for store in stores:
                selected_products = random.sample(products, random.randint(300, 500))
                inventory_items = []
                for prod in selected_products:
                    inventory_items.append(Inventory(
                        store=store,
                        product=prod,
                        quantity=random.randint(0, 100)
                    ))
                Inventory.objects.bulk_create(inventory_items)
            
            self.stdout.write(f"Seeded inventory for {len(stores)} stores.")

        self.stdout.write(self.style.SUCCESS("Successfully seeded dummy data!"))
