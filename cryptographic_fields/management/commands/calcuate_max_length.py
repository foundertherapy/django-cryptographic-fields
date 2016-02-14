from django.core.management.base import BaseCommand

from cryptographic_fields.fields import calc_encrypted_length


class Command(BaseCommand):
    help = ('Given a max_length for a field, returns the max length '
            'required to store encrypted result')

    def add_arguments(self, parser):
        parser.add_argument('length', nargs=1, type=int)

    def handle(self, *args, **options):
        self.stdout.write(str(calc_encrypted_length(options['length'][0])))
