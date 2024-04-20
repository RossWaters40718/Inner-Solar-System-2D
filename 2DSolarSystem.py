import tkinter as tk
from tkinter import DoubleVar, StringVar, IntVar, BooleanVar, Toplevel
from tkinter import ttk, font, messagebox, Menu
from tkinter.ttk import Progressbar
from win32api import GetMonitorInfo, MonitorFromPoint
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from astropy.coordinates import get_body
from astropy.coordinates import solar_system_ephemeris 
from astropy.time import Time
import astropy.units as u
from astroquery.jplhorizons import Horizons
from pathlib import Path
import numpy as np
import os
import re
def about():
       msg1='Creator: Ross Waters'
       msg2='\nEmail: RossWatersjr@gmail.com'
       msg3='\nRevision: 1.5'
       msg4='\nLast Revision Date: 04/20/2024'
       msg5='\nMatplotlib Version 3.8.0'
       msg6='\nAstropy Version 5.3.4'
       msg7='\nAstroquery Version 0.4.6'
       msg8='\nProgramming Language: Python 3.12.2 64-Bit'
       msg9='\nCreated For Windows 11'
       msg=msg1+msg2+msg3+msg4+msg5+msg6+msg7+msg8+msg9
       messagebox.showinfo('About Inner Solar System 2D', msg)
def anim_advance(frame):
    if Slider_Value.get()=='0': return
    inc=Increment_Step.get()
    day=(frame+1)*inc
    earth_days_past.set(str('Earth Days: '+str(round(day,6)))+' / Orbits: '+str(round((day/365.256),6)))
    mercury_days_past.set(str('Mercury Days: '+str(round(23.9345/1407.6*day,6)))+' / Orbits: '+str(round(day/87.969,6)))
    venus_days_past.set(str('Venus Days: '+str(round(23.9345/5832.5*day,6)))+' / Orbits: '+str(round(day/224.701,6)))
    mars_days_past.set(str('Mars Days: '+str(round(23.9345/24.6229*day,6)))+' / Orbits: '+str(round(day/686.980,6)))
    moon_orbits.set(str('Number Of Moon Orbits (Earth) = '+str(round(day/27.3217,6))))
    if day==Time_Span.get()+Leap_Years.get():
        stop()
        top_entries[2]['state']="normal"
        pause_btn['state']="disabled"
        stop_btn['state']="disabled"
        start_btn['state']="normal"
        Anim_Active.set(False) # Time Frame Complete
    return G2V.orbit(frame)
def anim_start(frames, speed):# Start Animation
    top_entries[2]['state']="normal"
    pause_btn['state']="normal"
    stop_btn['state']="normal"
    start_btn['state']="disabled"
    stat=grid_status.get() # Update Grid
    if stat=='off':
        ax.axis(False)
        ax.grid(False)
        grid_status.set('off')
        Grid_Text.set('Turn Grid ON') 
    else:
        ax.axis(True)
        ax.grid(True)
        grid_status.set('on')
        Grid_Text.set('Turn Grid OFF') 
    if Slider_Value.get()=='0': return
    colors=['#999999', '#cd9f6d', '#3292ea', '#cc0000']
    names=['Mercury', 'Venus', 'Earth', 'Mars']
    labels_y=[-0.28, 0.75, -0.95, 1.48]
    for p in range(0,4): # Update Planet Names
        plt.text(0, - (labels_y[p]), names[p], color=colors[p], zorder=1000, ha='center', fontsize='10')
    global Anim
    Anim_Active.set(True)
    Anim=animation.FuncAnimation(fig=Anim_Fig, func=anim_advance,  repeat=False, frames=frames, blit=True, interval=speed, cache_frame_data='False')
def set_anim_time(): # Use Porportions For Slider Position vs Time
    a1,a2,b1,b2,c1,c2=20,1,1,20,1,50
    a_range,b_range,c_range=abs(a1-a2),abs(b1-b2),abs(c1-c2)
    k_factor1=abs(b_range/a_range) 
    val=float(Slider_Value.get())
    if val==0: # If Slider Value = 0, Stop Animation
        try:
            Anim.event_source.stop()
        except Exception:
            pass
        return
    dt=abs(b1-((val-a1)*k_factor1)) # Get porportion Of Time
    k_factor2=abs(c_range/a_range) 
    multiplier=abs(c1-((val-a1)*k_factor2)) # Get Multiplier Ratio
    dt*=multiplier
    return dt
def move_slider(event):
    try:
        Anim.event_source.stop()
    except Exception:
        pass
def release_slider(event):
    speed=set_anim_time()
    if speed==None: return
    Anim_Speed.set(speed)
    if Anim_Active.get()==True:start()
