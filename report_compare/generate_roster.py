from faker import Faker
import json
import random
import sys

# Create a Faker instance
fake = Faker()

def create_person():
    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'dob': fake.date_of_birth(minimum_age=22, maximum_age=90).isoformat(),
        'address': fake.address().replace('\n', ', '),
        'SSN': fake.unique.ssn(),
        'credit_utilization': round(random.uniform(0, 1), 2),  # random float between 0 and 1
        'late_payments': random.randint(0, 10),  # random integer between 0 and 10
        'hard_enquiries': random.randint(0, 100),  # random integer between 0 and 100
        'is_deceased': random.choice([True]*10 + [False]*90)  # boolean with 10% chance of being True
    }

num = int(sys.argv[1])
# Generate a consumer roster of X people
people = [create_person() for _ in range(num)]

# Write the data to a JSON file
with open('data/consumer_roster.json', 'w') as f:
    json.dump(people, f)

print(f"Data generated and stored in 'consumer_roster.json' for {num} people")
