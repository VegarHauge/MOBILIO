import random
import string
from datetime import datetime, timedelta
from typing import List
from db.session import SessionLocal
from models.user import User
from models.product import Product
from models.order import Order
from models.orderitem import OrderItem

# User behavior profiles for realistic recommendation training data
USER_PROFILES = {
    'tech_enthusiast': {
        'weight': 0.15,  # 15% of users
        'order_frequency': (2, 8),  # 2-8 orders
        'avg_order_value': (2000, 15000),  # High-value orders
        'preferred_categories': ['Mobiltelefon', 'Smartklokke', 'Smartwatch'],
        'brand_loyalty': 0.7,  # 70% chance to stick with preferred brands
        'preferred_brands': ['Apple', 'Samsung', 'Garmin'],
        'item_per_order': (1, 3)
    },
    'budget_conscious': {
        'weight': 0.25,  # 25% of users
        'order_frequency': (1, 4),
        'avg_order_value': (100, 1000),  # Lower-value orders
        'preferred_categories': ['Case', 'Charger', 'Lader'],
        'brand_loyalty': 0.3,  # Less brand loyal
        'preferred_brands': [],  # No strong preference
        'item_per_order': (1, 2)
    },
    'brand_loyalist': {
        'weight': 0.20,  # 20% of users
        'order_frequency': (2, 6),
        'avg_order_value': (1000, 8000),
        'preferred_categories': [],  # No category preference
        'brand_loyalty': 0.9,  # Very brand loyal
        'preferred_brands': ['Apple', 'Samsung'],  # Will be assigned one
        'item_per_order': (1, 4)
    },
    'frequent_buyer': {
        'weight': 0.10,  # 10% of users
        'order_frequency': (5, 12),  # Many small orders
        'avg_order_value': (200, 2000),
        'preferred_categories': [],
        'brand_loyalty': 0.4,
        'preferred_brands': [],
        'item_per_order': (1, 2)
    },
    'casual_buyer': {
        'weight': 0.30,  # 30% of users - largest group
        'order_frequency': (1, 3),
        'avg_order_value': (500, 3000),
        'preferred_categories': [],
        'brand_loyalty': 0.5,
        'preferred_brands': [],
        'item_per_order': (1, 3)
    }
}

# Product affinity rules - products often bought together
PRODUCT_AFFINITIES = {
    'Mobiltelefon': {
        'Case': 0.8,        # 80% chance to also buy a case
        'Lader': 0.6,       # 60% chance to also buy a charger
        'Headset': 0.4      # 40% chance to also buy headset
    },
    'Smartwatch': {
        'Lader': 0.7        # 70% chance to buy charger with smartwatch
    },
    'Smartklokke': {
        'Lader': 0.7
    }
}

# Brand consistency rules
BRAND_CONSISTENCY = {
    'Apple': ['Apple'],
    'Samsung': ['Samsung', 'Samsung'],  # Higher weight for Samsung
    'Garmin': ['Garmin'],
    'Huawei': ['Huawei']
}

def generate_stripe_session_id():
    """Generate a random stripe session ID for seeded orders"""
    # Generate something that looks like a Stripe session ID: cs_test_[random string]
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return f"cs_test_{random_part}"

