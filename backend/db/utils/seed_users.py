import random
from db.session import SessionLocal
from models.user import User
from services.auth_service import AuthService

# Lists of names for random generation
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher",
    "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
    "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan",
    "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Benjamin", "Samuel", "Gregory", "Alexander", "Patrick", "Frank", "Raymond", "Jack", "Dennis", "Jerry",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Lisa", "Nancy", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle",
    "Laura", "Sarah", "Kimberly", "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen",
    "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Sarah", "Kimberly", "Deborah",
    "Amy", "Angela", "Ashley", "Brenda", "Emma", "Olivia", "Cynthia", "Marie", "Janet", "Catherine"
]

MIDDLE_NAMES = [
    "Lee", "Ann", "Marie", "Rose", "Grace", "Joy", "Faith", "Hope", "Sue", "Lynn",
    "Jean", "Jane", "Beth", "May", "Ray", "Jay", "Dean", "Gene", "Dale", "Wayne",
    "Roy", "Earl", "Carl", "Paul", "Alan", "Glen", "Hugh", "Neil", "Rex", "Guy",
    "Lou", "Max", "Sam", "Tom", "Dan", "Jon", "Ben", "Ted", "Joe", "Bob",
    "Jim", "Tim", "Ken", "Ron", "Don", "Art", "Ed", "Hal", "Cal", "Mel"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez"
]

def generate_random_name():
    """Generate a random full name using first, middle, and last names"""
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {middle} {last}"

def seed_users(num_users=1000):
    """Seed the database with the specified number of users"""
    db = SessionLocal()
    try:
        print(f"Starting to seed {num_users} users...")
        
        # Check if users already exist to avoid duplicates
        existing_users = db.query(User).count()
        print(f"Found {existing_users} existing users in database")
        
        users_created = 0
        
        for i in range(1, num_users + 1):
            # Generate random name
            full_name = generate_random_name()
            
            # Create email: firstname.lastname.counter@mail.com
            name_parts = full_name.split()
            first_name = name_parts[0].lower()
            last_name = name_parts[-1].lower()  # Use last name (skip middle name)
            email = f"{first_name}.{last_name}.{i}@mail.com"
            
            # Check if email already exists (just in case)
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"User with email {email} already exists, skipping...")
                continue
            
            # Hash the password using the same method as in auth service
            hashed_password = AuthService.get_password_hash("password")
            
            # Create user
            user = User(
                name=full_name,
                email=email,
                password=hashed_password,
                role="customer",  # All users will be customers
                sort_option="price_asc"  # Default sort option
            )
            
            db.add(user)
            users_created += 1
            
            # Commit every 100 users to avoid memory issues
            if i % 100 == 0:
                db.commit()
                print(f"Created {i} users so far...")
        
        # Final commit
        db.commit()
        print(f"Successfully created {users_created} new users!")
        print(f"Total users in database: {db.query(User).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred while seeding users: {str(e)}")
        raise
    finally:
        db.close()

def main():
    """Main function to run the seeding script"""
    try:
        seed_users(1000)
    except Exception as e:
        print(f"Failed to seed users: {str(e)}")

if __name__ == "__main__":
    main()