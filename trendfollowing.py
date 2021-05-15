import pandas
import pandas_datareader
import fix_yahoo_finance as yfinance
import matplotlib
import matplotlib.pyplot
import numpy
global data

yfinance.pdr_override()
matplotlib.pyplot.style.use('seaborn-whitegrid')

def get_data():
    data=pandas_datareader.data.get_data_yahoo(tickers='BOVA11.SA',start='2020-01-01',period='ytd',index_col=0,parse_dates=True)[['Close']]
    data=pandas.DataFrame(data)
    return data


def Simples(x,window):
    return x.rolling(window=window).mean()

def Exponencial(x,window):
    return x.ewm(span=window,adjust=False).mean()

def Linear(x,window):
    weights= numpy.arange(1,window+1)
    return x.rolling(window=window).apply(lambda x: numpy.dot(x,weights)/sum(weights))

func_map = {'Simples': Simples, 'Exponencial': Exponencial , 'Linear': Linear}


class Models:
    def __init__(self,model,mean):
        self.model = model
        self.mean = mean

   
    def strategy(self, **kwargs):
        SMA1=  kwargs.get('SMA1')
        SMA3 = kwargs.get('SMA3')
        SMA2 = kwargs.get('SMA2')
        if self.model is 'TripleCrossOver':
            if self.mean in func_map.keys():
                data['SMA1']=func_map[self.mean](data['Close'],SMA1)
                data['SMA2']=func_map[self.mean](data['Close'],SMA2)
                data['SMA3']=func_map[self.mean](data['Close'],SMA3)
                data.dropna(inplace=True)

                data['alert']=numpy.where((data['SMA1']>data['SMA2']) & (data['SMA1']>data['SMA3']),1,-1)
                data['Position']=numpy.where((data['SMA1']>data['SMA2']) & (data['SMA2']>data['SMA3']),1,-1)

        if self.model is 'DoubleCrossOver':
            if self.mean in func_map.keys():
                data['SMA1']=func_map[self.mean](data['Close'],SMA1)
                data['SMA2']=func_map[self.mean](data['Close'],SMA2)


                data.dropna(inplace=True)
                
                data['Position']= numpy.where(data['SMA1']> data['SMA2'],1,-1)

        if self.model is 'SingleAverage':
            if self.mean in func_map.keys():
                data['SMA1']= func_map[self.mean](data['Close'],SMA1)
                data.dropna(inplace=True)
                data['Position'] = numpy.where(data['SMA1']>data['Close'],1,-1)
            
    
        data['Returns']=numpy.log(data['Close']/data['Close'].shift(1))
        data['Strategy']= data['Position'].shift(1) * data['Returns']
        if self.model is 'TripleCrossOver':
            data['AlertStrat']= data['alert'].shift(1)* data['Returns']


        data.dropna(inplace=True)
        return

    def stats(self):
        RETURN = data[['Returns','Strategy']].sum().apply(numpy.exp) 
        data['CumReturn'] = data['Returns'].cumsum().apply(numpy.exp)
        data['CumReturnMax'] = data['CumReturn'].cummax()
        drawdown =  data['CumReturnMax'] - data['CumReturn']
        temp = drawdown[drawdown==0]
        ddperiods = temp.index[1:].to_pydatetime()-temp.index[:-1].to_pydatetime()
        data['Win rate'] =data['Strategy'].groupby((data['Position'].shift() != data['Position']).cumsum()).cumsum()
        Trade = data['Win rate'].groupby((data['Position'].shift()!=data['Position']).cumsum()).last().round(5)
        PD =data['Win rate'].groupby((data['Position'].shift()!=data['Position']).cumsum()).apply(len)

        return print('----------------------STATS------------------' , '\n'
        'Num. Trades', len(Trade) , '\n'  'Win Rate [%]' , sum(Trade > 0 ) / len(Trade),
        '\n' 'Best Trade [%]' , Trade.max() , '\n' 'Worst Trade [%]', Trade.min() ,
        '\n' 'Avg. Trade [%]' , round(Trade.mean(),5) , '\n' 'Max. Position Duration' , PD.max() , 
        '\n' 'Avg. Position Duration' , PD.mean(), '\n' 'Max Drawdown [%]' ,drawdown.max(), 
        '\n' 'Avg. Drawdown [%]', drawdown.mean(), '\n' 'Max. Drawdown Duration', ddperiods.max(), 
        '\n' 'Avg. Drawdown Duration' , ddperiods.mean(),'\n',RETURN)

    def graph(self):
            if self.model is 'SingleAverage':
                data[['Close','SMA1','Position']].plot(secondary_y=['Position'],style=['-','r','g--'])
            if self.model is 'TripleCrossOver':
                data[['Close','Position', 'SMA1', 'SMA2','SMA3']].plot(secondary_y=['Position'],style=['-','r', 'g--', 'b--'])
            if self.model is 'DoubleCrossOver':
                data[['Close','Position', 'SMA1', 'SMA2']].plot(secondary_y=['Position'],style=['-','r', 'g--', 'b--'])
            return matplotlib.pyplot.show()

# MODELO:
# data=get_data()
# x=Models('SingleAverage ou DoubleCrossOver ou TripleCrossOver', 'Simples ou Exponencial ou Linear')
# x.strategy(SMA1=a,e SMA2=b em caso de DoubleCrossOver, e SMA3=c em caso de TripleCrossOver)
# x.stats()
# x.graph()