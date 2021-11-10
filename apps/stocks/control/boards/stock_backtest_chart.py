from system.core.load import Control
import matplotlib.pyplot as plt
import os.path

class Stock_backtest_chart(Control) : 
    
    def show_chart(self) :
        cls_v = self.gets['cls_val'].split('-')[:-2]
        avg_v = self.gets['avg_val'].split('-')[:-2]
        code  = self.gets['code']
        season= self.gets['season']
        stra=self.gets['stra']
        start=self.gets['start']

        file_name = f"{self.C['DOCU_ROOT']}/개인자료/주식투자/백테스트/{code}_{stra}_{season}_{start}.png" 

        if not os.path.isfile(file_name) : 
            c_price = [float(x) for x in cls_v]
            m_price = [float(x) for x in avg_v]
            my_dpi = 100
            xx = list(range(0,60))
            xl = [x+1 for x in xx]
            plt.figure(facecolor='#24272d')
            plt.figure(figsize=(1400/my_dpi, 300/my_dpi),dpi=my_dpi)
            # plt.rcParams["figure.figsize"] = (20,4)
            plt.rcParams.update({"figure.figsize":(20,4),"axes.grid" : True, "grid.color": "#24272d",'font.size':8})
            ax = plt.axes()
            ax.set_facecolor('#33363b')

            ax.tick_params(color='#33363b',grid_alpha=0.7)
            plt.plot(c_price,color='#58ACFA',  linestyle='dotted')
            plt.plot(m_price,color='#f78181',  linestyle='solid',marker='o')
            plt.xticks(xx,xl,color='darkgray')
            plt.yticks(color='darkgray')
            plt.savefig(file_name,facecolor='#24272d',dpi=my_dpi,pad_inches=0)

        output  = "<div style='width:100%;height:300px;background-color:#1d1f24;color:#e1e1e1;' ondblclick=\"h_dialog.close('ST_CHART')\">"
        output += f"<img src='/DOCU_ROOT/개인자료/주식투자/백테스트/{code}_{stra}_{season}_{start}.png' style='border:1px solid black'>"
        output += "</div>"
        return output