def set_defaults():
    Slider_Value.set(20)
    speed=set_anim_time()
    Anim_Speed.set(speed)
    Anim_Active.set(False)
    Anim_Paused.set(False)
    Start_Date.set('2020-01-01T00:00:00')
    Old_StartDate.set("")
    Duration.set(1.0) # Earth Duration Years
    Old_Duration.set(0.0)# Comparison For Change
    Increment.set(24.0) # Hours (Earth Rotational Resolution)
    Old_Increment.set(0.0)
    inc=Increment.get()
    moon_orbits.set('')
    step=inc/24
    Increment_Step.set(step) # Time Increments
    dur=Duration.get()
    span=(dur*365.256)/step
    Time_Span.set(span)
    ax.axis(True)
    grid_status.set('on')
    top_entries[2]['state']="normal"
    pause_btn['state']="disabled"
    stop_btn['state']="disabled"
    start_btn['state']="normal"
def start():# Start Animation
    top_entries[2]['state']="normal"
    start_btn['state']="disabled"
    stop_btn['state']="normal"
    pause_btn['state']="normal"
    if Anim_Paused.get()==True:
        Anim_Paused.set(False)
        Anim.resume()
        return
    if float(Slider_Value.get())==0.0:
        msg1='Speed Slider Must Be Set To Number > 0 For Animation.\n'
        msg2='Please Change The Slider Position.'
        messagebox.showwarning('Time Acceleration', msg1+msg2)            
        time_scale.focus
        return
    dur=Duration.get()
    _dur=Old_Duration.get()
    date=Start_Date.get()
    _date=Old_StartDate.get()
    inc=Increment.get()
    _inc=Old_Increment.get()
    Anim_Paused.set(False)
    Anim_Active.set(False)
    Present_Time.set("")
    header.set("")
    moon_orbits.set("")
    earth_days_past.set('')
    earth_sun.set('')
    mercury_days_past.set('')
    mercury_distance.set('')
    mercury_time.set("")
    mercury_close.set('')        
    mercury_sun.set('')
    mars_days_past.set('')
    mars_time.set("")
    mars_close.set('')        
    mars_sun.set('')
    mars_distance.set('')
    moon_distance.set('')
    moon_time.set("")
    moon_close.set('')
    venus_days_past.set('')
    venus_distance.set('')
    venus_close.set('')
    venus_time.set("")        
    venus_sun.set('')
    sun_close.set('')
    sun_time.set("")
    Old_Moon.set(1.0e24)
    Old_Mercury.set(1.0e24)
    Old_Venus.set(1.0e24)
    Old_Mars.set(1.0e24)
    Old_Sun.set(1.0e24)
    if dur!=_dur or date!=_date or inc!=_inc:# Something Changed
        Old_Duration.set(dur)
        Old_StartDate.set(date)
        Old_Increment.set(inc)
        t=set_anim_time()
        Anim_Speed.set(t)
        End_Time.set("")
        if dur<= 0.0: # Duration Years
            msg1='Time Duration Must Be Set To Number > 0 For Animation.\n'
            msg2='Please Enter A Time Duration.'
            messagebox.showwarning('Time Duration', msg1+msg2)
            top_entries[1].focus
            return
        if date=='': # Start Date
            msg1='A Start Date Must Be Entered For Animation.\n'
            msg2='Example: 2022-01-15'
            messagebox.showwarning('Start Date', msg1+msg2)            
            top_entries[0].focus
            return
        if inc<= 0.0: # Increment Hrs 
            msg1='Time Increment Must Be Set To Number > 0 For Animation.\n'
            msg2='Please Enter A Time Increment.'
            messagebox.showwarning('Time Increment', msg1+msg2)
            top_entries[1].focus
            return
        Old_Duration.set(dur)
        Old_StartDate.set(date)
        Old_Increment.set(inc)
        step=inc/24
        Increment_Step.set(step)
        Astropy_Moon()
        step=inc/24
        Increment_Step.set(step) # Time Increments
        span=int(round((dur*365.256)/step))
        Time_Span.set(span)
        Horizon_Planets()
        try:
            Anim.resume()
            Anim.event_source.stop()
        except Exception:
            pass
        G2V.Time=Time(Start_Date.get()).jd
        speed=Anim_Speed.get()
        total_frames=int(len(Epoch))
        end_time=str(Time(Epoch[-1])+step*u.day)
        end_time=end_time.replace('T','  Hrs: ')[:-4] # Trim mSec From End And Add Hrs Label
        End_Time.set('   Finish Date: '+end_time)
        anim_start(total_frames, speed)
    else:# Nothing Changed
        speed=Anim_Speed.get()
        total_frames=int(len(Epoch))
        anim_start(total_frames, speed)
def on_resize(event):
    if root.state()=="normal":
        root.font["size"]=10
        present_font["size"]=12
    elif root.state()=="zoomed":    
        root.font["size"]=12
        present_font["size"]=14
def grid(event):
    stat=grid_status.get()
    plt.ion()
    try:
        if Anim_Paused.get()==True:return
        Anim.event_source.stop()
    except Exception:
        pass
    if stat=='off':
        ax.axis(True)
        ax.grid(True)
        grid_status.set('on')
        Grid_Text.set('Turn Grid OFF') 
    else:
        ax.axis(False)
        ax.grid(False)
        grid_status.set('off')
        Grid_Text.set('Turn Grid ON') 
    plt.ioff()
    if Anim_Active.get()==True:start()
