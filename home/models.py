from django.db import models

class Asset(models.Model):
    OPTIONS = [
        ('Buy','Buy'),
        ('Sell','Sell')
    ]
    symbol = models.CharField(max_length=200)
    amount = models.IntegerField()
    operation = models.CharField(max_length=4, choices=OPTIONS,default='')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __repr__(self) -> str:
        return f'The asset {self.symbol} was added to DB ({self.created_date})'