#from lib.instascrapper import Instascrapper
from lib.imgur import Imgur

class Huachiapi:

    description = "description"
    default_msg = "Holis aún estoy bajo construcción!"

    def __init__(self):
        pass

    # saldazo method
    def saldazo(self, *args):
        return f"{self.default_msg}"

    # shop method
    def shop(self, *args):
        if args[0] == 'frase_piolinera':
            return
            #i = Instascrapper("https://www.instagram.com/explore/tags/frasesdeldia/")
            #reponse = i.get_photo()
            #if reponse:
            #    return response
            #else:
            #    return f"{self.default_msg}"
        elif args[0] == 'piolin':
            return Imgur().get_image("piolin")
        else:
            return f"{self.default_msg}"

    # TTip method
    def tip(self, *args):
        return f"<:huachi:809238593696432200>"
