# Python importss
import logging
from transliterate import translit
import re

# Django imports
from django.core.management import BaseCommand

# import models
from posts.models.post import Post

log = logging.getLogger(__name__)


class Command(BaseCommand):
    ''' Django command '''
    help = "Add translitarate prefix to URL"

    def handle(self, *args, **options):
        ''' get posts titles, translitarate them all '''
        posts = Post.objects.filter(type='post').all()
        # for test on prod
        output_file_path = 'transliterated_slugs.txt'
        with open(output_file_path, 'w', encoding='utf-8') as output_file:

            for post in posts:
                
                try:
                    post_title = post.title
                    post_title = translit(post_title, 'ru', reversed=True)
                    post_title = post_title.strip()
                    # remove all except letters, numbers and spaces
                    post_title = re.sub("[^A-Za-z\d\s]", "", post_title)
                    post_slug = post.slug + f"-{post_title}"
                    self.stdout.write(post_slug)
                    post_slug = post_slug.replace(" ", "-").replace("--", "-")
                    while post_slug[-1] == '-':
                        post_slug = post_slug[:-1]

#                    post.slug = post_slug
#                    post.save()
                    output_file.write(f'{post_slug}\n')
#                    self.stdout.write(post_slug)

                except Exception as ex:

                    self.stdout.write("Транслитерация не "\
                                    f"получилась. Post ID:{post.id}. Ошибка: {ex}")
                    log.error("Транслитерация не получилась. "\
                            f"Post ID:{post.id}. Ошибка: {ex}")
