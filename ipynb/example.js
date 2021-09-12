function process_book( sel, rno, fac_fname, pay_method ) {
	if( pay_method == '현장카드' || pay_method == '현장현금' ) { h_dialog.alert("현장 결제는 처리하지 않습니다."); return; }
	selected_tr = $(sel).parent();
	$(selected_tr).css("backgroundColor","#5a5a5a");
	var url = uri('linkurl') + 'board-editor/dialog/bid='+uri(0)+'/dialog=process_book/rno='+ rno+'/fac_fname='+fac_fname;
	var o =	{id:'process_book',width:'1545px',x:20,y: mouse_Y + 12, header:false,overlay:true,over_opacity:0.1,drag:false,maxHeight:'200px',
			 buttons:   [
						 {text : '닫기', call: function(a) { $(selected_tr).css("backgroundColor",''); h_dialog.close(a); }},
						]			 
			};
	h_dialog.load(url,o);
}