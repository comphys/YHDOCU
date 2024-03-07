from myutils.DB import DB
import myutils.my_utils as my

class test001 :

    def __init__(self) :
        self.D = {}
        self.DB = DB('stocks')


    def doit(self) :


        sd = dict(self.DB.exe("SELECT add0,CAST(add17 as float) FROM h_S231226_board ORDER BY add0"))
        rd = dict(self.DB.exe("SELECT add0,CAST(add17 as float) FROM h_R230831_board ORDER BY add0"))
        vd = dict(self.DB.exe("SELECT add0,CAST(add17 as float) FROM h_V230831_board ORDER BY add0"))

        bs = 0.0
        br = 0.0

        sd['2023-12-29'] = 6997.28
        rd['2023-08-30'] = 45063.0



        NV = {}
        

        for key, val in vd.items() :
            NV[key] = val
            if key in rd : NV[key] += rd[key]; br = rd[key]
            else : rd[key]=0.0;   NV[key] += br

            if key in sd : NV[key] += sd[key]; bs = sd[key]
            else : sd[key]=0.0;   NV[key] += bs

            print(key,val,rd[key],sd[key],NV[key])
 






AA = test001()
AA.doit()