import tkinter as tk
import fitz
from PIL import Image,ImageTk
from tkinter import messagebox as msg
import os
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import sh

# version and compilation date of PyMuPDF
fitz_ver = fitz.__doc__
print(fitz_ver)

if not list(map(int, fitz.VersionBind.split("."))) >= [1, 16, 18]:
    raise SystemExit("need PyMuPDF v1.16.18 for this script")

class PDF_Reader():
    def __init__(self):
        self.main=tk.Tk()
        self.main.title('文献管理')
        self.main.geometry('600x600')
        self.main.grid_rowconfigure(2,weight=1)
        self.main.grid_columnconfigure(2,weight=1)
        self.pdf_files=[]
        self.current_pdf_file=''
        self.pages=0
        self.current_page=0
        self.pix_width=0
        self.pix_height=0
        self.zoom_x=2
        self.zoom_y=2
        self.shear_x=0
        self.shear_y=0
        self.rotate=0

    def pdf(self,doc,page):
        pdf_page=doc[page]
        mat=fitz.Matrix(self.rotate)
        mat.preRotate(self.rotate)
        mat.preScale(self.zoom_x,self.zoom_y)
        mat.preShear(self.shear_x,self.shear_y)
        pix=pdf_page.getPixmap(matrix=mat)
        mode='RGBA' if pix.alpha else 'RGB'
        self.pix_width=pix.width
        self.pix_height=pix.height
        img=Image.frombytes(mode,[self.pix_width,self.pix_height],pix.samples)
        pdf_img=ImageTk.PhotoImage(img)
        return pdf_img
        
    def ui(self):
        #--------------------------------------菜单命令函数
            #--------------------菜单函数
        def menu_open():
            filename=filedialog.askopenfilename(filetypes=[('PDF','.pdf')])
            if filename!='':
                self.pdf_files.append(filename)
            self.current_pdf_file=self.pdf_files[-1]
            self.run()
            self.main.update()
            
        def menu_save():
            filename=filedialog.askopenfilename(filetypes=[('PDF','.pdf')])
            name=os.path.basename(filename)
            if os.path.exists(filename):
                msg.showinfo('Attention!','the file'+name+'exists!')
            else:
                self.doc.save(fielname=filename)
                msg.showinfo('Saved','the file'+name+'has saved!')

        def command(i):
            if self.pdf_files:
                self.current_file=self.pdf_files[i]
            else:
                pass
        
            #--------------------页码选择
        def nextpage():
            lo=pdf_yscrollbar.get()[0]-1/self.pages
            self.pdf_canvas.yview_moveto(lo)

        def lastpage():
            lo=pdf_yscrollbar.get()[0]+1/self.pages
            self.pdf_canvas.yview_moveto(lo)
            
        def page(page):
            if page>0 and page<self.pages:
                lo=page/self.pages
                self.pdf_canvas.yview_moveto(lo)
            else:
                raise IndexError

        def page_go():
            page(int(page_var.get()))

            #-----------------伸缩选择
        def minus():
            zoom_list=[8.0, 6.4, 4.0, 2.0, 1.7, 1.5, 1.3, 1.0, 0.7, 0.3, 0.1]
            if self.zoom_x>0.1:
                for i in zoom_list:
                    if i <self.zoom_x:
                        self.zoom_x=i
                        self.zoom_y=i
                        break
            else:
                pass
            self.run()

        def plus():
            zoom_list=[0.1,0.3,0.7,1.0,1.3,1.5,1.7,2.0,4.0,6.4,8.0]
            if self.zoom_x<8.0:
                for i in zoom_list:
                    if i >self.zoom_x:
                        self.zoom_x=i
                        self.zoom_y=i
                        break
            else:
                pass
            self.run()
    
        def zoom():
            self.zoom_x=zoom_optionmenu.get()
            self.zoom_y=zoom_optionmenu.get()
            self.run()
                
            
            #-----------------旋转选择
        def rotate():
            self.rotate=float(rotate_entry.get())
            self.run()

            #--------------------批注
        def Highlight():
            self.canvas.bind('<Motion>',pdf_highlight)
        def pdf_hight(event):
            x=self.canvas.canvasx(event.x)
            y=self.canvas.canvasy(event.y)
            pge=self.doc[y//self.pix_height]
            r=fitz.Rect()
            
        #-------------------------------------菜单
        MenuBar=tk.Menu(self.main)
        filemenu=tk.Menu(MenuBar,tearoff=False)
        filemenu.add_command(label='open',command=menu_open)
        filemenu.add_command(label='save',command=menu_save)
        MenuBar.add_cascade(label='file',menu=filemenu)
        self.main.config(menu=MenuBar)
        #------------------------------------第一行工具栏
        first_toolbar=tk.Frame(self.main)
        main_button=tk.Button(first_toolbar,text='main')
        main_button.grid(row=0,column=0,columnspan=2,sticky='w',padx=5,pady=5)
        tool_button=tk.Button(first_toolbar,text='tool')
        tool_button.grid(row=0,column=2,columnspan=2,sticky='w',padx=5,pady=5)
        i=0
        if self.pdf_files:
            for file in self.pdf_files:
                text=os.path.basename(file)
                i+=1
                if len(file)>10:
                    name=text[0:10]+'button'
                else:
                    name=text+'_button'
                tk.Button(first_toolbar,text=name,command=command(i))
        columnspan=4+i
        first_toolbar.grid(row=0,column=0,columnspan=columnspan)
        #-----------------------------------第二行工具栏
                #---------------------------页码选择
        second_toolbar=tk.Frame(self.main)
        self.lastpage_img=tk.PhotoImage(file='icons/left.png')
        lastpage_button=tk.Button(second_toolbar,image=self.lastpage_img,width=-1,height=-1,command=lastpage)
        lastpage_button.grid(row=1,column=0,sticky='w',padx=5,pady=5)
        page_var=tk.IntVar()
        page_var.set(self.current_page)
        page_entry=tk.Entry(second_toolbar,textvariable=page_var,width=5)
        page_entry.grid(row=1,column=1,columnspan=2,sticky='w',padx=5,pady=5)
        self.pages_label=tk.Label(second_toolbar,text='('+str(self.pages)+')',width=-1,height=-1)
        self.pages_label.grid(row=1,column=3,sticky='w',padx=5,pady=5)
        page_button=tk.Button(second_toolbar,text='Go',width=-1,height=-1,command=page_go)
        page_button.grid(row=1,column=4,sticky='w',padx=5,pady=5)
        self.nextpage_img=tk.PhotoImage(file='icons/right.png')
        nextpage_button=tk.Button(second_toolbar,image=self.nextpage_img,width=-1,height=-1,command=nextpage)
        nextpage_button.grid(row=1,column=5,sticky='w',padx=5,pady=5)
                #------------------------伸缩选择
        self.minus_img=tk.PhotoImage(file='icons/minus.png')
        minus_button=tk.Button(second_toolbar,image=self.minus_img,width=-1,height=-1,command=minus)
        minus_button.grid(row=1,column=6,sticky='w',padx=5,pady=5)
        zoom_var=tk.DoubleVar()
        zoom_var.set(1.0)
        zoom_optionmenu=tk.OptionMenu(second_toolbar,zoom_var,0.1,0.3,0.7,1.0,1.3,1.5,1.7,2.0,4.0,6.4,8.0)
        zoom_optionmenu.grid(row=1,column=7,sticky='w',padx=5,pady=5)
        zoom_optionmenu.bind('<FocusOut>',zoom)
        self.plus_img=tk.PhotoImage(file='icons/plus.png')
        plus_button=tk.Button(second_toolbar,image=self.plus_img,width=-1,height=-1,command=plus)
        plus_button.grid(row=1,column=8,sticky='w',padx=5,pady=5)
                #----------------------旋转选择
        rotate_entry=tk.Entry(second_toolbar,width=5)
        rotate_entry.grid(row=1,column=9,columnspan=2,sticky='w',padx=5,pady=5)
        self.rotate_img=tk.PhotoImage(file='icons/rotate.png')
        rotate_button=tk.Button(second_toolbar,image=self.rotate_img,width=-1,height=-1,command=rotate)
        rotate_button.grid(row=1,column=11,sticky='w',padx=5,pady=5)
        second_toolbar.grid(row=1,column=0,columnspan=12,sticky='w',padx=5,pady=5)

    def run(self):
        def root_destroy():
            if msg.askokcancel('Quit','Do you really wish to quit?'):
                self.main.destroy()

        def mouse_wheel(event):
            self.pdf_canvas.yview_scroll(int(-1*(event.delta/120)),'units')
                               
        #--------------------阅读界面
        pdf_frame=tk.Frame(self.main)
        if  not self.current_pdf_file=='':
            self.doc=fitz.open(self.current_pdf_file)
            self.pages=self.doc.pageCount
            self.pages_label.config(text='('+str(self.pages)+')')
            self.pdf(self.doc,0)
            self.pdf_yscrollbar=tk.Scrollbar(pdf_frame,orient=tk.VERTICAL)
            self.pdf_yscrollbar.pack(side='right',fill='y')
            pdf_xscrollbar=tk.Scrollbar(pdf_frame,orient=tk.HORIZONTAL)
            pdf_xscrollbar.pack(side='bottom',fill='x')
            self.pdf_canvas=tk.Canvas(pdf_frame,bd=0,width=self.pix_width,height=self.pix_height*self.pages,scrollregion=(0,0,self.pix_width,self.pix_height*self.pages),yscrollcommand=self.pdf_yscrollbar.set,xscrollcommand=pdf_xscrollbar.set)
            self.pdf_canvas.pack(side='left',fill='none',anchor='nw')
            self.pdf_canvas.bind_all('<MouseWheel>',mouse_wheel)
            self.pdf_yscrollbar.config(command=self.pdf_canvas.yview)
            pdf_xscrollbar.config(command=self.pdf_canvas.xview)
            img=[]
            for page in range(self.pages):
                img.append(self.pdf(self.doc,page))
                self.pdf_canvas.create_image(0,page*self.pix_height,image=img[-1],anchor=tk.NW,tags=str(page))
                self.pdf_canvas.create_line(0,page*self.pix_height,self.pix_width,page*self.pix_height)
                self.pdf_canvas.create_text(self.pix_width,page*self.pix_height,text=str(page),anchor=tk.NE)
        else:
            pass
        pdf_frame.grid(row=2,rowspan=15,column=0,columnspan=21)
        self.main.mainloop()
        self.main.protocol('WM_DELETE_WINDOW',root_destroy)

if __name__=='__main__':
    pdf_reader=PDF_Reader()
    pdf_reader.ui()
    pdf_reader.run()