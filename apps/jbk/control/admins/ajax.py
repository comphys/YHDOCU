from system.core.load import Control

class Ajax(Control) :

    def _auto(self) :
        self.DB = self.db('jbk')
        
    def board_list(self) :
        section = self.D['post']['section']
        target  = self.D['post']['target']
        board_list = self.DB.exe(f"SELECT bid, title FROM h_board_config WHERE section='{section}' ORDER BY bposition", assoc=True)

        data  = "<select class='form-control input-sm' style='background:#ffecef;display:inline;width:150px'"
        data += "onchange=\"selectC(this,'" + target + "')\">\n"
        data += "<option value=''>보드 선택</option>\n"
        if section :
            for val in board_list :
                data += "<option value='" + val['bid'] + "'>" + val['title'] + "</option>\n"
        
        data += "</select>\n"

        return self.echo(data)

    def colorpicker(self) :
        D = {'skin':'admin/colorpicker.html' }
        return self.echo(D)

    def delete_exfields(self) :
        qry = f"UPDATE h_board_config SET {self.D['post']['fid']} = Null WHERE bid='{self.D['post']['bid']}'"
        self.DB.exe(qry)
        return self.echo('Field Deleted')

    def update_exfields(self) :
        P=self.D['post']
        dbset=f"{P['FieldTitle']}/{P['FieldType']}/{P['FieldAlign']}/{P['FieldColor']}/{P['FieldFormat']}/{P['FieldWidth']}/{P['FieldMust']}"
        qry=f"UPDATE h_board_config SET {P['fid']} = '{dbset}' WHERE bid='{P['bid']}'"
        self.DB.exe(qry)
        return self.echo('')

