from django.db import models

# Create your models here.
class Demographics(models.Model):
    # gender that user identifies as
    male    = models.IntegerField(default=10)
    female  = models.IntegerField(default=10)
    other   = models.IntegerField(default=10)
    
    # age group user belongs to
    y0_12   = models.IntegerField(default=10)
    y13_17  = models.IntegerField(default=10)
    y18_21  = models.IntegerField(default=10)
    y22_25  = models.IntegerField(default=10)
    y26_30  = models.IntegerField(default=10)
    y31_35  = models.IntegerField(default=10)
    y36_45  = models.IntegerField(default=10)
    y46_55  = models.IntegerField(default=10)
    y56_65  = models.IntegerField(default=10)
    y65plus = models.IntegerField(default=10)
    
    # interests
    dance   = models.IntegerField(default=10)
    comedy  = models.IntegerField(default=10)
    trends  = models.IntegerField(default=10)
    singing = models.IntegerField(default=10)
    
    def get_int_list(self):
        return [
            self.male    ,
            self.female  ,
            self.other   ,

            self.y0_12   ,
            self.y13_17  ,
            self.y18_21  ,
            self.y22_25  ,
            self.y26_30  ,
            self.y31_35  ,
            self.y36_45  ,
            self.y46_55  ,
            self.y56_65  ,
            self.y65plus ,
            
            self.dance   ,
            self.comedy  ,
            self.trends  ,
            self.singing ,
        ]
    
    def set_int_list(self, intList):
        self.male    = int(intList[0])
        self.female  = int(intList[1])
        self.other   = int(intList[2])
        
        self.y0_12   = int(intList[3])
        self.y13_17  = int(intList[4])
        self.y18_21  = int(intList[5])
        self.y22_25  = int(intList[6])
        self.y26_30  = int(intList[7])
        self.y31_35  = int(intList[8])
        self.y36_45  = int(intList[9])
        self.y46_55  = int(intList[10])
        self.y56_65  = int(intList[11])
        self.y65plus = int(intList[12])
        
        self.dance   = int(intList[13])
        self.comedy  = int(intList[14])
        self.trends  = int(intList[15])
        self.singing = int(intList[16])