#!/usr/bin/env python3
"""
Initialize marketplace data - categories and sample dengue prevention products
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ProductCategory, Product
from datetime import datetime

def init_marketplace_data():
    """Initialize marketplace with categories and sample products"""
    with app.app_context():
        try:
            print("🏪 Initializing Dengue Prevention Marketplace...")
            
            # Create categories
            categories_data = [
                {
                    'name': 'Mosquito Repellents',
                    'description': 'Sprays, creams, coils and electronic repellents to keep mosquitoes away',
                    'icon': 'fas fa-spray-can'
                },
                {
                    'name': 'Bed Nets & Covers', 
                    'description': 'Treated bed nets, window screens and protective covers',
                    'icon': 'fas fa-bed'
                },
                {
                    'name': 'Testing Kits',
                    'description': 'Rapid dengue testing kits for early detection',
                    'icon': 'fas fa-vial'
                },
                {
                    'name': 'Protective Clothing',
                    'description': 'Long-sleeve clothing and treated garments for protection',
                    'icon': 'fas fa-tshirt'
                },
                {
                    'name': 'Water Storage',
                    'description': 'Covered containers and larvicide tablets for water storage',
                    'icon': 'fas fa-tint'
                },
                {
                    'name': 'Health Supplements',
                    'description': 'Immunity boosters and recovery supplements',
                    'icon': 'fas fa-pills'
                }
            ]
            
            print("📂 Creating product categories...")
            for cat_data in categories_data:
                category = ProductCategory.query.filter_by(name=cat_data['name']).first()
                if not category:
                    category = ProductCategory(**cat_data)
                    db.session.add(category)
            
            db.session.commit()
            print(f"✅ Created {len(categories_data)} categories")
            
            # Get category IDs for products
            categories = {cat.name: cat.id for cat in ProductCategory.query.all()}
            
            # Create sample products
            products_data = [
                # Mosquito Repellents
                {
                    'name': 'Odomos Mosquito Repellent Cream',
                    'description': 'Long-lasting protection against mosquitoes for up to 12 hours. Clinically proven effective against Aedes aegypti mosquitoes that carry dengue.',
                    'short_description': 'Clinically proven 12-hour protection against dengue mosquitoes',
                    'price': 125.0,
                    'discounted_price': 99.0,
                    'category_id': categories['Mosquito Repellents'],
                    'image_url': '/static/images/products/odomos-cream.jpg',
                    'stock_quantity': 150,
                    'is_featured': True,
                    'effectiveness_rating': 4.5,
                    'usage_instructions': 'Apply evenly on exposed skin. Reapply after 12 hours or after sweating/bathing.',
                    'ingredients': 'N,N-Diethyl-meta-toluamide (DEET) 20%',
                    'safety_notes': 'For external use only. Avoid contact with eyes. Not recommended for children under 2 years.'
                },
                {
                    'name': 'Good knight Power Activ+ Mosquito Spray',
                    'description': 'Instant protection spray that kills mosquitoes on contact. Effective for indoor and outdoor use.',
                    'short_description': 'Instant kill mosquito spray for immediate protection',
                    'price': 180.0,
                    'discounted_price': 159.0,
                    'category_id': categories['Mosquito Repellents'],
                    'stock_quantity': 200,
                    'effectiveness_rating': 4.2,
                    'usage_instructions': 'Spray in the air or on surfaces where mosquitoes rest. Use in well-ventilated areas.',
                    'safety_notes': 'Keep away from flames. Use only in ventilated areas. Keep out of reach of children.'
                },
                {
                    'name': 'Mortein Insta5 Electric Mosquito Repellent',
                    'description': 'Electronic liquid vaporizer that provides continuous protection for up to 45 nights.',
                    'short_description': 'Electric liquid repellent for 45 nights continuous protection',
                    'price': 299.0,
                    'category_id': categories['Mosquito Repellents'],
                    'stock_quantity': 100,
                    'is_featured': True,
                    'effectiveness_rating': 4.7,
                    'usage_instructions': 'Plugin to power socket. One refill lasts 45 nights when used 8 hours daily.',
                    'safety_notes': 'Keep away from children. Ensure proper ventilation during use.'
                },
                
                # Bed Nets & Covers
                {
                    'name': 'WHO Approved Long Lasting Insecticidal Net (LLIN)',
                    'description': 'Permethrin-treated bed net that provides protection for 3-5 years. Recommended by WHO for dengue prevention.',
                    'short_description': 'WHO approved treated bed net with 3-5 year effectiveness',
                    'price': 450.0,
                    'discounted_price': 399.0,
                    'category_id': categories['Bed Nets & Covers'],
                    'stock_quantity': 75,
                    'is_featured': True,
                    'effectiveness_rating': 4.9,
                    'usage_instructions': 'Hang above bed ensuring complete coverage. Do not wash for first 6 months.',
                    'ingredients': 'Permethrin-treated polyester mesh',
                    'safety_notes': 'Safe for daily use. Wash only when necessary with mild soap.'
                },
                {
                    'name': 'Window Mesh Screen Set',
                    'description': 'Fine mesh screens for windows and doors to prevent mosquito entry while allowing air circulation.',
                    'short_description': 'Window and door mesh screens to block mosquito entry',
                    'price': 899.0,
                    'discounted_price': 749.0,
                    'category_id': categories['Bed Nets & Covers'],
                    'stock_quantity': 50,
                    'effectiveness_rating': 4.6,
                    'usage_instructions': 'Install on all windows and doors. Ensure no gaps for mosquito entry.',
                    'safety_notes': 'Check regularly for tears and repair immediately.'
                },
                
                # Testing Kits
                {
                    'name': 'SD Bioline Dengue Rapid Test Kit',
                    'description': 'WHO approved rapid diagnostic test for dengue fever. Results in 15-20 minutes.',
                    'short_description': 'WHO approved rapid dengue test with 15-minute results',
                    'price': 899.0,
                    'discounted_price': 799.0,
                    'category_id': categories['Testing Kits'],
                    'stock_quantity': 30,
                    'is_featured': True,
                    'effectiveness_rating': 4.8,
                    'usage_instructions': 'For healthcare professional use. Follow kit instructions carefully.',
                    'safety_notes': 'For diagnostic use only. Consult healthcare provider for interpretation.'
                },
                
                # Protective Clothing
                {
                    'name': 'Anti-Mosquito Long Sleeve Shirt',
                    'description': 'Permethrin-treated full sleeve shirt that repels mosquitoes while remaining comfortable.',
                    'short_description': 'Treated long-sleeve shirt with built-in mosquito protection',
                    'price': 1299.0,
                    'discounted_price': 999.0,
                    'category_id': categories['Protective Clothing'],
                    'stock_quantity': 40,
                    'effectiveness_rating': 4.3,
                    'usage_instructions': 'Wash with regular detergent. Treatment lasts 70+ washes.',
                    'safety_notes': 'Safe for daily wear. Effectiveness decreases with frequent washing.'
                },
                
                # Water Storage
                {
                    'name': 'Dengue Prevention Water Tank Cover',
                    'description': 'Heavy-duty cover for water tanks to prevent mosquito breeding in stored water.',
                    'short_description': 'Tank cover to prevent mosquito breeding in stored water',
                    'price': 599.0,
                    'discounted_price': 499.0,
                    'category_id': categories['Water Storage'],
                    'stock_quantity': 60,
                    'effectiveness_rating': 4.4,
                    'usage_instructions': 'Cover all water storage containers completely. Check weekly for damage.',
                    'safety_notes': 'Ensure proper fit to prevent gaps where mosquitoes can enter.'
                },
                {
                    'name': 'Larvicide Tablets (BTI)',
                    'description': 'Biological larvicide tablets safe for drinking water that prevent mosquito larvae development.',
                    'short_description': 'Safe larvicide tablets for drinking water storage',
                    'price': 299.0,
                    'category_id': categories['Water Storage'],
                    'stock_quantity': 100,
                    'effectiveness_rating': 4.6,
                    'usage_instructions': 'Add 1 tablet per 100 liters of stored water. Effective for 30 days.',
                    'ingredients': 'Bacillus thuringiensis israelensis (BTI)',
                    'safety_notes': 'Safe for drinking water. WHO approved biological control agent.'
                },
                
                # Health Supplements
                {
                    'name': 'Papaya Leaf Extract Capsules',
                    'description': 'Natural extract known to boost platelet count. Helpful during dengue recovery.',
                    'short_description': 'Natural papaya leaf extract to support platelet count',
                    'price': 399.0,
                    'discounted_price': 349.0,
                    'category_id': categories['Health Supplements'],
                    'stock_quantity': 80,
                    'effectiveness_rating': 4.1,
                    'usage_instructions': 'Take 1-2 capsules daily with water after meals. Consult doctor during illness.',
                    'safety_notes': 'Consult healthcare provider before use, especially during active dengue infection.'
                },
                {
                    'name': 'Immunity Booster Vitamin C + Zinc',
                    'description': 'High-strength vitamin C and zinc supplement to boost immune system against viral infections.',
                    'short_description': 'Vitamin C + Zinc for immune system support',
                    'price': 249.0,
                    'category_id': categories['Health Supplements'],
                    'stock_quantity': 120,
                    'effectiveness_rating': 4.0,
                    'usage_instructions': 'Take 1 tablet daily with water. Best taken with meals.',
                    'safety_notes': 'Do not exceed recommended dosage. Consult doctor if pregnant or nursing.'
                }
            ]
            
            print("🛍️ Creating sample products...")
            created_count = 0
            for prod_data in products_data:
                product = Product.query.filter_by(name=prod_data['name']).first()
                if not product:
                    product = Product(**prod_data)
                    db.session.add(product)
                    created_count += 1
            
            db.session.commit()
            print(f"✅ Created {created_count} new products")
            
            # Print summary
            total_products = Product.query.count()
            total_categories = ProductCategory.query.count()
            
            print(f"\n🎉 Marketplace initialization complete!")
            print(f"📊 Summary:")
            print(f"   • {total_categories} product categories")
            print(f"   • {total_products} total products")
            print(f"   • Featured products: {Product.query.filter_by(is_featured=True).count()}")
            print(f"\n🌐 Access marketplace at: http://localhost:5000/marketplace")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing marketplace: {e}")
            raise

if __name__ == '__main__':
    init_marketplace_data()