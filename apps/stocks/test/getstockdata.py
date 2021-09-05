import FinanceDataReader as fdr

code='TQQQ'

df = fdr.DataReader(symbol=code, start='2018')

df.to_excel("D:/stocks/"+code+".xlsx", sheet_name=code)

print(code +" OK")
