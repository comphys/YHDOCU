from system.core.load import Control
import system.core.my_utils as my

class Rest(Control) : 


    def _auto(self) :
        self.DB = self.db('stocks')

    def check(self) :
        return self.echo("Hellow")
  

 
 
    