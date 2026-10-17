import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import math, random, json, os, threading, urllib.request, urllib.error
from .database import Database

BG = "#050817"; SIDEBAR = "#070d20"; PANEL = "#0a122b"; PANEL2 = "#111b3a"
EDGE = "#1a2b55"; TEXT = "#f5f7ff"; MUTED = "#91a0c8"
CYAN = "#00eaff"; BLUE = "#218bff"; PURPLE = "#a238ff"; PINK = "#ff3bd4"
GREEN = "#19e6a3"; GOLD = "#ffbd42"; RED = "#ff5a83"

class NeonButton(tk.Button):
    def __init__(self, master, text, command, bg=PANEL2, fg=TEXT, **kw):
        super().__init__(master, text=text, command=command, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg, bd=0, relief="flat",
                         font=("Segoe UI", 9, "bold"), padx=12, pady=8, cursor="hand2",
                         highlightthickness=1, highlightbackground=EDGE, **kw)
        self.bind("<Enter>", lambda e: self.configure(highlightbackground=CYAN))
        self.bind("<Leave>", lambda e: self.configure(highlightbackground=EDGE))

class AnimatedBackdrop(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, highlightthickness=0, **kw)
        self.dots=[]
        for _ in range(42):
            x=random.randint(0,1000); y=random.randint(0,700); r=random.choice([1,1,2])
            item=self.create_oval(x,y,x+r,y+r,fill=random.choice([CYAN,BLUE,PURPLE,"#465da5"]),outline="")
            self.dots.append((item,random.uniform(.25,1.0),r))
        self.after(90,self.animate)
    def animate(self):
        try:
            w=max(self.winfo_width(),1); h=max(self.winfo_height(),1)
            for item,speed,r in self.dots:
                c=self.coords(item)
                if not c: continue
                x,y=c[0],c[1]+speed
                if y>h: x,y=random.randint(0,w),0
                self.coords(item,x,y,x+r,y+r)
            self.after(90,self.animate)
        except tk.TclError: pass

class Mascot(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master,bg=kw.pop("bg",PANEL),highlightthickness=0,**kw)
        self.t=0; self.bind("<Configure>",lambda e:self.draw()); self.after(150,self.tick)
    def tick(self): self.t+=1; self.draw(); self.after(130,self.tick)
    def draw(self):
        self.delete("all"); w=max(self.winfo_width(),1); h=max(self.winfo_height(),1)
        cx=w*.53; cy=h*.48+math.sin(self.t/5)*2
        for pad,col in [(28,"#152a70"),(17,"#183e8b"),(7,"#432477")]:
            self.create_oval(cx-62-pad,cy-43-pad/2,cx+62+pad,cy+43+pad/2,outline=col,width=2)
        self.create_oval(cx-48,cy-48,cx+48,cy+48,fill="#0c1d4b",outline=BLUE,width=3)
        self.create_oval(cx-39,cy-39,cx+39,cy+39,fill="#14275c",outline=PURPLE,width=3)
        self.create_polygon(cx-29,cy-22,cx+29,cy-22,cx+34,cy-10,cx+34,cy+22,cx+24,cy+30,cx-24,cy+30,cx-34,cy+22,cx-34,cy-10,fill="#071126",outline=CYAN,width=2)
        self.create_oval(cx-48,cy-7,cx-34,cy+14,fill="#154c96",outline=CYAN,width=2)
        self.create_oval(cx+34,cy-7,cx+48,cy+14,fill="#154c96",outline=CYAN,width=2)
        if self.t%32 not in (0,1):
            self.create_oval(cx-19,cy-4,cx-9,cy+10,fill=CYAN,outline="")
            self.create_oval(cx+9,cy-4,cx+19,cy+10,fill=CYAN,outline="")
        else:
            self.create_line(cx-19,cy+3,cx-9,cy+3,fill=CYAN,width=3)
            self.create_line(cx+9,cy+3,cx+19,cy+3,fill=CYAN,width=3)
        self.create_arc(cx-10,cy+5,cx+10,cy+18,start=205,extent=130,style="arc",outline=PINK,width=2)
        self.create_text(cx,h-12,text="FOCUS BOT  •  ONLINE",fill=CYAN,font=("Segoe UI",7,"bold"))

class FocusFlowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FocusFlow | Neon Student Productivity Studio")
        self.geometry("1500x940"); self.minsize(1160,760); self.configure(bg=BG)
        self.db=Database(); self.timer_seconds=1500; self.timer_length=25; self.timer_running=False; self.timer_after=None
        self._build_shell(); self.show_page("Dashboard")

    def _build_shell(self):
        # Fixed sidebar matching the reference layout.
        self.side=tk.Frame(self,bg=SIDEBAR,width=205,highlightbackground="#14244b",highlightthickness=1)
        self.side.pack(side="left",fill="y"); self.side.pack_propagate(False)
        logo=tk.Frame(self.side,bg=SIDEBAR); logo.pack(fill="x",padx=15,pady=(16,20))
        icon=tk.Canvas(logo,width=38,height=38,bg=SIDEBAR,highlightthickness=0); icon.pack(side="left")
        icon.create_oval(2,2,36,36,fill="#14265a",outline=CYAN,width=2); icon.create_text(19,19,text="✦",fill=CYAN,font=("Segoe UI",18,"bold"))
        box=tk.Frame(logo,bg=SIDEBAR); box.pack(side="left",padx=7)
        tk.Label(box,text="FocusFlow",bg=SIDEBAR,fg=TEXT,font=("Segoe UI",13,"bold")).pack(anchor="w")
        tk.Label(box,text="STUDENT STUDIO",bg=SIDEBAR,fg=CYAN,font=("Segoe UI",7,"bold")).pack(anchor="w")
        tk.Label(self.side,text="W O R K S P A C E",bg=SIDEBAR,fg="#63739e",font=("Segoe UI",8,"bold")).pack(anchor="w",padx=18,pady=(0,8))
        self.nav={}
        items=[("Dashboard","⌂"),("My Tasks","☑"),("Quick Notes","▤"),("Focus Timer","◴"),("Study Goals","◎"),("Analytics","↗"),("Calendar","▦"),("Settings","⚙"),("About Project","ⓘ")]
        for name,sym in items:
            b=tk.Button(self.side,text=f"  {sym}   {name}",anchor="w",bg=SIDEBAR,fg=MUTED,activebackground="#172653",activeforeground=CYAN,bd=0,font=("Segoe UI",9,"bold"),padx=12,pady=9,cursor="hand2",command=lambda n=name:self.show_page(n))
            b.pack(fill="x",padx=10,pady=2); self.nav[name]=b
        filler=tk.Frame(self.side,bg=SIDEBAR); filler.pack(fill="both",expand=True)
        streak=tk.Frame(self.side,bg="#10173a",highlightbackground=PURPLE,highlightthickness=1); streak.pack(fill="x",padx=12,pady=8)
        tk.Label(streak,text="🔥  Keep Going!",bg="#10173a",fg="#ffd7f7",font=("Segoe UI",9,"bold")).pack(anchor="w",padx=10,pady=(8,2))
        tk.Label(streak,text="Small steps. Big results.",bg="#10173a",fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",padx=10)
        tk.Frame(streak,bg="#25386d",height=5).pack(fill="x",padx=10,pady=9)
        profile=tk.Frame(self.side,bg="#0c1430",highlightbackground=EDGE,highlightthickness=1); profile.pack(fill="x",padx=12,pady=(0,12))
        tk.Label(profile,text="SR",bg="#193f91",fg="white",font=("Segoe UI",11,"bold"),width=3,pady=7).pack(side="left",padx=8,pady=8)
        pbox=tk.Frame(profile,bg="#0c1430"); pbox.pack(side="left")
        tk.Label(pbox,text="Student Profile",bg="#0c1430",fg=TEXT,font=("Segoe UI",8,"bold")).pack(anchor="w")
        tk.Label(pbox,text="Local workspace",bg="#0c1430",fg=MUTED,font=("Segoe UI",7)).pack(anchor="w")
        # Content region and topbar
        self.right=tk.Frame(self,bg=BG); self.right.pack(side="left",fill="both",expand=True)
        self.top=tk.Frame(self.right,bg="#070c1c",height=58,highlightbackground="#17244a",highlightthickness=1); self.top.pack(fill="x"); self.top.pack_propagate(False)
        tk.Label(self.top,text="⌕",bg="#0d1632",fg=MUTED,font=("Segoe UI",14),width=3).pack(side="left",padx=(16,0),pady=9)
        self.global_search=tk.Entry(self.top,bg="#0d1632",fg=TEXT,insertbackground=CYAN,relief="flat",font=("Segoe UI",9),width=38)
        self.global_search.insert(0,"Search tasks, notes, topics..."); self.global_search.pack(side="left",ipady=9,pady=9)
        self.global_search.bind("<Return>",lambda e:self._global_search())
        tk.Button(self.top,text="⌕",bg="#0d1632",fg=CYAN,bd=0,command=self._global_search,cursor="hand2").pack(side="left",padx=(0,12),pady=9)
        tk.Label(self.top,text="♧  3",bg="#070c1c",fg=TEXT,font=("Segoe UI",10)).pack(side="right",padx=12)
        tk.Label(self.top,text="☼",bg="#070c1c",fg=GOLD,font=("Segoe UI",14)).pack(side="right",padx=7)
        tk.Label(self.top,text="✧",bg="#070c1c",fg=PURPLE,font=("Segoe UI",13)).pack(side="right",padx=7)
        self.breadcrumb=tk.Label(self.top,text="DASHBOARD",bg="#070c1c",fg=CYAN,font=("Segoe UI",8,"bold")); self.breadcrumb.pack(side="right",padx=20)
        self.backdrop=AnimatedBackdrop(self.right); self.backdrop.place(x=0,y=58,relwidth=1,relheight=1)
        self.body=tk.Frame(self.right,bg=BG); self.body.pack(fill="both",expand=True,padx=20,pady=15); self.body.lift()

    def panel(self,parent,bg=PANEL,edge=EDGE):
        return tk.Frame(parent,bg=bg,highlightbackground=edge,highlightthickness=1)
    def label(self,parent,text,size=9,color=TEXT,bold=False,bg=None,**kw):
        return tk.Label(parent,text=text,font=("Segoe UI",size,"bold" if bold else "normal"),fg=color,bg=bg or parent.cget("bg"),**kw)
    def button(self,parent,text,command,bg=PANEL2,fg=TEXT,**kw): return NeonButton(parent,text,command,bg,fg,**kw)

    def show_page(self,name):
        self.page=name
        for n,b in self.nav.items():
            b.configure(bg="#14224a" if n==name else SIDEBAR,fg=CYAN if n==name else MUTED,
                        highlightthickness=1 if n==name else 0,highlightbackground=CYAN if n==name else SIDEBAR)
        self.breadcrumb.configure(text=name.upper())
        for w in self.body.winfo_children(): w.destroy()
        if name=="Dashboard": self.dashboard()
        elif name=="My Tasks": self.tasks_page()
        elif name=="Quick Notes": self.notes_page()
        elif name=="Focus Timer": self.timer_page()
        elif name=="Study Goals": self.goals_page()
        elif name=="Analytics": self.analytics_page()

        elif name=="Calendar": self.info_page("STUDY CALENDAR","Use task due dates in My Tasks to plan your schedule. A full calendar grid can be added as a future module.")
        elif name=="Settings": self.info_page("SETTINGS","FocusFlow stores tasks, notes and completed focus sessions in a local SQLite database. Keep focusflow.db to preserve your data.")

        else: self.about_page()

    def _global_search(self):
        q=self.global_search.get().strip()
        self.show_page("My Tasks")
        if hasattr(self,"task_search"):
            self.task_search.delete(0,"end"); self.task_search.insert(0,"" if q=="Search tasks, notes, topics..." else q); self.refresh_tasks()

    def dashboard(self):
        stats=self.db.task_stats(); focus=self.db.focus_stats()
        # Top hero row: greeting + mascot, reference-style.
        top=tk.Frame(self.body,bg=BG); top.pack(fill="x",pady=(0,12))
        hero=self.panel(top,bg="#11143a",edge="#332778"); hero.pack(side="left",fill="both",expand=True,padx=(0,10))
        h=tk.Frame(hero,bg="#11143a"); h.pack(fill="both",expand=True,padx=20,pady=15)
        self.label(h,"✦  GOOD TO SEE YOU",8,CYAN,True).pack(anchor="w")
        self.label(h,"Welcome back, Student! 👋",23,TEXT,True).pack(anchor="w",pady=(5,1))
        self.label(h,"Your potential is endless. Plan • Focus • Learn • Achieve.",9,"#c2cbed").pack(anchor="w")
        badges=tk.Frame(h,bg="#11143a"); badges.pack(anchor="w",pady=(11,0))
        for txt,col in [(f"🔥 {stats['done']} goals completed",PINK),(f"⭐ {focus['sessions']} focus sprints",GOLD),("🎯 Keep your streak alive",CYAN)]:
            tk.Label(badges,text=txt,bg="#28205a",fg=col,font=("Segoe UI",8,"bold"),padx=10,pady=5).pack(side="left",padx=(0,7))
        mascot_frame=self.panel(top,bg="#09122d",edge=BLUE); mascot_frame.pack(side="right",fill="y")
        Mascot(mascot_frame,width=210,height=152,bg="#09122d").pack(fill="both",expand=True,padx=4,pady=3)
        # Stats cards: task totals, completed, active, streak
        cards=tk.Frame(self.body,bg=BG); cards.pack(fill="x",pady=(0,12))
        streak_days=min(focus["sessions"],30)
        data=[("✓",stats["total"],"TOTAL TASKS",CYAN),("◎",stats["done"],"COMPLETED",PURPLE),("⌛",stats["active"],"IN PROGRESS",GOLD),("♛",streak_days,"DAY STREAK",BLUE)]
        for i,(sym,val,title,col) in enumerate(data):
            c=self.panel(cards,bg="#0a1228",edge=col); c.grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 5,0 if i==3 else 5)); cards.grid_columnconfigure(i,weight=1,uniform="stats")
            tk.Frame(c,bg=col,height=3).pack(fill="x")
            inside=tk.Frame(c,bg="#0a1228"); inside.pack(fill="x",padx=13,pady=10)
            self.label(inside,sym,16,col,True).pack(anchor="w")
            self.label(inside,str(val),22,TEXT,True).pack(anchor="w",pady=(1,0))
            self.label(inside,title,8,MUTED,True).pack(anchor="w")
        # Mid feature scenic panel and timer.
        mid=tk.Frame(self.body,bg=BG); mid.pack(fill="x",pady=(0,12))
        scene=self.panel(mid,bg="#0b1234",edge="#204fba"); scene.pack(side="left",fill="both",expand=True,padx=(0,10))
        art=tk.Canvas(scene,height=170,bg="#0b1234",highlightthickness=0); art.pack(fill="both",expand=True)
        def draw_scene(event=None):
            art.delete("all"); w=max(art.winfo_width(),1); h=max(art.winfo_height(),1)
            # starfield and layered mountain silhouettes to evoke reference art
            for i in range(36):
                x=(i*97+19)%w; y=(i*31+9)%(h//2+1)
                art.create_oval(x,y,x+2,y+2,fill=random.choice([CYAN,BLUE,PURPLE]),outline="")
            art.create_oval(w*.68,h*.35,w*.78,h*.88,fill="#fa6dd5",outline="")
            art.create_polygon(0,h*.82,w*.14,h*.42,w*.26,h*.78,w*.38,h*.33,w*.56,h*.83,w*.70,h*.53,w*.83,h*.82,w,h*.43,w,h,0,h,fill="#182b73",outline="")
            art.create_polygon(0,h*.90,w*.18,h*.65,w*.32,h*.91,w*.47,h*.56,w*.62,h*.9,w*.82,h*.64,w,h*.86,w,h,0,h,fill="#101b4c",outline="")
            art.create_line(0,h*.96,w*.18,h*.92,w*.32,h*.98,w*.49,h*.87,w*.66,h*.94,w*.82,h*.9,w,h*.97,fill=CYAN,width=2,smooth=True)
            art.create_text(20,24,text="TURN YOUR GOALS",anchor="w",fill=TEXT,font=("Segoe UI",18,"bold"))
            art.create_text(20,51,text="INTO REALITY  🚀",anchor="w",fill=CYAN,font=("Segoe UI",18,"bold"))
            art.create_text(20,77,text="Plan • Focus • Learn • Achieve",anchor="w",fill="#c0cbf0",font=("Segoe UI",9))
            # call to action button drawn as clickable canvas region
            art.create_rectangle(20,105,168,139,fill="#5221ce",outline=CYAN,width=1,tags="add")
            art.create_text(94,122,text="＋ Add New Task",fill="white",font=("Segoe UI",9,"bold"),tags="add")
        art.bind("<Configure>",draw_scene); art.tag_bind("add","<Button-1>",lambda e:self.show_page("My Tasks"))
        timer=self.panel(mid,bg="#0a122b",edge=PURPLE); timer.pack(side="right",fill="y")
        self.label(timer,"◷  FOCUS TIMER",9,CYAN,True).pack(padx=18,pady=(13,3))
        # Circular timer visualization
        ring=tk.Canvas(timer,width=156,height=128,bg="#0a122b",highlightthickness=0); ring.pack(padx=8)
        ring.create_oval(14,3,142,121,outline="#15265d",width=10)
        ring.create_arc(14,3,142,121,start=90,extent=300,style="arc",outline=BLUE,width=7)
        ring.create_arc(14,3,142,121,start=-30,extent=100,style="arc",outline=PINK,width=7)
        ring.create_text(78,52,text="25:00",fill=TEXT,font=("Segoe UI",20,"bold"))
        ring.create_text(78,77,text="Focus Time",fill=MUTED,font=("Segoe UI",8))
        self.button(timer,"▶  START FOCUS",lambda:self.show_page("Focus Timer"),"#4a1bd0",TEXT).pack(fill="x",padx=15,pady=(2,13))
        # Bottom analytics, progress and upcoming task cards.
        bottom=tk.Frame(self.body,bg=BG); bottom.pack(fill="both",expand=True)
        progress=self.panel(bottom,bg="#0a1228"); progress.pack(side="left",fill="both",expand=True,padx=(0,6))
        self.label(progress,"TODAY'S PROGRESS",9,TEXT,True).pack(anchor="w",padx=13,pady=(12,8))
        pct=int(stats["done"]/stats["total"]*100) if stats["total"] else 0
        donut=tk.Canvas(progress,width=110,height=105,bg="#0a1228",highlightthickness=0); donut.pack(side="left",padx=(10,4),pady=3)
        donut.create_oval(9,7,101,99,outline="#1d2b59",width=9)
        donut.create_arc(9,7,101,99,start=90,extent=-3.6*pct,style="arc",outline=CYAN,width=9)
        donut.create_text(55,53,text=f"{pct}%",fill=TEXT,font=("Segoe UI",13,"bold"))
        txt=tk.Frame(progress,bg="#0a1228"); txt.pack(side="left",fill="both",expand=True,padx=4)
        for t in [f"✓  {stats['done']} / {stats['total']} tasks completed",f"✓  {focus['minutes']//60} hours study time", "✓  Keep going! 🔥"]:
            self.label(txt,t,8,"#bdc9ec").pack(anchor="w",pady=5)
        analytics=self.panel(bottom,bg="#0a1228"); analytics.pack(side="left",fill="both",expand=True,padx=6)
        self.label(analytics,"STUDY ANALYTICS",9,TEXT,True).pack(anchor="w",padx=13,pady=(12,4))
        chart=tk.Canvas(analytics,height=104,bg="#0a1228",highlightthickness=0); chart.pack(fill="both",expand=True,padx=10,pady=(0,8))
        def draw_chart(event=None):
            chart.delete("all"); w=max(chart.winfo_width(),1); h=max(chart.winfo_height(),1)
            chart.create_line(5,h-22,w-5,h-22,fill="#25345f")
            vals=[.25,.38,.68,.35,.48,.86,.55]
            names=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            bw=max(8,int(w/18))
            for i,v in enumerate(vals):
                x=10+(i+.5)*((w-20)/7); bh=(h-34)*v
                color=[BLUE,BLUE,PURPLE,BLUE,BLUE,PINK,CYAN][i]
                chart.create_rectangle(x-bw/2,h-22-bh,x+bw/2,h-22,fill=color,outline="")
                chart.create_text(x,h-9,text=names[i],fill=MUTED,font=("Segoe UI",7))
            chart.create_line(0,h*.35,w,h*.35,fill="#111d3d")
        chart.bind("<Configure>",draw_chart)
        upcoming=self.panel(bottom,bg="#0a1228"); upcoming.pack(side="left",fill="both",expand=True,padx=(6,0))
        head=tk.Frame(upcoming,bg="#0a1228"); head.pack(fill="x",padx=13,pady=(12,6))
        self.label(head,"UPCOMING TASKS",9,TEXT,True).pack(side="left")
        tk.Button(head,text="View all →",command=lambda:self.show_page("My Tasks"),bg="#0a1228",fg=CYAN,bd=0,cursor="hand2").pack(side="right")
        tasks=self.db.tasks(status="Active")[:3]
        if not tasks:self.label(upcoming,"No tasks yet. Add your first task!",8,MUTED).pack(anchor="w",padx=13,pady=10)
        for t in tasks:
            row=tk.Frame(upcoming,bg="#0a1228"); row.pack(fill="x",padx=12,pady=4)
            self.label(row,"◯",11,CYAN,True).pack(side="left")
            txt=tk.Frame(row,bg="#0a1228"); txt.pack(side="left",fill="x",expand=True,padx=5)
            self.label(txt,t["title"][:24],8,TEXT,True).pack(anchor="w")
            self.label(txt,t["due_date"] or "No due date",7,MUTED).pack(anchor="w")
            color=RED if t["priority"]=="High" else GOLD if t["priority"]=="Medium" else GREEN
            self.label(row,t["priority"],7,color,True).pack(side="right")
        # Quick launch row, similar to the reference's four action cards.
        quick=tk.Frame(self.body,bg=BG); quick.pack(fill="x",pady=(10,0))
        for i,(title,sub,sym,col,page) in enumerate([
            ("Add Task","Plan your work","＋",CYAN,"My Tasks"),("New Note","Capture ideas","▤",PURPLE,"Quick Notes"),
            ("Start Focus","Stay distraction free","◷",PINK,"Focus Timer"),("View Calendar","Manage schedule","▦",BLUE,"Calendar")]):
            c=self.panel(quick,bg="#0b1430",edge=col); c.grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 5,0 if i==3 else 5)); quick.grid_columnconfigure(i,weight=1,uniform="quick")
            tk.Button(c,text=f"{sym}  {title}\n     {sub}     →",command=lambda p=page:self.show_page(p),anchor="w",justify="left",bg="#0b1430",fg=TEXT,activebackground="#14234a",activeforeground=col,bd=0,font=("Segoe UI",8,"bold"),padx=10,pady=10,cursor="hand2").pack(fill="both",expand=True)

    def tasks_page(self):
        form=self.panel(self.body,bg="#0a1228");form.pack(fill="x",pady=(0,10))
        self.label(form,"CREATE A NEW TASK",9,CYAN,True).pack(anchor="w",padx=14,pady=(12,7))
        row=tk.Frame(form,bg="#0a1228");row.pack(fill="x",padx=14,pady=(0,12))
        self.task_title=tk.Entry(row,bg="#111b3a",fg=TEXT,insertbackground=CYAN,relief="flat",font=("Segoe UI",9));self.task_title.pack(side="left",fill="x",expand=True,ipady=9,padx=(0,6))
        self.task_cat=ttk.Combobox(row,values=["Study","Assignment","Project","Personal","Health","Other"],state="readonly",width=12);self.task_cat.set("Study");self.task_cat.pack(side="left",padx=4)
        self.task_pri=ttk.Combobox(row,values=["Low","Medium","High"],state="readonly",width=9);self.task_pri.set("Medium");self.task_pri.pack(side="left",padx=4)
        self.task_due=tk.Entry(row,bg="#111b3a",fg=MUTED,insertbackground=CYAN,relief="flat",width=12);self.task_due.insert(0,"YYYY-MM-DD");self.task_due.pack(side="left",padx=4,ipady=9)
        self.button(row,"＋ ADD TASK",self.add_task,CYAN,"#04101c").pack(side="left",padx=(6,0))
        controls=tk.Frame(self.body,bg=BG);controls.pack(fill="x",pady=(0,8))
        self.task_search=tk.Entry(controls,bg="#0a1228",fg=TEXT,insertbackground=CYAN,relief="flat",width=30);self.task_search.pack(side="left",ipady=8,padx=(0,7));self.task_search.bind("<KeyRelease>",lambda e:self.refresh_tasks())
        self.task_filter=ttk.Combobox(controls,values=["All","Active","Completed"],state="readonly",width=12);self.task_filter.set("All");self.task_filter.pack(side="left");self.task_filter.bind("<<ComboboxSelected>>",lambda e:self.refresh_tasks())
        self.label(controls,"Double-click a row to toggle completion",8,MUTED).pack(side="right")
        table=self.panel(self.body,bg="#0a1228");table.pack(fill="both",expand=True)
        cols=("title","category","priority","due","status");self.task_tree=ttk.Treeview(table,columns=cols,show="headings")
        for c,t,w in [("title","TASK",400),("category","CATEGORY",120),("priority","PRIORITY",100),("due","DUE DATE",120),("status","STATUS",100)]:
            self.task_tree.heading(c,text=t);self.task_tree.column(c,width=w,anchor="w" if c=="title" else "center")
        self.task_tree.pack(fill="both",expand=True,padx=10,pady=10);self.task_tree.bind("<Double-1>",self.toggle_task)
        actions=tk.Frame(self.body,bg=BG);actions.pack(fill="x",pady=(9,0))
        self.button(actions,"✓  TOGGLE COMPLETE",self.toggle_task,GREEN,"#04101c").pack(side="left")
        self.button(actions,"DELETE SELECTED",self.delete_task,"#34162f","#ffdce8").pack(side="left",padx=8)
        self.refresh_tasks()

    def add_task(self):
        title=self.task_title.get().strip();due=self.task_due.get().strip()
        if not title:messagebox.showwarning("Title required","Enter a task title first.");return
        if due=="YYYY-MM-DD":due=""
        if due:
            try:date.fromisoformat(due)
            except ValueError:messagebox.showwarning("Invalid date","Use YYYY-MM-DD or leave the date empty.");return
        self.db.add_task(title,self.task_cat.get(),self.task_pri.get(),due)
        self.task_title.delete(0,"end");self.task_due.delete(0,"end");self.task_due.insert(0,"YYYY-MM-DD")
        self.refresh_tasks();messagebox.showinfo("Saved","Task added successfully.")
    def refresh_tasks(self):
        if not hasattr(self,"task_tree") or not self.task_tree.winfo_exists():return
        for i in self.task_tree.get_children():self.task_tree.delete(i)
        for t in self.db.tasks(self.task_search.get() if hasattr(self,"task_search") else "",self.task_filter.get() if hasattr(self,"task_filter") else "All"):
            self.task_tree.insert("","end",iid=str(t["id"]),values=(t["title"],t["category"],t["priority"],t["due_date"] or "—","Completed" if t["completed"] else "Active"))
    def selected_task(self):
        s=self.task_tree.selection();return int(s[0]) if s else None
    def toggle_task(self,event=None):
        tid=self.selected_task()
        if not tid:
            if event is None:messagebox.showinfo("Select task","Select a task row first.")
            return
        self.db.toggle_task(tid);self.refresh_tasks()
    def delete_task(self):
        tid=self.selected_task()
        if not tid:messagebox.showinfo("Select task","Select a task row first.");return
        if messagebox.askyesno("Delete task","Delete this task permanently?"):self.db.delete_task(tid);self.refresh_tasks()

    def notes_page(self):
        outer=tk.Frame(self.body,bg=BG);outer.pack(fill="both",expand=True)
        left=self.panel(outer,bg="#0a1228");left.pack(side="left",fill="y",padx=(0,9));left.configure(width=260);left.pack_propagate(False)
        self.label(left,"YOUR NOTEBOOK",9,CYAN,True).pack(anchor="w",padx=12,pady=(12,7))
        self.note_search=tk.Entry(left,bg="#111b3a",fg=TEXT,insertbackground=CYAN,relief="flat");self.note_search.pack(fill="x",padx=10,ipady=8);self.note_search.bind("<KeyRelease>",lambda e:self.refresh_notes())
        self.note_list=tk.Listbox(left,bg="#0a1228",fg=TEXT,selectbackground="#253d7a",relief="flat",font=("Segoe UI",9),activestyle="none");self.note_list.pack(fill="both",expand=True,padx=9,pady=9);self.note_list.bind("<<ListboxSelect>>",self.load_note)
        right=self.panel(outer,bg="#0a1228");right.pack(side="left",fill="both",expand=True)
        self.label(right,"NOTE EDITOR",9,CYAN,True).pack(anchor="w",padx=16,pady=(12,7))
        self.note_title=tk.Entry(right,bg="#111b3a",fg=TEXT,insertbackground=CYAN,relief="flat",font=("Segoe UI",12,"bold"));self.note_title.pack(fill="x",padx=16,pady=(0,8),ipady=9)
        self.note_text=tk.Text(right,bg="#070d20",fg=TEXT,insertbackground=CYAN,relief="flat",font=("Segoe UI",10),wrap="word",padx=12,pady=12);self.note_text.pack(fill="both",expand=True,padx=16,pady=(0,8))
        acts=tk.Frame(right,bg="#0a1228");acts.pack(fill="x",padx=16,pady=(0,12))
        self.button(acts,"＋ NEW NOTE",self.new_note).pack(side="left");self.button(acts,"SAVE NOTE",self.save_note,CYAN,"#04101c").pack(side="left",padx=7);self.button(acts,"DELETE",self.delete_note,"#34162f","#ffdce8").pack(side="left")
        self.selected_note_id=None;self.refresh_notes()
    def refresh_notes(self):
        if not hasattr(self,"note_list") or not self.note_list.winfo_exists():return
        self.note_list.delete(0,"end")
        for n in self.db.notes(self.note_search.get()):self.note_list.insert("end","  ✦  "+n["title"][:25])
    def load_note(self,event=None):
        sel=self.note_list.curselection()
        if not sel:return
        ns=self.db.notes(self.note_search.get())
        if sel[0]>=len(ns):return
        n=ns[sel[0]];self.selected_note_id=n["id"];self.note_title.delete(0,"end");self.note_title.insert(0,n["title"]);self.note_text.delete("1.0","end");self.note_text.insert("1.0",n["content"])
    def new_note(self):
        self.selected_note_id=None;self.note_title.delete(0,"end");self.note_text.delete("1.0","end");self.note_title.focus_set()
    def save_note(self):
        title=self.note_title.get().strip();content=self.note_text.get("1.0","end-1c").strip()
        if not title or not content:messagebox.showwarning("Missing content","Enter a title and some note content.");return
        self.db.save_note(title,content,self.selected_note_id);self.refresh_notes();messagebox.showinfo("Saved","Note saved.")
    def delete_note(self):
        if not self.selected_note_id:messagebox.showinfo("Select note","Select a saved note first.");return
        if messagebox.askyesno("Delete note","Delete this note?"):self.db.delete_note(self.selected_note_id);self.new_note();self.refresh_notes()

    def timer_page(self):
        hero=self.panel(self.body,bg="#10133b",edge=PURPLE);hero.pack(fill="x",pady=(0,12))
        self.label(hero,"THE DEEP WORK ZONE",10,CYAN,True).pack(pady=(17,4))
        self.label(hero,"One task. One sprint. No distractions.",18,TEXT,True).pack()
        self.label(hero,"Choose a session length and focus on one thing at a time.",9,MUTED).pack(pady=(5,16))
        p=self.panel(self.body,bg="#080f28",edge=BLUE);p.pack(fill="both",expand=True)
        ring=tk.Canvas(p,width=260,height=260,bg="#080f28",highlightthickness=0);ring.pack(pady=(22,4))
        ring.create_oval(15,15,245,245,outline="#1b2c62",width=14);ring.create_arc(15,15,245,245,start=90,extent=300,style="arc",outline=BLUE,width=9);ring.create_arc(15,15,245,245,start=-30,extent=100,style="arc",outline=PINK,width=9)
        self.timer_display=tk.Label(p,text=self.format_time(self.timer_seconds),bg="#080f28",fg=TEXT,font=("Segoe UI",30,"bold"));ring.create_window(130,115,window=self.timer_display)
        self.timer_status=self.label(p,"READY WHEN YOU ARE",9,CYAN,True);self.timer_status.pack(pady=(0,12))
        presets=tk.Frame(p,bg="#080f28");presets.pack()
        for m in (15,25,45):self.button(presets,f"{m} MIN",lambda mm=m:self.set_timer(mm)).pack(side="left",padx=4)
        acts=tk.Frame(p,bg="#080f28");acts.pack(pady=17)
        self.button(acts,"▶ START / RESUME",self.start_timer,CYAN,"#04101c").pack(side="left",padx=4);self.button(acts,"Ⅱ PAUSE",self.pause_timer).pack(side="left",padx=4);self.button(acts,"↺ RESET",lambda:self.set_timer(self.timer_length),"#34162f","#ffdce8").pack(side="left",padx=4)
        self.label(p,"Completed focus sessions are recorded in your local database.",8,MUTED).pack(pady=(0,18))
    @staticmethod
    def format_time(s):return f"{s//60:02d}:{s%60:02d}"
    def set_timer(self,m):
        self.pause_timer();self.timer_length=m;self.timer_seconds=m*60
        if hasattr(self,"timer_display") and self.timer_display.winfo_exists():self.timer_display.configure(text=self.format_time(self.timer_seconds));self.timer_status.configure(text=f"{m}-MINUTE SPRINT READY",fg=CYAN)
    def start_timer(self):
        if self.timer_running:return
        self.timer_running=True
        if hasattr(self,"timer_status") and self.timer_status.winfo_exists():self.timer_status.configure(text="FOCUS MODE ACTIVE",fg=GREEN)
        self.tick()
    def tick(self):
        if not self.timer_running:return
        if self.timer_seconds<=0:
            self.timer_running=False;self.db.add_focus_session(self.timer_length)
            if hasattr(self,"timer_status") and self.timer_status.winfo_exists():self.timer_status.configure(text="SPRINT COMPLETE!",fg=CYAN)
            messagebox.showinfo("Focus complete","Great work! Session recorded.");return
        if hasattr(self,"timer_display") and self.timer_display.winfo_exists():self.timer_display.configure(text=self.format_time(self.timer_seconds))
        self.timer_seconds-=1;self.timer_after=self.after(1000,self.tick)
    def pause_timer(self):
        self.timer_running=False
        if self.timer_after:
            try:self.after_cancel(self.timer_after)
            except tk.TclError:pass
            self.timer_after=None
        if hasattr(self,"timer_status") and self.timer_status.winfo_exists():self.timer_status.configure(text="PAUSED",fg=GOLD)

    def goals_page(self):
        s=self.db.task_stats();f=self.db.focus_stats();p=self.panel(self.body,bg="#0a1228");p.pack(fill="both",expand=True)
        self.label(p,"STUDY GOALS",20,TEXT,True).pack(anchor="w",padx=22,pady=(22,4));self.label(p,"Small goals build big momentum.",9,MUTED).pack(anchor="w",padx=22,pady=(0,14))
        for title,desc,val,col in [("Finish your task list","Complete tasks you've added",f"{int(s['done']/s['total']*100) if s['total'] else 0}% complete",CYAN),("Build a focus habit","Finish a focus sprint",f"{f['sessions']} sessions",PURPLE),("Capture your ideas","Keep useful notes in one place",f"{len(self.db.notes())} notes",GOLD)]:
            r=tk.Frame(p,bg="#111b3a",highlightbackground=EDGE,highlightthickness=1);r.pack(fill="x",padx=22,pady=6)
            self.label(r,"◎",18,col,True).pack(side="left",padx=15,pady=14)
            x=tk.Frame(r,bg="#111b3a");x.pack(side="left",fill="x",expand=True,pady=10);self.label(x,title,10,TEXT,True).pack(anchor="w");self.label(x,desc,8,MUTED).pack(anchor="w",pady=3);self.label(r,val,10,col,True).pack(side="right",padx=16)

    def analytics_page(self):
        s=self.db.task_stats();f=self.db.focus_stats();p=self.panel(self.body,bg="#0a1228");p.pack(fill="both",expand=True)
        self.label(p,"STUDY ANALYTICS",20,TEXT,True).pack(anchor="w",padx=22,pady=(22,5));self.label(p,"Statistics update from your saved application data.",9,MUTED).pack(anchor="w",padx=22,pady=(0,18))
        cards=tk.Frame(p,bg="#0a1228");cards.pack(fill="x",padx=16)
        for title,val,col in [("TOTAL TASKS",s["total"],CYAN),("COMPLETED",s["done"],GREEN),("ACTIVE",s["active"],GOLD),("FOCUS MINUTES",f["minutes"],PURPLE),("SESSIONS",f["sessions"],BLUE),("SAVED NOTES",len(self.db.notes()),PINK)]:
            c=self.panel(cards,bg="#111b3a",edge=col);c.pack(side="left",fill="both",expand=True,padx=4);self.label(c,title,8,MUTED,True).pack(pady=(15,5));self.label(c,str(val),22,col,True).pack(pady=(0,15))
        chart=self.panel(p,bg="#080f24");chart.pack(fill="both",expand=True,padx=20,pady=20)
        self.label(chart,"WEEKLY STUDY ACTIVITY  •  ILLUSTRATIVE VISUAL",9,CYAN,True).pack(anchor="w",padx=14,pady=(12,0))
        cv=tk.Canvas(chart,bg="#080f24",height=210,highlightthickness=0);cv.pack(fill="both",expand=True,padx=10,pady=10)
        def draw(e=None):
            cv.delete("all");w=max(cv.winfo_width(),1);h=max(cv.winfo_height(),1);vals=[.25,.4,.7,.35,.5,.9,.6];days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            for i,v in enumerate(vals):
                x=(i+.5)*w/7;bh=(h-35)*v;col=[BLUE,BLUE,PURPLE,BLUE,BLUE,PINK,CYAN][i];cv.create_rectangle(x-13,h-25-bh,x+13,h-25,fill=col,outline="");cv.create_text(x,h-11,text=days[i],fill=MUTED,font=("Segoe UI",8))
        cv.bind("<Configure>",draw)

    def info_page(self,title,desc):
        p=self.panel(self.body,bg="#0a1228");p.pack(fill="both",expand=True)
        self.label(p,title,22,CYAN,True).pack(anchor="w",padx=24,pady=(24,8));self.label(p,desc,10,MUTED,wraplength=700,justify="left").pack(anchor="w",padx=24)

    def about_page(self):
        p=self.panel(self.body,bg="#0a1228");p.pack(fill="both",expand=True)
        self.label(p,"FOCUSFLOW NEON STUDIO",21,CYAN,True).pack(anchor="w",padx=22,pady=(22,5));self.label(p,"Python + Tkinter + SQLite desktop productivity application.",9,MUTED).pack(anchor="w",padx=22,pady=(0,16))
        rows=[("Dashboard","Neon dashboard, animated star particles, vector robot mascot, live task totals and progress."),("Task manager","Create, search, filter, complete and delete tasks with priorities, categories and due dates."),("Quick Notes","Create, edit, search and delete saved notes."),("Focus Timer","15, 25 and 45 minute sessions with start, pause and reset."),("Study Goals and Analytics","Summary pages based on saved task, note and focus session data."),("SQLite persistence","Local database tables keep tasks, notes and completed sessions across restarts.")]
        for title,desc in rows:
            r=tk.Frame(p,bg="#111b3a");r.pack(fill="x",padx=22,pady=5);self.label(r,title,9,TEXT,True).pack(anchor="w",padx=12,pady=(9,3));self.label(r,desc,8,MUTED,wraplength=850,justify="left").pack(anchor="w",padx=12,pady=(0,9))

    def destroy(self):
        self.timer_running=False
        if self.timer_after:
            try:self.after_cancel(self.timer_after)
            except tk.TclError:pass
        super().destroy()