def pause(event):
    try:
        Anim.pause()
        Anim_Paused.set(True)
    except Exception:
        pass
    top_entries[2]['state']="normal"
    start_btn['state']="normal"
    stop_btn['state']="disabled"
    pause_btn['state']="disabled"
def stop(event=None):
    try:
        Anim.event_source.stop()
        Anim_Paused.set(False)# Restart Animation
        Anim_Active.set(False)
    except Exception:
        pass
    top_entries[2]['state']="normal"
    start_btn['state']="normal"
    pause_btn['state']="disabled"
    stop_btn['state']="disabled"
def callback(event): # Entry Widgets
    start_btn['state']="disabled"
    pause_btn['state']="disabled"
    stop_btn['state']="disabled"
    Anim_Active.set(False)
    Anim_Paused.set(False)
    start()
def unit_change(event): # AU, Metric, U.S.
    selected=event.widget.get()
    Units.set(selected)
def destroy():# X Icon Or Exit Program Clicked
    try:
        Anim.event_source.stop()
    except Exception:
        pass
    Lunar.clear()
    Real_Lunar.clear()
    for widget in root.winfo_children():# Destroys Menu Bars, Frame, Canvas And Scroll Bars
        if isinstance(widget, tk.Canvas):widget.destroy()
        else:widget.destroy()
    os._exit(0)
def menu_popup(event):# display the popup menu
    if Anim_Active.get()==False:
        try:popup.tk_popup(event.x_root, event.y_root)
        finally:popup.grab_release()
def validate_dates(string): # Entry Date Widget
    regex=re.compile(r'[(0-9-)]*$') # Date Widget, Allow Integers and -
    result=regex.match(string)
    return (string == "" 
    or (string.count(string)>0# Prevent duplicates
        and result is not None
        and result.group(0) != ""))       
def on_validate_dates(P):return validate_dates(P)
def validate_double(dbl_value): # Duration, Increment Widgets
    str_value=str(dbl_value)
    regex=re.compile(r'[(0-9.)]*$') # Allowed Integers Only
    result=regex.match(str_value)
    return (str_value == "" 
    or (str_value.count(str_value)>0 # Prevent duplicates
        and result is not None
        and result.group(0) != ""))       
def on_validate_double(P):return validate_double(P)
class Bodies: # Define Sun And Planets
    def __init__(self,name,rad,color,atmos,xyz,v_xyz):
        if name ==301:self.name=5 # Change 301 To 5 For Iteration
        else:self.name=name   
        self.radian=rad*1
        self.color=color
        self.atmosphere=atmos
        self.xyz=np.array(xyz, dtype=float)
        self.v_xyz=np.array(v_xyz, dtype=float)
        if name=='Sun':
            G2V.create_sun(self.radian)
        else:self.plot=plt.scatter(0, 0, s=self.radian, color=self.color,  antialiased=True, edgecolors=self.atmosphere, zorder=10)
