import random
from fractions import Fraction

class Question:
    def __init__(self):
        self.left_side = 0
        self.right_side = 0
        self.answer = 0
        next(self)
        

    def __next__(self):
        self.populate_multiple_choice()

    def populate_multiple_choice(self):
        self.answer_index = random.randrange(4)
        self.choices = []
        
        for num in range(0,4):
            if num == self.answer_index:
                self.left_side = self.get_fraction()
                self.right_side = self.get_fraction()
                self.answer = self.left_side + self.right_side
                while (
                    any([x == self.answer for x in self.choices]) 
                ):
                    self.left_side = self.get_fraction()
                    self.right_side = self.get_fraction()
                    self.answer = self.left_side + self.right_side
                    
                self.choices.append(
                    self.answer
                )
                
            else:
                choice = self.create_choice()
                while (
                    any([x == choice for x in self.choices]) 
                ):
                    choice = self.create_choice()
                    
                self.choices.append(
                    choice
                )

    def get_fraction(self):
        den = random.randint(2,5)
        num = random.randint(1,3)
        while num % den == 0: num = random.randint(1,4)
        return Fraction(num, den)

    def create_choice(self):
        return Fraction(self.get_fraction() + self.get_fraction())
    
    def is_answer(self, fraction):
        return fraction == self.answer

    def __str__(self):
        return '{left} + {right} = ?'.format(
            left=self.left_side,
            right=self.right_side
        )
