from django.db import models

# Create your models here.
class Demographics(models.Model):
    # gender that user identifies as
    male    = models.FloatField(default=.1)
    female  = models.FloatField(default=.1)
    other   = models.FloatField(default=.1)
    
    # age group user belongs to
    y0_12   = models.FloatField(default=.1)
    y13_17  = models.FloatField(default=.1)
    y18_21  = models.FloatField(default=.1)
    y22_25  = models.FloatField(default=.1)
    y26_30  = models.FloatField(default=.1)
    y31_35  = models.FloatField(default=.1)
    y36_45  = models.FloatField(default=.1)
    y46_55  = models.FloatField(default=.1)
    y56_65  = models.FloatField(default=.1)
    y65plus = models.FloatField(default=.1)
    
    # interests
    dance   = models.FloatField(default=.1)
    comedy  = models.FloatField(default=.1)
    trends  = models.FloatField(default=.1)
    singing = models.FloatField(default=.1)
    
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