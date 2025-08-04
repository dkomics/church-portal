import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from membership.models import Member


class Command(BaseCommand):
    help = 'Populate the database with dummy member data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of dummy members to create (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample data for generating realistic dummy members
        first_names_male = [
            'John', 'David', 'Michael', 'James', 'Robert', 'William', 'Richard', 
            'Charles', 'Joseph', 'Thomas', 'Daniel', 'Matthew', 'Anthony', 'Mark',
            'Paul', 'Steven', 'Kenneth', 'Joshua', 'Kevin', 'Brian'
        ]
        
        first_names_female = [
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan',
            'Jessica', 'Sarah', 'Karen', 'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra',
            'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores'
        ]
        
        kenyan_names_male = [
            'Mwangi', 'Kamau', 'Kiprotich', 'Otieno', 'Wanjiku', 'Njoroge', 'Kipchoge',
            'Ochieng', 'Mutua', 'Kiptoo', 'Macharia', 'Kimani', 'Wanyama', 'Chelimo'
        ]
        
        kenyan_names_female = [
            'Wanjiru', 'Akinyi', 'Chebet', 'Nyokabi', 'Wairimu', 'Adhiambo', 'Jeptoo',
            'Muthoni', 'Chepkemoi', 'Wambui', 'Awino', 'Jelagat', 'Njeri', 'Chepkoech'
        ]
        
        addresses = [
            'Kileleshwa, Nairobi', 'Westlands, Nairobi', 'Karen, Nairobi', 'Runda, Nairobi',
            'Lavington, Nairobi', 'Kilimani, Nairobi', 'Parklands, Nairobi', 'Muthaiga, Nairobi',
            'Gigiri, Nairobi', 'Spring Valley, Nairobi', 'Riverside, Nairobi', 'Hurlingham, Nairobi',
            'Kiambu Road, Kiambu', 'Thika Road, Kiambu', 'Limuru, Kiambu', 'Ruiru, Kiambu',
            'Arusha Town, Arusha', 'Moshi, Kilimanjaro', 'Usa River, Arusha', 'Tengeru, Arusha'
        ]
        
        churches = [
            'St. Paul\'s Cathedral', 'Grace Baptist Church', 'Pentecostal Church', 
            'Methodist Church', 'Presbyterian Church', 'Catholic Church', 
            'Seventh Day Adventist', 'Anglican Church', 'Evangelical Church',
            'Redeemed Gospel Church', 'Christ the King Church', 'Holy Trinity Church'
        ]
        
        emergency_relations = ['Mke', 'Mume', 'Mama', 'Baba', 'Kaka', 'Dada', 'Mjomba', 'Shangazi']
        
        created_members = []
        
        for i in range(count):
            # Randomly choose gender
            gender = random.choice(['Male', 'Female'])
            
            # Choose appropriate names based on gender
            if gender == 'Male':
                first_name = random.choice(first_names_male + kenyan_names_male)
            else:
                first_name = random.choice(first_names_female + kenyan_names_female)
            
            last_name = random.choice(last_names + kenyan_names_male + kenyan_names_female)
            full_name = f"{first_name} {last_name}"
            
            # Generate random birth date (18-80 years old)
            today = date.today()
            min_age = 18
            max_age = 80
            birth_year = today.year - random.randint(min_age, max_age)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)  # Safe day for all months
            dob = date(birth_year, birth_month, birth_day)
            
            # Generate random phone number (Kenyan format)
            phone_prefixes = ['0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709',
                            '0710', '0711', '0712', '0713', '0714', '0715', '0716', '0717', '0718', '0719',
                            '0720', '0721', '0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729',
                            '0730', '0731', '0732', '0733', '0734', '0735', '0736', '0737', '0738', '0739']
            phone = random.choice(phone_prefixes) + str(random.randint(100000, 999999))
            
            # Generate email
            email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}"
            
            # Random salvation date (1-30 years ago)
            salvation_years_ago = random.randint(1, 30)
            salvation_date = today - timedelta(days=salvation_years_ago * 365 + random.randint(0, 365))
            
            # Random baptism status and date
            baptized = random.choice(['Yes', 'No'])
            baptism_date = None
            if baptized == 'Yes':
                # Baptism date should be after salvation date
                days_after_salvation = random.randint(30, 365 * 5)  # 1 month to 5 years after salvation
                baptism_date = salvation_date + timedelta(days=days_after_salvation)
                if baptism_date > today:
                    baptism_date = today - timedelta(days=random.randint(30, 365))
            
            # Random membership class completion
            membership_class = random.choice(['Completed', 'Not Yet', 'In Progress'])
            
            # Random membership type
            membership_type = random.choice(['New', 'Transfer', 'Returning'])
            
            # Random marital status
            marital_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
            
            # Emergency contact
            emergency_name = f"{random.choice(first_names_male + first_names_female)} {random.choice(last_names)}"
            emergency_phone = random.choice(phone_prefixes) + str(random.randint(100000, 999999))
            emergency_relation = random.choice(emergency_relations)
            
            # Registration date (within last 2 years)
            reg_days_ago = random.randint(1, 730)  # 1 day to 2 years ago
            registration_date = today - timedelta(days=reg_days_ago)
            
            # Create member
            member = Member.objects.create(
                full_name=full_name,
                gender=gender,
                dob=dob,
                marital_status=marital_status,
                phone=phone,
                email=email,
                address=random.choice(addresses),
                salvation_date=salvation_date,
                baptized=baptized,
                baptism_date=baptism_date,
                membership_class=membership_class,
                previous_church=random.choice(churches),
                emergency_name=emergency_name,
                emergency_relation=emergency_relation,
                emergency_phone=emergency_phone,
                membership_type=membership_type,
                registration_date=registration_date
            )
            
            created_members.append(member)
            
            self.stdout.write(
                self.style.SUCCESS(f'Created member: {member.full_name} (ID: {member.membership_id})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {len(created_members)} dummy members!')
        )
        
        # Display summary statistics
        total_members = Member.objects.count()
        male_count = Member.objects.filter(gender='Male').count()
        female_count = Member.objects.filter(gender='Female').count()
        baptized_count = Member.objects.filter(baptized='Yes').count()
        
        self.stdout.write(f'\nDatabase Summary:')
        self.stdout.write(f'Total Members: {total_members}')
        self.stdout.write(f'Male: {male_count}')
        self.stdout.write(f'Female: {female_count}')
        self.stdout.write(f'Baptized: {baptized_count}')
