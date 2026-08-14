from system.core.load import Control

class Check(Control) : 


    def _auto(self) :
        self.DB = self.db('stocks')

    def get(self) :

        token = self.DB.store('kiwoom_token')
        self.D['post']['token'] = token
        return self.D['post']

    def rsn_check(self):

        self.DB.parameter_update('TX070',self.D['post']['date'])
        return self.D['post']['date']
