from tkinter import *
from tkinter import messagebox
import time
from datetime import datetime

bgColor = "#24272D"
root = Tk()
root.geometry("250x230")
root.title("J Counter")
root.config(bg=bgColor)
root.resizable(False,False)

heading = Label(root,text="Counter",font="arial 20 bold",fg="#ea3548",bg=bgColor)
heading.pack(pady=5)
#clock
Label(root,font=("arial",15,"bold"),text="현재 시각 :",fg="#fff",bg=bgColor).place(x=20,y=50)
Label(root,font=("arial",15,"bold"),text="설정 시각 :",fg="#fff",bg=bgColor).place(x=20,y=80)
Label(root,font=("arial",15,"bold"),text="남은 시간 :",fg="#fff",bg=bgColor).place(x=20,y=110)

current_time=Label(root,font=("arial",15,"bold"),text="",fg="yellow",bg=bgColor); current_time.place(x=140,y=50)

setTime = "22:37:53"
set_time=Label(root,font=("arial",15,"bold"),text="",fg="white",bg=bgColor);set_time.place(x=140,y=80);set_time.config(text=setTime)
cnt_time=Label(root,font=("arial",15,"bold"),text="",fg="gray",bg=bgColor); cnt_time.place(x=140,y=110);cnt_time.config(text='00:00:00')

def clock() :
    clock_time=time.strftime("%H:%M:%S")
    current_time.config(text=clock_time)
    current_time.after(1000,clock)

clock()

def Timer():
    time_1 = datetime.strptime(time.strftime("%H:%M:%S"),"%H:%M:%S")
    time_2 = datetime.strptime(setTime,"%H:%M:%S")

    time_interval = str(time_2 - time_1)
    hh,mm,ss = time_interval.split(":")
    try : hh = int(hh)
    except : messagebox.showerror(message="시간 설정 오류입니다")

    temp = int(hh)*3600 + int(mm)*60 + int(ss)

    while temp > -1:
        mins,secs = divmod(temp,60)
        hours=0
        if mins > 60: hours, mins = divmod(mins, 60)

        counter = f"{hours:02d}:{mins:02d}:{secs:02d}"
        cnt_time.config(text=counter)

        root.update()
        time.sleep(1)

        if (temp == 0): 
            root.destroy()
            root.quit()
        temp -= 1

button=Button(root,text="Start",bg="#DC504B",bd=0,fg="#fff",width=10,height=1,font="arial 10 bold",command=Timer)
button.place(x=30,y=170)

button=Button(root,text="Stop",bg="#006BCC",bd=0,fg="#fff",width=10,height=1,font="arial 10 bold",command=Timer)
button.place(x=140,y=170)

root.mainloop()