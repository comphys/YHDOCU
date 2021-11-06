from system.core.load import Control
import matplotlib.pyplot as plt

class Stock_backtest_chart(Control) : 
    
    def show_chart(self) :
        cls_v = (self.D['post']['cls_val'].split('/'))[:-2]
        avg_v = (self.D['post']['avg_val'].split('/'))[:-2]

        c_price = [float(x) for x in cls_v]
        m_price = [float(x) for x in avg_v]
        xx = list(range(0,len(c_price)))
        xl = [x+1 for x in xx]

        plt.plot(c_price,color='#58ACFA',  linestyle='dotted')
        plt.plot(m_price,color='#f78181',  linestyle='solid',marker='o')
        plt.xticks(xx,xl)
        plt.grid(True)

        plt.show(block=True)
        return None

