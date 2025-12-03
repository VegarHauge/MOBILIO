import csv
import os
from decimal import Decimal
from db.session import SessionLocal
from models.product import Product

# Mapping of CSV files to their categories
CSV_FILES = {
    'cleaned_smartwatch.csv': 'Smartwatch',
    'cleaned_phone.csv': 'Phone', 
    'cleaned_headset.csv': 'Headset',
    'cleaned_lader.csv': 'Charger',
    'cleaned_deksel.csv': 'Case'
}

def clean_numeric_value(value_str):
    """Clean and convert numeric values, handling empty strings and None"""
    if not value_str or value_str.strip() == '' or value_str.lower() == 'nan':
        return None
    
    try:
        # Remove any whitespace and convert
        cleaned = str(value_str).strip()
        return float(cleaned) if '.' in cleaned else int(cleaned)
    except (ValueError, TypeError):
        return None

def clean_rating_value(value_str):
    """Clean and convert rating values to Decimal"""
    cleaned = clean_numeric_value(value_str)
    if cleaned is None:
        return None
    
    try:
        return Decimal(str(cleaned))
    except:
        return None

def read_csv_file(file_path):
    """Read CSV file and return list of product dictionaries"""
    products = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Clean and convert data
                product_data = {
                    'name': row.get('name', '').strip(),
                    'price': clean_numeric_value(row.get('price')),
                    'description': row.get('description', '').strip() or None,
                    'brand': row.get('brand', '').strip() or None,
                    'rating': clean_rating_value(row.get('rating')),
                    'ratings': clean_numeric_value(row.get('ratings')),
                    'stock': clean_numeric_value(row.get('stock')),
                    'category': row.get('category', '').strip() or None,
                    'picture': row.get('picture', '').strip() or None
                }
                
                # Only add if we have required fields (name and price)
                if product_data['name'] and product_data['price'] is not None:
                    products.append(product_data)
                else:
                    print(f"Skipping row with missing required data: {row.get('name', 'Unknown')}")
    
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
    
    return products

def seed_products_from_csv():
    """Seed the database with products from all CSV files"""
    db = SessionLocal()
    dataset_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'products')
    
    try:
        print("Starting product seeding from CSV files...")
        print(f"Looking for CSV files in: {os.path.abspath(dataset_path)}")
        
        # Check existing products
        existing_products = db.query(Product).count()
        print(f"Found {existing_products} existing products in database")
        
        total_products_added = 0
        
        # Process each CSV file
        for csv_filename, default_category in CSV_FILES.items():
            file_path = os.path.join(dataset_path, csv_filename)
            
            if not os.path.exists(file_path):
                print(f"Warning: {csv_filename} not found, skipping...")
                continue
            
            print(f"\nProcessing {csv_filename}...")
            products_data = read_csv_file(file_path)
            
            if not products_data:
                print(f"No valid products found in {csv_filename}")
                continue
            
            products_added_from_file = 0
            
            for product_data in products_data:
                try:
                    # Use category from CSV, fallback to default if empty
                    category = product_data['category'] or default_category
                    
                    # Create Product object
                    product = Product(
                        name=product_data['name'],
                        price=float(product_data['price']),
                        description=product_data['description'],
                        brand=product_data['brand'],
                        rating=product_data['rating'],
                        ratings=product_data['ratings'],
                        stock=product_data['stock'] or 0,  # Default to 0 if None
                        category=category,
                        picture=product_data['picture']
                    )
                    
                    db.add(product)
                    products_added_from_file += 1
                    
                except Exception as e:
                    print(f"Error creating product {product_data['name']}: {str(e)}")
                    continue
            
            # Commit products from this file
            try:
                db.commit()
                total_products_added += products_added_from_file
                print(f"Successfully added {products_added_from_file} products from {csv_filename}")
            except Exception as e:
                db.rollback()
                print(f"Error committing products from {csv_filename}: {str(e)}")
        
        print(f"\n✅ Seeding completed!")
        print(f"📊 Total products added: {total_products_added}")
        print(f"📈 Total products in database: {db.query(Product).count()}")
        
        # Show summary by category
        print(f"\n📋 Products by category:")
        categories = db.query(Product.category).distinct().all()
        for (category,) in categories:
            count = db.query(Product).filter(Product.category == category).count()
            print(f"   {category}: {count} products")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error occurred during seeding: {str(e)}")
        raise
    finally:
        db.close()

def clear_all_products():
    """Clear all existing products from database (use with caution!)"""
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count > 0:
            response = input(f"Are you sure you want to delete all {count} products? (yes/no): ").strip().lower()
            if response == 'yes':
                db.query(Product).delete()
                db.commit()
                print(f"✅ Deleted {count} products")
            else:
                print("❌ Deletion cancelled")
        else:
            print("No products to delete")
    except Exception as e:
        db.rollback()
        print(f"Error clearing products: {str(e)}")
    finally:
        db.close()

def main():
    """Main function to run the product seeding"""
    try:
        seed_products_from_csv()
    except Exception as e:
        print(f"Failed to seed products: {str(e)}")

if __name__ == "__main__":
    main()