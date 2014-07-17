import random

def get_fridge_language(language):
    if (language == "EN"):
        return EnglishFridgeLanguage()

class FridgeLanguage:

    def _init_(self):
        random.seed()        
        
    def get_random_letter(self):
        value = random.random() * 100
        total = 0
        for letter_frequency in self.distribution:
            letter = letter_frequency[1]
            total += letter_frequency[0]
            if (value < total):
                 break
                    
        return letter

class EnglishFridgeLanguage(FridgeLanguage):
    distribution = [
        [ 13.0001 , 'E'],
        [ 9.056 , 'T'],
        [ 8.167 , 'A'],
        [ 7.507 , 'O'],
        [ 6.966 , 'I'],
        [ 6.749 , 'N'],
        [ 6.327 , 'S'],
        [ 6.094 , 'H'],
        [ 5.987 , 'R'],
        [ 4.253 , 'D'],
        [ 4.025 , 'L'],
        [ 2.782 , 'C'],
        [ 2.758 , 'U'],
        [ 2.406 , 'M'],
        [ 2.360 , 'W'],
        [ 2.228 , 'F'],
        [ 2.015 , 'G'],
        [ 1.974 , 'Y'],
        [ 1.929 , 'P'],
        [ 1.492 , 'B'],
        [ 0.978 , 'V'],
        [ 0.772 , 'K'],
        [ 0.153 , 'J'],
        [ 0.150 , 'X'],
        [ 0.095 , 'Q'],
        [ 0.074 , 'Z']
    ]
