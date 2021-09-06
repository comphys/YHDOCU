from system.core.load import Control


class History(Control) : 

    def index(self) :
        return self.echo('Stock history')