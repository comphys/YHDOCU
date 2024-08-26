from system.core.load import Control

class Rst_control(Control) :

    def index(self) :
        self.DB = self.db('stocks')
        RST = self.load_lib('rst')
        aa = RST.get_date_serial('2019-08-24','2024-08-23')
        aa.reverse()
        HTML = '<table>'
        for a in aa :

            RST.get_start(a,'2024-08-26')
            RST.init_value()

            RST.simulate()
            RST.result()

            HTML += f"<tr><td>{a}</td><td style='text-align:right'>{RST.D['R_최종수익']}</td><td style='text-align:right'>{RST.D['R_종수익률']}</td>"
            HTML += f"<td style='color:blue'>{RST.D['최대날자']}</td><td style='text-align:right;color:blue'>{RST.D['최대일수']:.2f}</td>"
            HTML += f"<td style='font-weight:bold'>{RST.D['저점날자']}</td><td style='text-align:right;color:red'>{RST.D['손익저점']:.2f}</td></tr>"
        HTML += "</table>"

        return self.echo(HTML)

