from pywikibot import family

class Family(family.Family):
        name = 'fantasylife'
        langs = {
                'en': 'fantasy-life.fandom.com'
        }

        def scriptpath(self, code):
                return ''

        def protocol(self, code):
                return 'HTTPS'
