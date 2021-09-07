from flask import session

class YHCATEGORY :

    def __init__(self,SYS) :

        self.SYS = SYS
        self.D = SYS.D
        self.info = SYS.info
        self.order = 65
        self.con = []
    
    def make_select(self,CATEGORY,exFIDktitle) :
        data = [] ;  Opt  = [] ; fkey = [] ; 

        item_key = CATEGORY.split('/')
        item_cnt = len(item_key)

        for val in item_key :
            fkey.append(val)
            self.con.append(self.jsearch_word(val))
        
        if item_cnt >= 1 :
            data.append(self.jsearch_item_print(exFIDktitle[item_key[0]],fkey[0],''))
        
        option = ''
        for ic in range(2,6) :
            if item_cnt >= ic :
                ic1 = ic-1
                ic2 = ic-2
                if self.con[ic2] :
                    Opt.append(f" {fkey[ic2]} = '{self.con[ic2]}'")
                    option = ' and '.join(Opt)
 
                data.append(self.jsearch_item_print(exFIDktitle[item_key[ic1]],fkey[ic1],option))
        return data
    
    def jsearch_item_print(self,title,fkey,wre='') :
        bid = self.D['bid']
        cats = {}
        lili = []

        is_field = self.jsearch_word(fkey)
        if is_field :
            cats['chked'] = True
            cats['value'] = is_field
        else :
            cats['chked'] = False
            cats['value'] = ''
        
        cats['id'] = 'sh_'+ chr(self.order)
        cats['fkey'] = fkey

        qry = f"SELECT distinct {fkey} FROM h_{bid}_board WHERE brother <=0 "
        if wre : qry += ' and '+ wre
        qry += "ORDER BY "+fkey

        category = self.SYS.DB.exe(qry)
        cats['title'] = title

        if category : 
            for val in category :
                lili.append(val)
        
        cats['lists'] = lili
        self.order += 1

        return cats
    
    def jsearch_word(self,field_name) :
        if session['CSH'] : return session['CSH'].get('csh_'+field_name,None) 
        else : return None