from system.core.load import Model

class M_config_outsourcing(Model) :

    def view(self) :
        co_list = self.DB.one("SELECT out_co_list FROM h_estimate_config WHERE no=1")
        self.D['out_co_list'] = co_list
        


