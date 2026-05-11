from django.db import models

######################################################################################
######################################################################################

class FAQ(models.Model) :
    FAQ_id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=500)

    def __str__(self):
        return self.question
    
######################################################################################
######################################################################################

    