class G2V_Solar_System:
    def __init__(self):
        self.planets=[]
        self.Planets_Data=[]
        self.Plots=[]
        self.Zero_Frame=0
    def add_planet(self, planet):
        self.planets.append(planet)
    def planet_properties(self,radius,color,atmos):
        self.radius=radius
        self.color=color
        self.atmosphere=atmos
        radius=[303.19, 752.08, 791.75, 421.33, 107.955]# Body Diameter = (Miles / 10) Except Mooon = Miles / 20
        color=['#999999', '#cd9f6d', '#3292ea', '#cc0000', '#f3f6f4']
        atmosphere=['#d2d2d2','#999999','#00ffff', '#daa520', '#000000']       
        for i, p in enumerate(radius):
            self.radius.append(p)
            self.color.append(color[i])
            self.atmosphere.append(atmosphere[i])
    def create_sun(self,radius):
        filename='sun.jpg'
        path=os.path.join(dir, filename)
        image=plt.imread(path)
        sun=plt.imshow(image, extent=(-0.2,0.2,-0.2,0.2)) 
        plot=plt.Circle((0, 0), radius=radius, antialiased=True, transform=ax.transData)
        sun.set_clip_path(plot)
    def finalize_planet_data(self): # Finalize All Planet Data, Place In Dict 
        dt=Increment_Step.get()
        mercury,venus,earth,mars,moon={},{},{},{},{}
        temp,temp2=[],[]
        for p in self.planets:
            for e in range(0,len(Epoch)):
                if p.name!=5: # Moon Data Already Present
                    p.xyz+=p.v_xyz*dt
                    acc=-2.959e-4*p.xyz/np.sum(p.xyz**2)**(3./2)
                    p.v_xyz+=acc*dt
                    temp=p.xyz.tolist()
                    if p.name==1:mercury[e]=[element for element in temp]
                    elif p.name==2:venus[e]=[element for element in temp]
                    elif p.name==3: # Create And Combine Earth Data To Moon Data
                        earth[e]=[element for element in temp]
                        combined=zip(earth[e],Lunar[e]) # Earth + Moon
                        temp2=[x+y for (x,y) in combined]
                        moon[e]=[element for element in temp2]
                    elif p.name==4:mars[e]=[element for element in temp]
                    temp=[]
                    temp2=[]
        self.Planets_Data=[mercury,venus,earth,mars,moon]
    def orbit(self,frame):
        try:
            if frame==0:# 0 Frame Is Sent 3 Times By Anim Function
                if self.Zero_Frame==0:self.Zero_Frame+=1
                Increment_Step.set(1)
            self.Plots=[]
            for i, p in enumerate(self.planets):
                p.xyz=self.Planets_Data[i][frame]    
                p.plot.set_offsets(p.xyz[:2])
                self.Plots.append(p.plot)
            time_now=str(Time(Epoch[frame])+Increment_Step.get()*u.day)
            time_now=time_now.replace('T','  Hrs: ')[:-4] # Trim mSec From End And Add Hrs Label
            Present_Time.set('Present Date: '+time_now)
            if p.name==5: # Update All Display Widgets
                d1=str(round(np.sqrt((Real_Lunar[frame][0])**2+(Real_Lunar[frame][1])**2+(Real_Lunar[frame][2])**2),18))
                new_moon=float(d1)
                d2=str(round(np.sqrt((self.Planets_Data[2][frame][0])**2+(self.Planets_Data[2][frame][1])**2+
                    (self.Planets_Data[2][frame][2])**2),18))
                new_sun=float(d2)
                d3=str(round(np.sqrt((self.Planets_Data[0][frame][0]-self.Planets_Data[2][frame][0])**2+
                    (self.Planets_Data[0][frame][1]-self.Planets_Data[2][frame][1])**2+(self.Planets_Data[0][frame][2]-
                        self.Planets_Data[2][frame][2])**2),18))
                new_mercury=float(d3)
                d4=str(round(np.sqrt((self.Planets_Data[0][frame][0])**2+(self.Planets_Data[0][frame][1])**2+
                    (self.Planets_Data[0][frame][2])**2),18))
                d5=str(round(np.sqrt((self.Planets_Data[1][frame][0]-self.Planets_Data[2][frame][0])**2+
                    (self.Planets_Data[1][frame][1]-self.Planets_Data[2][frame][1])**2+(self.Planets_Data[1][frame][2]-
                        self.Planets_Data[2][frame][2])**2),18))
                new_venus=float(d5)
                d6=str(round(np.sqrt((self.Planets_Data[1][frame][0])**2+(self.Planets_Data[1][frame][1])**2+
                    (self.Planets_Data[1][frame][2])**2),18))
                d7=str(round(np.sqrt((self.Planets_Data[3][frame][0]-self.Planets_Data[2][frame][0])**2+
                    (self.Planets_Data[3][frame][1]-self.Planets_Data[2][frame][1])**2+(self.Planets_Data[3][frame][2]-
                        self.Planets_Data[2][frame][2])**2),18))
                new_mars=float(d7)
                d8=str(round(np.sqrt((self.Planets_Data[3][frame][0])**2+(self.Planets_Data[3][frame][1])**2+
                    (self.Planets_Data[3][frame][2])**2),18))
                meas=Units.get()
                if meas=='AU': # Leave As Is
                    unit=' au'
                elif meas=='U.S.': # Convert AU To Miles
                    d1=str(round(float(d1)*92955807.26743,18))
                    new_moon=float(d1)
                    d2=str(round(float(d2)*92955807.26743,18))
                    new_sun=float(d2)
                    d3=str(round(float(d3)*92955807.26743,18)) 
                    new_mercury=float(d3)
                    d4=str(round(float(d4)*92955807.26743,18)) 
                    d5=str(round(float(d5)*92955807.26743,18))
                    new_venus=float(d5)
                    d6=str(round(float(d6)*92955807.26743,18))
                    d7=str(round(float(d7)*92955807.26743,18)) 
                    new_mars=float(d7)
                    d8=str(round(float(d8)*92955807.26743,18)) 
                    unit=' mi'
                elif meas=='Metric': # Convert AU To Kilometers
                    d1=str(round(float(d1)*149597870.691,18)) 
                    new_moon=float(d1)
                    d2=str(round(float(d2)*149597870.691,18))
                    new_sun=float(d2)
                    d3=str(round(float(d3)*149597870.691,18))
                    new_mercury=float(d3)
                    d4=str(round(float(d4)*149597870.691,18)) 
                    d5=str(round(float(d5)*149597870.691,18)) 
                    new_venus=float(d5)
                    d6=str(round(float(d6)*149597870.691,18))
                    d7=str(round(float(d7)*149597870.691,18)) 
                    new_mars=float(d7)
                    d8=str(round(float(d8)*149597870.691,18)) 
                    unit=' km'
                header.set('{Nearest Distances To Earth, Date / UTC Time}')
                moon_distance.set('Distance'+chr(8853)+' To Moon: '+d1+unit)
                earth_sun.set('Distance'+chr(8853)+' To Sun: '+d2+unit)
                mercury_distance.set('Distance'+chr(8853)+' To Earth: '+d3+unit)
                mercury_sun.set('Distance'+chr(8853)+' To Sun: '+d4+unit)
                venus_distance.set('Distance'+chr(8853)+' To Earth: '+d5+unit)
                venus_sun.set('Distance'+chr(8853)+' To Sun: '+d6+unit)
                mars_distance.set('Distance'+chr(8853)+' To Earth: '+d7+unit)
                mars_sun.set('Distance'+chr(8853)+' To Sun: '+d8+unit)
                # Distances And Closest Distances To Earth
                tol=str(round(Increment_Step.get()*24,3))+' hrs'
                if new_sun<Old_Sun.get():
                    Old_Sun.set(new_sun)
                    sun_close.set('Sun = '+str(d2)+unit)
                    sun_time.set('Date: '+time_now+' '+chr(177)+' '+tol)
                if new_moon<Old_Moon.get():
                    Old_Moon.set(new_moon)
                    moon_close.set('Moon = '+str(d1)+unit)
                    moon_time.set('Date: '+time_now+' '+chr(177)+' '+tol)
                if new_mercury<Old_Mercury.get():
                    Old_Mercury.set(new_mercury)
                    mercury_close.set('Mercury = '+str(d3)+unit)
                    mercury_time.set('Date: '+time_now+' '+chr(177)+' '+tol)
                if new_venus<Old_Venus.get():
                    Old_Venus.set(new_venus)
                    venus_close.set('Venus = '+str(d5)+unit)
                    venus_time.set('Date: '+time_now+' '+chr(177)+' '+tol)
                if new_mars<Old_Mars.get():
                    Old_Mars.set(new_mars)
                    mars_close.set('Mars = '+str(d7)+unit)
                    mars_time.set('Date: '+time_now+' '+chr(177)+' '+tol)
        except Exception:
            pass
        return self.Plots