class OrderSeeder:
    def __init__(self):
        self.db = SessionLocal()
        self.users = []
        self.products_by_category = {}
        self.products_by_brand = {}
        self.user_profiles = {}  # Will store assigned profiles for each user
    
    def load_data(self):
        """Load users and products from database"""
        print("Loading users and products...")
        
        # Load all users
        self.users = self.db.query(User).filter(User.role == 'customer').all()
        if not self.users:
            raise Exception("No customer users found! Please seed users first.")
        
        # Load and categorize products
        products = self.db.query(Product).all()
        if not products:
            raise Exception("No products found! Please seed products first.")
        
        # Group products by category
        for product in products:
            category = product.category
            if category not in self.products_by_category:
                self.products_by_category[category] = []
            self.products_by_category[category].append(product)
        
        # Group products by brand
        for product in products:
            brand = product.brand
            if brand and brand not in self.products_by_brand:
                self.products_by_brand[brand] = []
            if brand:
                self.products_by_brand[brand].append(product)
        
        print(f"Loaded {len(self.users)} users and {len(products)} products")
        print(f"Categories: {list(self.products_by_category.keys())}")
        print(f"Brands: {list(self.products_by_brand.keys())}")
    
    def assign_user_profiles(self):
        """Assign behavior profiles to users"""
        print("Assigning user behavior profiles...")
        
        profile_names = list(USER_PROFILES.keys())
        profile_weights = [USER_PROFILES[p]['weight'] for p in profile_names]
        
        for user in self.users:
            # Randomly assign profile based on weights
            profile_name = random.choices(profile_names, weights=profile_weights)[0]
            profile = USER_PROFILES[profile_name].copy()
            
            # For brand loyalists, assign a specific brand
            if profile_name == 'brand_loyalist' and self.products_by_brand:
                available_brands = [b for b in ['Apple', 'Samsung', 'Garmin'] if b in self.products_by_brand]
                if available_brands:
                    profile['preferred_brands'] = [random.choice(available_brands)]
            
            self.user_profiles[user.id] = {
                'profile_name': profile_name,
                **profile
            }
        
        # Print profile distribution
        profile_counts = {}
        for user_profile in self.user_profiles.values():
            name = user_profile['profile_name']
            profile_counts[name] = profile_counts.get(name, 0) + 1
        
        print("Profile distribution:")
        for name, count in profile_counts.items():
            percentage = (count / len(self.users)) * 100
            print(f"  {name}: {count} users ({percentage:.1f}%)")
    
    def get_products_for_user(self, user_id: int) -> List[Product]:
        """Get products that match user's profile preferences"""
        profile = self.user_profiles[user_id]
        available_products = []
        
        # Filter by preferred categories
        if profile['preferred_categories']:
            for category in profile['preferred_categories']:
                if category in self.products_by_category:
                    available_products.extend(self.products_by_category[category])
        else:
            # If no category preference, use all products
            for products in self.products_by_category.values():
                available_products.extend(products)
        
        # Apply brand preference
        if profile['preferred_brands'] and random.random() < profile['brand_loyalty']:
            brand_products = []
            for brand in profile['preferred_brands']:
                if brand in self.products_by_brand:
                    brand_products.extend([p for p in self.products_by_brand[brand] if p in available_products])
            
            if brand_products:
                available_products = brand_products
        
        return available_products
    
    def create_realistic_order(self, user: User, order_date: datetime) -> Order:
        """Create a realistic order for a user based on their profile"""
        profile = self.user_profiles[user.id]
        
        # Get suitable products for this user
        available_products = self.get_products_for_user(user.id)
        if not available_products:
            return None
        
        # Determine number of items in this order
        min_items, max_items = profile['item_per_order']
        num_items = random.randint(min_items, max_items)
        
        # Create order
        order = Order(
            customer_id=user.id,
            total_amount=0.0,  # Will be calculated
            created_at=order_date,
            stripe_session_id=generate_stripe_session_id()
        )
        
        order_items = []
        total_amount = 0.0
        selected_products = []
        
        # Select first product
        primary_product = random.choice(available_products)
        quantity = random.randint(1, 2)  # Usually 1-2 of each item
        
        order_item = OrderItem(
            product_id=primary_product.id,
            quantity=quantity,
            total_amount=float(primary_product.price * quantity)
        )
        order_items.append(order_item)
        total_amount += order_item.total_amount
        selected_products.append(primary_product)
        
        # Add complementary products based on affinity rules
        for i in range(num_items - 1):
            next_product = self.get_complementary_product(selected_products, available_products, profile)
            if next_product:
                quantity = random.randint(1, 2)
                order_item = OrderItem(
                    product_id=next_product.id,
                    quantity=quantity,
                    total_amount=float(next_product.price * quantity)
                )
                order_items.append(order_item)
                total_amount += order_item.total_amount
                selected_products.append(next_product)
        
        # Check if total is within user's budget range
        min_budget, max_budget = profile['avg_order_value']
        if total_amount < min_budget * 0.5 or total_amount > max_budget * 2:
            # If way outside budget, try again with different products
            return None
        
        order.total_amount = total_amount
        
        # Save order and items
        self.db.add(order)
        self.db.flush()  # Get order ID
        
        for order_item in order_items:
            order_item.order_id = order.id
            self.db.add(order_item)
        
        return order
    
    def get_complementary_product(self, existing_products: List[Product], 
                                available_products: List[Product], 
                                profile: dict) -> Product:
        """Get a product that complements existing products in the order"""
        
        # Check affinity rules
        for existing_product in existing_products:
            if existing_product.category in PRODUCT_AFFINITIES:
                affinities = PRODUCT_AFFINITIES[existing_product.category]
                
                for target_category, probability in affinities.items():
                    if random.random() < probability:
                        # Look for products in the target category
                        candidates = [p for p in available_products 
                                    if p.category == target_category 
                                    and p not in existing_products]
                        
                        if candidates:
                            # Apply brand consistency if relevant
                            if (existing_product.brand and 
                                existing_product.brand in BRAND_CONSISTENCY and
                                random.random() < profile['brand_loyalty']):
                                
                                brand_candidates = [p for p in candidates 
                                                  if p.brand == existing_product.brand]
                                if brand_candidates:
                                    return random.choice(brand_candidates)
                            
                            return random.choice(candidates)
        
        # If no affinity match, return random product not already selected
        remaining_products = [p for p in available_products if p not in existing_products]
        return random.choice(remaining_products) if remaining_products else None
    
    def generate_order_dates(self, user: User, num_orders: int) -> List[datetime]:
        """Generate realistic order dates for a user"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Last year
        
        dates = []
        current_date = start_date
        
        for i in range(num_orders):
            # Add some randomness to spacing
            days_to_add = random.randint(10, 90)  # 10-90 days between orders
            current_date += timedelta(days=days_to_add)
            
            if current_date > end_date:
                break
                
            dates.append(current_date)
        
        return dates[:num_orders]
    
    def seed_orders(self, max_orders_per_user: int = None):
        """Generate realistic orders for all users"""
        print("Generating realistic orders...")
        
        total_orders_created = 0
        total_revenue = 0.0
        
        for user in self.users:
            profile = self.user_profiles[user.id]
            
            # Determine number of orders for this user
            min_orders, max_orders = profile['order_frequency']
            if max_orders_per_user:
                max_orders = min(max_orders, max_orders_per_user)
            
            num_orders = random.randint(min_orders, max_orders)
            order_dates = self.generate_order_dates(user, num_orders)
            
            user_orders_created = 0
            
            for order_date in order_dates:
                try:
                    order = self.create_realistic_order(user, order_date)
                    if order:
                        user_orders_created += 1
                        total_orders_created += 1
                        total_revenue += order.total_amount
                        
                        if total_orders_created % 100 == 0:
                            self.db.commit()
                            print(f"Created {total_orders_created} orders so far...")
                
                except Exception as e:
                    print(f"Error creating order for user {user.id}: {str(e)}")
                    continue
            
            if user_orders_created > 0 and total_orders_created % 50 == 0:
                print(f"User {user.name} ({profile['profile_name']}): {user_orders_created} orders")
        
        # Final commit
        self.db.commit()
        
        print("\n✅ Order seeding completed!")
        print(f"📊 Total orders created: {total_orders_created}")
        print(f"💰 Total revenue: {total_revenue:,.2f} NOK")
        print(f"📈 Average order value: {total_revenue/total_orders_created:,.2f} NOK")
        
        # Show statistics by profile
        self.show_statistics()
    
    def show_statistics(self):
        """Show order statistics by user profile"""
        profile_stats = {}
        
        for user in self.users:
            profile_name = self.user_profiles[user.id]['profile_name']
            if profile_name not in profile_stats:
                profile_stats[profile_name] = {'orders': 0, 'revenue': 0.0, 'users': 0}
            
            user_orders = self.db.query(Order).filter(Order.customer_id == user.id).all()
            profile_stats[profile_name]['orders'] += len(user_orders)
            profile_stats[profile_name]['revenue'] += sum(o.total_amount for o in user_orders)
            profile_stats[profile_name]['users'] += 1
        
        print("\n📈 Statistics by user profile:")
        for profile_name, stats in profile_stats.items():
            avg_orders = stats['orders'] / stats['users'] if stats['users'] > 0 else 0
            avg_revenue = stats['revenue'] / stats['orders'] if stats['orders'] > 0 else 0
            print(f"  {profile_name}:")
            print(f"    Users: {stats['users']}")
            print(f"    Total orders: {stats['orders']}")
            print(f"    Avg orders per user: {avg_orders:.1f}")
            print(f"    Avg order value: {avg_revenue:,.2f} NOK")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def seed_realistic_orders(max_orders_per_user: int = None):
    """Main function to seed orders with realistic patterns"""
    seeder = OrderSeeder()
    
    try:
        seeder.load_data()
        seeder.assign_user_profiles()
        seeder.seed_orders(max_orders_per_user)
        
    except Exception as e:
        seeder.db.rollback()
        print(f"❌ Error during order seeding: {str(e)}")
        raise
    finally:
        seeder.close()

def main():
    """Main function"""
    try:
        seed_realistic_orders()
    except Exception as e:
        print(f"Failed to seed orders: {str(e)}")

if __name__ == "__main__":
    main()