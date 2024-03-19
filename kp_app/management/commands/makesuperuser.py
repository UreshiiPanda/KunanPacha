from django.contrib.auth import get_user_model  
from django.core.management.base import BaseCommand  

User = get_user_model()  


class Command(BaseCommand):  
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("username", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)


    def handle(self, *args, **options):  

        username = options['username']
        email = options['email']
        new_password = options['password']

        try:  
            u = None  
            if not User.objects.filter(username=username).exists() and not User.objects.filter(  
            is_superuser=True).exists():  
                print("no existing superuser found, creating one")  

                # new_password = get_random_string(10)  

                u = User.objects.create_superuser(username, email, new_password)  
                print(f"===================================")  
                print(f"A superuser '{username}' was created with email '{email}' and password '{new_password}'")  
                print(f"===================================")  
            else:  
                print("superuser found. Skipping superuser creation")  
                print(u)  
        except Exception as e:  
            print(f"There was an error with the makesuperuser file: {e}")

