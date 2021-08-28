from system.core.load import Control


class Editor(Control) : 

  
    def _auto(self) :

        self.D['bid'] = self.gets['bid']
        self.dialog_skin = 'board/'+self.DB.one(f"SELECT skin FROM h_board_config WHERE bid = '{self.D['bid']}'")+'/dialog/'


    def dialog(self) :
        D={}
        tool = self.gets['dialog']
        D['skin'] = self.dialog_skin + tool + '.html'
        return self.echo(D)