class Horizon_Planets():
    def __init__(self):
        global G2V
        G2V=G2V_Solar_System()
        G2V.Time = Time(Start_Date.get()).jd
        radius,color,atmosphere=[],[],[]
        G2V.planet_properties(radius,color,atmosphere)
        solar_system_ephemeris.set('builtin')
        for p, planets in enumerate([1, 2, 3, 4, 301]): # 1st, 2nd, 3rd, 4th planet in solar system
            obj=Horizons(id=planets,location='@sun',epochs=G2V.Time,id_type=None).vectors()
            G2V.add_planet(Bodies(planets,radius[p],color[p],atmosphere[p], 
                [np.double(obj[xyz]) for xyz in ['x', 'y', 'z']], 
                [np.double(obj[v_xyz]) for v_xyz in ['vx', 'vy', 'vz']]))
        Bodies("Sun",0.2,'#ffe200',"#c90076",0.0,0.0)
        G2V.finalize_planet_data()        
class Astropy_Moon():
    def __init__(self):
        top_entries[2]['state']="disabled"
        exit_btn['state']="disabled"
        start_btn['state']="disabled"
        pause_btn['state']="disabled"
        stop_btn['state']="disabled"
        start=Start_Date.get()
        if start=='':return
        dur=Duration.get()
        if Duration.get()<=0: return
        step=Increment_Step.get()
        if Increment_Step.get()<=0:return
        incre=Increment.get()
        if Increment.get()<=0:return
        try:
            leap_years=[str(y)for y in range(1820,2248,4)]# Leap Years Within +- 200 Year Span From 2024
            span=int(round((dur*365.256)/step))
            Time_Span.set(span)
            Increment_Step.set(incre/24)
            global Epoch
            Epoch=Time(start) + np.arange(span)*u.hour*Increment.get()
            count=0
            done_year="0"
            for y in range(len(Epoch)):
                year=str(Epoch[y])[0:4]
                if year!=done_year:
                    if year in leap_years:
                        count+=1
                        done_year=year
            Leap_Years.set(count)    
            if Leap_Years.get()!=0:Epoch=Time(start) + np.arange(span+Leap_Years.get())*u.hour*Increment.get()
        except Exception:
            msg1='Something is not correct with Entered Text.\n'
            msg2='Please check the values and try again.'
            messagebox.showwarning('Start Date', msg1+msg2)
            return
        pb=Progressbar(root, orient='horizontal', length=100, mode='determinate')
        pb.place(relx=0.2833333, rely=0.0777777, relwidth=0.4555555, relheight=0.0244444)
        txt1=tk.Label(root, text='0%', bg='#000000', fg ='#ffffff', font=root.font)
        txt1.place(relx=0.7388888, rely=0.0777777, relwidth=0.0666666, relheight=0.0244444)
        txt2=tk.Label(root, text='Please Wait! Retrieving Planetary Data For New Time Duration.', bg='#000000', fg ='#ffffff', font=root.font)
        txt2.place(relx=0.2833333, rely=0.09555555, relwidth=0.4555555, relheight=0.0244444)
        solar_system_ephemeris.set('builtin')
        for e in range(0,len(Epoch)):  
            moon=get_body("moon",Epoch[e])
            Real_Lunar[e]=[np.double(moon.cartesian.xyz[0]), np.double(moon.cartesian.xyz[1]), np.double(moon.cartesian.xyz[2])]
            Lunar[e]=[element * 70 for element in Real_Lunar[e]] # Exaggerate Moons Orbit To Accomidate Size Of Earth
            root.update_idletasks()
            pb['value']+=100/span
            txt1['text']=round(pb['value'],1),'%'
        pb.destroy()
        txt1.destroy()
        txt2.destroy()
        start_btn['state']="active"
        top_entries[2]['state']="normal"
        stop_btn['state']="normal"
        exit_btn['state']="normal"
