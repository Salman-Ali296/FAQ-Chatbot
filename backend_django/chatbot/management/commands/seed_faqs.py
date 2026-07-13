import json
import os

from django.core.management.base import BaseCommand

from chatbot.models import FAQ

DEFAULT_SEED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "seed_data", "faqs.json"
)


class Command(BaseCommand):
    help = "Load FAQ question/answer pairs from a JSON file into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=DEFAULT_SEED_PATH,
            help="Path to a JSON file of {question, answer, category?} objects.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing FAQs before seeding.",
        )

    def handle(self, *args, **options):
        file_path = os.path.abspath(options["file"])

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Seed file not found: {file_path}"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if options["clear"]:
            deleted_count, _ = FAQ.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted_count} existing FAQ rows."))

        created = 0
        for entry in data:
            _, was_created = FAQ.objects.get_or_create(
                question=entry["question"],
                defaults={
                    "answer": entry["answer"],
                    "category": entry.get("category", "General"),
                },
            )
            if was_created:
                created += 1

        from chatbot.nlp_matcher import invalidate_matcher_cache
        invalidate_matcher_cache()

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new FAQ(s). Total in DB: {FAQ.objects.count()}"))
