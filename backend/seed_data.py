import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from models import UserCreate, BookCreate
from database import create_user, create_book
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_database():
    """Seed the database with demo data."""
    print("🌱 Starting database seeding...")
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Clear existing data (for demo purposes)
        await db.users.delete_many({})
        await db.books.delete_many({})
        await db.loans.delete_many({})
        await db.reservations.delete_many({})
        print("🗑️  Cleared existing data")
        
        # Create users
        users_data = [
            {
                "username": "admin",
                "email": "admin@ecole.fr",
                "password": "admin123",
                "full_name": "Administrateur Système",
                "role": "admin"
            },
            {
                "username": "bibliothecaire",
                "email": "bibliothecaire@ecole.fr", 
                "password": "biblio123",
                "full_name": "Marie Dubois",
                "role": "librarian"
            },
            {
                "username": "prof_martin",
                "email": "martin@ecole.fr",
                "password": "prof123",
                "full_name": "Jean Martin",
                "role": "teacher",
                "class_name": "CM2-A"
            },
            {
                "username": "eleve_sophie",
                "email": "sophie@ecole.fr",
                "password": "eleve123",
                "full_name": "Sophie Durand",
                "role": "student",
                "class_name": "CM2-A"
            },
            {
                "username": "eleve_pierre",
                "email": "pierre@ecole.fr",
                "password": "eleve123",
                "full_name": "Pierre Moreau",
                "role": "student",
                "class_name": "CM1-B"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            try:
                user = await create_user(UserCreate(**user_data))
                created_users.append(user)
                print(f"✅ Utilisateur créé: {user.username} ({user.role})")
            except Exception as e:
                print(f"❌ Erreur création utilisateur {user_data['username']}: {e}")
        
        # Create books
        books_data = [
            {
                "title": "Le Petit Prince",
                "authors": ["Antoine de Saint-Exupéry"],
                "isbn": "978-2-07-040850-7",
                "publisher": "Gallimard",
                "year": 1943,
                "description": "L'histoire d'un petit prince qui voyage de planète en planète.",
                "categories": ["Fiction", "Jeunesse", "Classique"],
                "location": "Rayon A - Étage 1",
                "tags": ["aventure", "philosophie", "enfance"],
                "total_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400"
            },
            {
                "title": "Harry Potter à l'école des sorciers",
                "authors": ["J.K. Rowling"],
                "isbn": "978-2-07-054120-8",
                "publisher": "Gallimard Jeunesse",
                "year": 1997,
                "description": "Un jeune garçon découvre qu'il est un sorcier le jour de ses 11 ans.",
                "categories": ["Fantasy", "Jeunesse", "Aventure"],
                "location": "Rayon B - Étage 1",
                "tags": ["magie", "école", "amitié"],
                "total_copies": 5,
                "cover_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
            },
            {
                "title": "Les Misérables",
                "authors": ["Victor Hugo"],
                "isbn": "978-2-07-040987-0",
                "publisher": "Gallimard",
                "year": 1862,
                "description": "Roman historique et social français du XIXe siècle.",
                "categories": ["Classique", "Histoire", "Roman"],
                "location": "Rayon C - Étage 2",
                "tags": ["histoire", "social", "France"],
                "total_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400"
            },
            {
                "title": "Le Tour du monde en 80 jours",
                "authors": ["Jules Verne"],
                "isbn": "978-2-07-040123-2",
                "publisher": "Gallimard",
                "year": 1873,
                "description": "Les aventures de Phileas Fogg dans son pari fou.",
                "categories": ["Aventure", "Classique", "Voyage"],
                "location": "Rayon A - Étage 2",
                "tags": ["voyage", "aventure", "pari"],
                "total_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=400"
            },
            {
                "title": "L'Étranger",
                "authors": ["Albert Camus"],
                "isbn": "978-2-07-040004-4",
                "publisher": "Gallimard",
                "year": 1942,
                "description": "Roman existentialiste sur l'absurdité de la condition humaine.",
                "categories": ["Philosophie", "Littérature", "Classique"],
                "location": "Rayon D - Étage 2",
                "tags": ["existentialisme", "philosophie", "absurde"],
                "total_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400"
            },
            {
                "title": "Charlotte's Web",
                "authors": ["E.B. White"],
                "isbn": "978-0-06-440055-6",
                "publisher": "Harper & Brothers",
                "year": 1952,
                "description": "L'amitié entre une petite fille, un cochon et une araignée.",
                "categories": ["Jeunesse", "Amitié", "Animaux"],
                "location": "Rayon B - Étage 1",
                "tags": ["animaux", "amitié", "ferme"],
                "total_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400"
            },
            {
                "title": "Le Journal d'Anne Frank",
                "authors": ["Anne Frank"],
                "isbn": "978-2-253-00395-1",
                "publisher": "Le Livre de Poche",
                "year": 1947,
                "description": "Le témoignage poignant d'une adolescente pendant la Seconde Guerre mondiale.",
                "categories": ["Histoire", "Biographie", "Témoignage"],
                "location": "Rayon C - Étage 1",
                "tags": ["guerre", "holocauste", "témoignage"],
                "total_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1471017432530-1be22d4c23d1?w=400"
            },
            {
                "title": "1984",
                "authors": ["George Orwell"],
                "isbn": "978-2-07-036822-5",
                "publisher": "Gallimard",
                "year": 1949,
                "description": "Une dystopie sur la surveillance et le totalitarisme.",
                "categories": ["Science-Fiction", "Dystopie", "Politique"],
                "location": "Rayon D - Étage 1",
                "tags": ["dystopie", "surveillance", "liberté"],
                "total_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400"
            }
        ]
        
        created_books = []
        for book_data in books_data:
            try:
                book = await create_book(BookCreate(**book_data))
                created_books.append(book)
                print(f"📚 Livre créé: {book.title} ({book.total_copies} exemplaires)")
            except Exception as e:
                print(f"❌ Erreur création livre {book_data['title']}: {e}")
        
        print(f"\n🎉 Seeding terminé!")
        print(f"👥 {len(created_users)} utilisateurs créés")
        print(f"📖 {len(created_books)} livres créés")
        print("\n🔑 Comptes de test:")
        print("   Admin: admin / admin123")
        print("   Bibliothécaire: bibliothecaire / biblio123")
        print("   Professeur: prof_martin / prof123")
        print("   Élève: eleve_sophie / eleve123")
        print("   Élève: eleve_pierre / eleve123")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())