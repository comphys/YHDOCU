from system.core.load import Model
import system.core.my_utils as my

class M_config_drawings(Model) :

    def view(self) :
        self.D['save_img_dir'], self.D['save_img_dir2'] = self.DB.oneline("SELECT save_img_dir,save_img_dir2 FROM h_estimate_config WHERE no=1")