if __name__ == "__main__":
    root=tk.Tk()
    style=ttk.Style()
    style.theme_use('classic')
    style.map('TCombobox', background=[('readonly','#000000')])# Down Arrow
    style.map('TCombobox', fieldbackground=[('readonly','#000000')])
    style.map('TCombobox', selectbackground=[('readonly','#000000')])
    style.map('TCombobox', selectforeground=[('readonly', '#a7f8f8')])
    root.title('Our Inner Solar System 2D')
    pgm_Path=Path(__file__).parent.absolute()
    dir=Path(__file__).parent.absolute()
    filename='2DSpace.ico'
    path=os.path.join(dir, filename)
    root.iconbitmap(path) # Program icon
    root.font=font.Font(family='lucidas', size=10, weight='normal', slant='italic')
    present_font=font.Font(family='lucidas', size=12, weight='normal', slant='italic')
    monitor_info=GetMonitorInfo(MonitorFromPoint((0,0)))
    work_area=monitor_info.get("Work")
    monitor_area=monitor_info.get("Monitor")
    taskbar_height = monitor_area[3] - work_area[3]
    screen_width=work_area[2]
    screen_height=work_area[3]
    taskbar_hgt=(monitor_area[3]-work_area[3])
    root_hgt=(screen_height-taskbar_height)*0.8
    root_wid=screen_width*0.8 
    x=(screen_width/2)-(root_wid/2)
    y=(screen_height/2)-(root_hgt/2)
    root.geometry('%dx%d+%d+%d' % (root_wid, root_hgt, x, y, ))
    root.configure(bg='#000000')
    root.bind("<Configure>", on_resize)
    root.option_add('*TCombobox*Listbox.font', root.font)
    root.protocol("WM_DELETE_WINDOW", destroy)
    popup=Menu(root, tearoff=0) # PopUp Menu
    popup.add_command(label="About", background='aqua', command=lambda:about())
    root.bind("<Button-3>", menu_popup)
    px=1/plt.rcParams['figure.dpi']
    dpi=root.winfo_fpixels('1i')
    Anim_Fig=plt.figure(figsize=(root_hgt*px,root_wid*px),facecolor='#000000',dpi=dpi)
    #Anim_Fig=plt.figure(figsize=(10, 10),facecolor='#000000')
    ax=plt.axes(xlim=(-1.6,1.6), ylim=(-1.6,1.9))
    ax.set_facecolor('#000000')
    Anim_Fig.canvas.draw()
    plt.cla()
    dir=Path(__file__).parent.absolute()
    filename='space.PNG'
    path=os.path.join(dir, filename)
    space=plt.imread(path)
    ax.imshow(space, extent=[-1.8, 1.7, -1.6, 1.6])
    ax.set_xlim([-1.8,1.7])
    ax.set_ylim([-1.6,1.9])
    ax.tick_params(axis='x', colors='#ffffff') # Grid And Label The Axis Ticks
    ax.tick_params(axis='y', colors='#ffffff')
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(which='major', color='#7e7e7e', linestyle='dotted') # Turn Both Major and Minor Ticks On
    ax.grid(which='minor', color='#7e7e7e', linestyle='dotted')
    ax.set_xlabel('Astronomical Units', ha='center', color='#ffffff', # Label Axis
        fontsize=10, weight='normal', style='italic')
    ax.set_ylabel('Astronomical Units', ha='center', color='#ffffff',
        fontsize=10, weight='normal', style='italic')
    Anim_Fig.add_axes(ax)        
    canvas=FigureCanvasTkAgg(Anim_Fig, root)
    canvas.get_tk_widget().place(x=0, y=0, width=root_wid, height=root_hgt)  
    canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.X)
    canvas=Toplevel
    plt.tight_layout()
    Real_Lunar={}
    Lunar={}
    Anim_Active=BooleanVar()
    Anim_Speed=IntVar()
    Anim_Paused=BooleanVar()
    Old_Sun=DoubleVar()
    Old_Moon=DoubleVar()
    Old_Mercury=DoubleVar()
    Old_Venus=DoubleVar()
    Old_Mars=DoubleVar()
    Present_Time=StringVar() # Present Date Label
    End_Time=StringVar()
    earth_days_past=StringVar()
    moon_distance=StringVar()
    moon_orbits=StringVar()
    earth_sun=StringVar()
    mercury_days_past=StringVar()
    mercury_distance=StringVar()
    mercury_sun=StringVar()
    venus_days_past=StringVar()
    venus_distance=StringVar()
    venus_sun=StringVar()
    mars_days_past=StringVar()
    mars_distance=StringVar()
    mars_sun=StringVar()
    header=StringVar()
    sun_close=StringVar()
    sun_time=StringVar()
    moon_close=StringVar()
    moon_time=StringVar()
    mercury_close=StringVar()
    mercury_time=StringVar()
    venus_close=StringVar()
    venus_time=StringVar()
    mars_close=StringVar()
    mars_time=StringVar()
    Start_Date=StringVar()
    Old_StartDate=StringVar()
    Time_Span=DoubleVar()
    Duration=DoubleVar()
    Old_Duration=DoubleVar()
    Increment=DoubleVar()
    Old_Increment=DoubleVar()
    Increment_Step=DoubleVar()
    grid_status=StringVar()
    Grid_Text=StringVar()
    Slider_Value=StringVar()
    Leap_Years=IntVar()
    time_scale=tk.Scale( root, variable=Slider_Value, from_=0,to=20, orient='vertical', resolution=1, tickinterval=1, 
        bg='#000000', fg='#ffffff', troughcolor='#73B5FA', activebackground='#1065BF')
    time_scale.place(relx=0.78, rely=0.14, relwidth=0.034, relheight=0.4)
    time_scale.bind("<ButtonPress-1>", move_slider)
    time_scale.bind("<ButtonRelease-1>", release_slider)
    # tk Slider Label
    speed_lbl=tk.Label(root, bg='#000000', fg='#ffffff', font=root.font, 
        text='Speed', justify='left', anchor='c')
    speed_lbl.place(relx=0.775, rely=0.105, relwidth=0.035, relheight=0.0344)
    top_lbls=[]
    x_rel=[0.095,0.215,0.325,0.44]
    wid=[0.11,0.1,0.105,0.05]
    txt=['Start Date / UTC Time','Earth Duration (Yrs.)','Time Increment (Hrs.)','Units']
    for index, element in enumerate(x_rel): # Labels For Top Row Entries
        top_lbls.append([index])
        top_lbls[index]=tk.Label(root, bg='#000000', fg='#ffffff', font=root.font, 
            text=txt[index], justify='left', anchor='c')
        top_lbls[index].place(relx=element, rely=0.005, relwidth=wid[index], relheight=0.0344)
    top_entries=[]
    validates=[validate_dates,validate_double,validate_double]
    cmds=[on_validate_dates,on_validate_double,on_validate_double]
    txt_var=[Start_Date,Duration,Increment]
    for index, element in enumerate(txt_var): # Top Row Entries
        top_entries.append([index])
        top_entries[index]=tk.Entry(root, bg='#000000', fg='#a7f8f8', textvariable=element, font=root.font, 
                justify='center',insertbackground='#ffffff')
        top_entries[index].place(relx=x_rel[index], rely=0.0366666, relwidth=wid[index], relheight=0.0344)
        top_entries[index]['validatecommand']=(top_entries[index].register(validates[index]),'%P','%d')
        cmd=(top_entries[index].register(cmds[index]), '%P')
        top_entries[index].config(validate="key", validatecommand=cmd)
        top_entries[index].config(cursor="xterm #ffffff")
        #top_entries[index].bind("<Button-1>", pause)
        top_entries[index].bind('<Return>', callback)
    start_btn=tk.Button(root, text='Start', background="#000000", foreground='#ffffff', font=root.font, command=lambda:start())
    start_btn.place(relx=0.50, rely=0.0366666, relwidth=0.05, relheight=0.0344)
    pause_btn=tk.Button(root, text='Pause', background="#000000", foreground='#ffffff', font=root.font)
    pause_btn.place(relx=0.56, rely=0.0366666, relwidth=0.05, relheight=0.0344)
    pause_btn.bind("<Button-1>", pause)
    stop_btn=tk.Button(root, text='Stop', background="#000000", foreground='#ffffff', font=root.font)
    stop_btn.place(relx=0.62, rely=0.0366666, relwidth=0.05, relheight=0.0344)
    stop_btn.bind("<Button-1>", stop)
    Units=tk.StringVar()
    units_cb=ttk.Combobox(root, textvariable=Units, background="#000000", foreground='#a7f8f8', font=root.font, justify='center')
    units_cb.place(relx=0.44, rely=0.0366666, relwidth=0.05, relheight=0.0344) # using place method
    units_cb['values']=('AU','U.S.','Metric')
    units_cb['state']='readonly'
    units_cb.current(0)
    #units_cb.bind("<Button-1>", pause)
    units_cb.bind('<<ComboboxSelected>>', unit_change)
    Grid_Text.set('Turn Grid OFF') 
    grid_btn=tk.Button(root, textvariable=Grid_Text, background="#000000", foreground='#ffffff', font=root.font,)
    grid_btn.place(relx=0.68, rely=0.0366666, relwidth=0.08, relheight=0.0344)
    grid_btn.bind("<Button-1>", grid)
    exit_btn=tk.Button(root, text='Exit Program', background="#000000", foreground = '#ffffff', font=root.font, command=lambda: destroy())
    exit_btn.place(relx=0.77, rely=0.0366666, relwidth=0.08, relheight=0.0344)
    present_lbl=tk.Label(root, bg='#000000', fg='#a7f8f8', font=present_font, 
        text='', textvariable=Present_Time, justify='left', anchor='w')
    present_lbl.place(relx=0.015, rely=0.15, relwidth=0.21, relheight=0.03)
    end_lbl=tk.Label(root, bg='#000000', fg='#a7f8f8', font=present_font, 
        text='', textvariable=End_Time, justify='left', anchor='w')
    end_lbl.place(relx=0.01, rely=0.18, relwidth=0.21, relheight=0.03)
    strvar=[earth_days_past,moon_distance,moon_orbits,earth_sun,mercury_days_past,mercury_distance,
        mercury_sun,venus_days_past,venus_distance,venus_sun,mars_days_past,mars_distance,mars_sun]
    color=['#3292ea','#3292ea','#3292ea','#3292ea','#d2d2d2','#d2d2d2','#d2d2d2','#cd9f6d','#cd9f6d',
        '#cd9f6d','#cc0000','#cc0000','#cc0000']
    do_lbl=[] # Days Past Data / Orbits Data
    y=0.23 
    for index, element in enumerate(strvar):
        do_lbl.append([index])
        do_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text='', textvariable=element, justify='left', anchor='w')
        do_lbl[index].place(relx=0.02, rely=y, relwidth=0.21, relheight=0.03)
        y+=0.025
    y+=0.025
    nd_lbl=[] # Nearest Distance / Date/Time Data
    strvar=[header,sun_close,sun_time,moon_close,moon_time,mercury_close,mercury_time,venus_close,venus_time,mars_close,mars_time]
    color=['#a7f8f8','#ff7469','#ff7469','#ffffff','#ffffff','#999999','#999999','#cd9f6d',
        '#cd9f6d','#cc0000','#cc0000']
    for index, element in enumerate(strvar):
        nd_lbl.append([index])
        nd_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        textvariable=element, justify='left', anchor='w')
        nd_lbl[index].place(relx=0.02, rely=y, relwidth=0.21, relheight=0.03)
        y+=0.025
    y=0.11
    bd_lbl=[] # Body Diameters
    text=['{Body Diameters}','Sun = 1,391,983 km, 864,938 mi','Earth = 12,741.98 km, 7,917.5 mi',
        'Moon = 3,474.735 km, 2,159.1 mi','Mercury = 4,879.37 km, 3,031.9 mi',
        'Venus = 12,103.554 km, 7,520.8 mi','Mars = 6,779.04 km, 4,213.3 mi']
    color=['#a7f8f8','#ff7469','#3292ea','#f3f6f4','#999999','#cd9f6d','#cc0000']
    for index, element in enumerate(text):
        bd_lbl.append([index])
        bd_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        bd_lbl[index].place(relx=0.82, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    bm_lbl=[] # Body Mass
    text=['{Body Masses}','Sun = 1.98847 x 10'+ chr(179) + chr(8304) + ' kg','Earth = 5.97219 x 10'+ chr(178) + chr(8308) + ' kg',
        'Moon = 7.34767 x 10'+ chr(178) + chr(178) + ' kg','Mercury = 3.30104 x 10'+ chr(178) + chr(179) + ' kg',
        'Venus = 4.86732 x 10'+ chr(178) + chr(8308) + ' kg','Mars = 6.4169 x 10'+ chr(178) + chr(179) + ' kg']
    for index, element in enumerate(text):
        bm_lbl.append([index])
        bm_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        bm_lbl[index].place(relx=0.82, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    rp_lbl=[] # Rotation Periods
    color=['#a7f8f8','#3292ea','#f3f6f4','#999999','#cd9f6d','#cc0000']
    text=['{Rotational Periods}','Earth = 23.9345 hrs.','Moon = 655.7 hrs.',
        'Mercury = 1407.6 hrs.','Venus = -5832.5 hrs.','Mars = 24.6229 hrs.']
    for index, element in enumerate(text):
        rp_lbl.append([index])
        rp_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        rp_lbl[index].place(relx=0.82, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    op_lbl=[] # Orbital Periods
    text=['{Orbital Periods}','Earth = 365.256 days','Moon (Earth) = 27.3217 days',
        'Mercury = 87.969 days','Venus = 224.701 days','Mars = 686.980 days']
    for index, element in enumerate(text):
        op_lbl.append([index])
        op_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        op_lbl[index].place(relx=0.82, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    ov_lbl=[] # Orbital Velocities
    text=['{Orbital Velocities}','Earth = 29.8 km/sec, 18.5 mi/sec','Moon = 1.022 km/sec, 0.6350 mi/sec ',
        'Mercury = 47.4 km/sec, 29.4 mi/sec','Venus = 35.0 km/sec, 21.8 mi/sec','Mars = 21.4 km/sec, 15.0 mi/sec']
    for index, element in enumerate(text):
        ov_lbl.append([index])
        ov_lbl[index]=tk.Label(root, bg='#000000', fg=color[index], font=root.font, 
        text=element, justify='left', anchor='w')
        ov_lbl[index].place(relx=0.82, rely=y, relwidth=0.235, relheight=0.03)
        y+=0.025
    strvar.clear()
    color.clear()
    text.clear()    
    popup=Menu(root, tearoff=0) # PopUp Menu
    popup.add_command(label="About", background='aqua', command=lambda:about())
    set_defaults()
root.mainloop()