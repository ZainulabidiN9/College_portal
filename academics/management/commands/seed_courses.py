from django.core.management.base import BaseCommand
from academics.models import course


class Command(BaseCommand):
    help = 'Create sample courses for the portal if no course records exist.'

    def handle(self, *args, **options):
        default_courses = [
            {
                'name': 'Introduction to Programming',
                'code': 'CS101',
                'teacher': 'Mr. Ali Hassan',
                'credits': 3,
                'description': 'Basic programming concepts using Python.',
            },
            {
                'name': 'Database Systems',
                'code': 'CS205',
                'teacher': 'Dr. Sarah Khan',
                'credits': 3,
                'description': 'Relational database design and SQL basics.',
            },
            {
                'name': 'Web Development',
                'code': 'CS310',
                'teacher': 'Ms. Ayesha Raza',
                'credits': 4,
                'description': 'Frontend and backend web application development.',
            },
        ]

        created = 0
        for data in default_courses:
            obj, was_created = course.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name':data['name'],
                    'code':data['code'],
                    'credits':data['credits'],
                    'description':data['description'],
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created course: {obj.name} ({obj.code})'))
            else:
                self.stdout.write(f'Already exists: {obj.name} ({obj.code})')

        self.stdout.write(self.style.SUCCESS(f'Finished. {created} new courses added.'))
